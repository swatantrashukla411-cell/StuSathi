"""
QUMS (Quantum University Management System) Integration Service
Connects to https://qums.quantumuniversity.edu.in to:
1. Fetch live Captcha image and session cookies.
2. Perform in-memory ephemeral authentication (Zero Password Storage in DB!).
3. Scrape and parse dashboard attendance tables.
4. Synchronize records into CampusPilot database models.
"""

import base64
import json
import re
import time
import uuid
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from apps.api.src.models.academic import User, Semester, Subject, AttendanceRecord
from apps.api.src.services.attendance_service import AttendanceService

QUMS_BASE_URL = "https://qums.quantumuniversity.edu.in"

# In-memory session store mapping session_token -> session state
# Stores active httpx client cookies and form token.
# Automatically cleared after 5 minutes (TTL).
_SESSIONS: Dict[str, Dict[str, Any]] = {}


class QUMSService:
    @staticmethod
    def _clean_expired_sessions():
        """Removes sessions older than 5 minutes."""
        now = time.time()
        expired = [k for k, v in _SESSIONS.items() if now - v["created_at"] > 300]
        for k in expired:
            _SESSIONS.pop(k, None)

    @classmethod
    async def get_captcha_session(cls) -> Dict[str, str]:
        """
        Initializes a fresh connection with QUMS:
        1. Calls GET / to obtain session cookies and __RequestVerificationToken.
        2. Calls POST /Account/showrefreshcaptchaImage to obtain raw captcha PNG bytes.
        3. Encodes captcha PNG into Base64 data URL for frontend display.
        """
        cls._clean_expired_sessions()
        session_token = str(uuid.uuid4())

        client = httpx.AsyncClient(
            base_url=QUMS_BASE_URL,
            verify=False,
            timeout=15.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        try:
            # Step 1: Initial landing page GET
            r_home = await client.get("/")
            html = r_home.text

            token_match = re.search(
                r'name=[\"\']__RequestVerificationToken[\"\'][^>]*value=[\"\']([^\"\']+)[\"\']',
                html,
            )
            form_token = token_match.group(1) if token_match else ""

            # Step 2: Request live captcha image
            r_captcha = await client.post(
                "/Account/showrefreshcaptchaImage",
                headers={"X-Requested-With": "XMLHttpRequest"},
            )

            # QUMS returns a JSON array of byte integers [137, 80, 78, 71, ...]
            byte_list = json.loads(r_captcha.text)
            png_bytes = bytes(byte_list)
            b64_image = base64.b64encode(png_bytes).decode("utf-8")
            image_data_url = f"data:image/png;base64,{b64_image}"

            # Save session state
            _SESSIONS[session_token] = {
                "client": client,
                "form_token": form_token,
                "created_at": time.time(),
            }

            return {
                "session_token": session_token,
                "captcha_image": image_data_url,
                "form_token": form_token,
            }
        except Exception as e:
            await client.aclose()
            raise RuntimeError(f"Could not connect to QUMS portal: {str(e)}")

    @classmethod
    async def sync_student_data(
        cls,
        session_token: str,
        qid: str,
        password: str,
        captcha: str,
        user_id: int,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Logs into QUMS using the active session, extracts the dashboard attendance table,
        and synchronizes subjects and attendance records into the database.
        Password is kept purely in-memory and immediately destroyed after request.
        """
        session_data = _SESSIONS.get(session_token)
        if not session_data:
            raise ValueError("Session expired or invalid. Please refresh captcha.")

        client: httpx.AsyncClient = session_data["client"]
        form_token: str = session_data["form_token"]

        try:
            # Step 1: Submit login form
            login_payload = {
                "__RequestVerificationToken": form_token,
                "UserName": qid.strip(),
                "Password": password,
                "captcha": captcha.strip(),
                "hdnMsg": "QGC",
                "checkOnline": "0",
                "clientIP": "",
                "DeviceLocalIp": "",
                "DeviceMachineName": "",
                "DeviceMachineGuid": "",
                "DeviceMacAddress": "",
                "DeviceAgentInstalled": "",
            }

            r_login = await client.post("/", data=login_payload, follow_redirects=True)
            response_text = r_login.text

            # Check for standard QUMS login errors
            if "Captcha does not match" in response_text:
                raise ValueError("Captcha does not match. Please try again.")

            if "User name or Password is not valid" in response_text or "Invalid credentials" in response_text:
                raise ValueError("Invalid QID or Password. Please check your credentials.")

            # If still on login page without explicit message
            if 'id="UserName"' in response_text and 'id="Password"' in response_text:
                soup_err = BeautifulSoup(response_text, "html.parser")
                err_div = soup_err.find("div", class_="validation-summary-errors")
                err_msg = err_div.get_text(strip=True) if err_div else "Login failed. Please verify your QID and password."
                raise ValueError(err_msg)

            # Step 2: Extract Attendance Table from Dashboard / Student Portal
            parsed_subjects = cls._parse_attendance_from_html(response_text)

            # If not found directly on landing dashboard, check common attendance sub-routes
            if not parsed_subjects:
                for sub_route in ["/Student/Attendance", "/Attendance/StudentAttendance", "/Student/Home"]:
                    try:
                        r_sub = await client.get(sub_route)
                        parsed_subjects = cls._parse_attendance_from_html(r_sub.text)
                        if parsed_subjects:
                            break
                    except Exception:
                        continue

            if not parsed_subjects:
                raise ValueError(
                    "Login was successful, but no attendance table could be located on your QUMS dashboard. "
                    "Please check if your semester attendance is currently published on QUMS."
                )

            # Step 3: Synchronize parsed subjects into CampusPilot Database
            synced_count = await cls._save_to_database(db=db, user_id=user_id, subjects_data=parsed_subjects)

            return {
                "success": True,
                "message": f"Successfully synced {synced_count} subjects from QUMS!",
                "synced_subjects": parsed_subjects,
            }

        finally:
            # Memory safety: Clean up and close client
            await client.aclose()
            _SESSIONS.pop(session_token, None)

    @classmethod
    def _parse_attendance_from_html(cls, html: str) -> List[Dict[str, Any]]:
        """
        Parses tables in HTML looking for subject names, conducted classes,
        attended classes, and attendance percentages based on header mapping.
        """
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")
        parsed_subjects: List[Dict[str, Any]] = []

        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue

            # Identify column indexes from header row
            header_row = rows[0]
            header_cols = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]

            subj_idx = -1
            conducted_idx = -1
            attended_idx = -1

            for idx, h in enumerate(header_cols):
                if any(k in h for k in ["subject", "course", "paper"]):
                    subj_idx = idx
                elif any(k in h for k in ["conducted", "total", "held", "delivered"]):
                    conducted_idx = idx
                elif any(k in h for k in ["attended", "present"]):
                    attended_idx = idx

            # If headers were successfully identified
            if subj_idx != -1 and conducted_idx != -1 and attended_idx != -1:
                for row in rows[1:]:
                    cols = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cols) > max(subj_idx, conducted_idx, attended_idx):
                        raw_title = cols[subj_idx]
                        raw_conducted = cols[conducted_idx].replace("%", "").strip()
                        raw_attended = cols[attended_idx].replace("%", "").strip()

                        try:
                            conducted = float(raw_conducted)
                            attended = float(raw_attended)
                        except ValueError:
                            continue

                        # Extract code and name
                        code_match = re.search(r"([A-Z]{2,4}\d{3,4})", raw_title)
                        code = code_match.group(1) if code_match else f"SUB_{len(parsed_subjects)+1}"
                        name = raw_title.replace(code, "").strip(" -:")
                        if not name:
                            name = raw_title

                        pct = round((attended / conducted * 100), 2) if conducted > 0 else 100.0

                        parsed_subjects.append({
                            "subject_code": code,
                            "subject_name": name,
                            "classes_conducted": conducted,
                            "classes_attended": attended,
                            "percentage": pct,
                        })

                if parsed_subjects:
                    break

        return parsed_subjects

    @classmethod
    async def _save_to_database(
        cls,
        db: AsyncSession,
        user_id: int,
        subjects_data: List[Dict[str, Any]],
    ) -> int:
        """
        Saves or updates subjects and attendance records for the user.
        """
        # Get active semester or create one
        sem_res = await db.execute(
            select(Semester).where(Semester.user_id == user_id, Semester.is_active.is_(True))
        )
        active_sem = sem_res.scalar_one_or_none()
        if not active_sem:
            active_sem = Semester(
                user_id=user_id,
                semester_number=5,
                name="Synced from QUMS",
                start_date=date(2026, 8, 1),
                end_date=date(2026, 12, 15),
                is_active=True,
            )
            db.add(active_sem)
            await db.flush()

        synced_count = 0
        start_cal = date(2026, 8, 15)

        for s in subjects_data:
            # Check if subject already exists
            query = select(Subject).where(
                Subject.semester_id == active_sem.id,
                Subject.code == s["subject_code"],
            )
            res = await db.execute(query)
            subj = res.scalar_one_or_none()

            if not subj:
                subj = Subject(
                    semester_id=active_sem.id,
                    code=s["subject_code"],
                    name=s["subject_name"],
                    credits=4.0,
                    attendance_threshold=75.0,
                    total_planned_sessions=max(40, int(s["classes_conducted"] + 10)),
                )
                db.add(subj)
                await db.flush()

            # Refresh attendance records matching conducted/attended counts
            conducted = int(s["classes_conducted"])
            attended = int(s["classes_attended"])

            # Remove old records for this subject and re-populate
            del_query = select(AttendanceRecord).where(AttendanceRecord.subject_id == subj.id)
            old_recs = (await db.execute(del_query)).scalars().all()
            for r in old_recs:
                await db.delete(r)

            for i in range(conducted):
                status = "attended" if i < attended else "missed"
                db.add(
                    AttendanceRecord(
                        subject_id=subj.id,
                        class_date=start_cal + timedelta(days=i * 2),
                        status=status,
                        session_weight=1.0,
                    )
                )

            synced_count += 1

        await db.commit()
        return synced_count
