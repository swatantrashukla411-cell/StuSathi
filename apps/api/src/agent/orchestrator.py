"""
Agent Orchestrator Layer
Bridges Gemini 1.5 Flash LLM with the deterministic academic tool registry.
Maintains multi-turn context, parses intents, executes backend tools,
and generates conversational Hinglish/English responses.
"""

import time
import re
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.src.core.config import settings
from apps.api.src.agent.prompts import CAMPUSPILOT_SYSTEM_PROMPT
from apps.api.src.agent.tools import (
    execute_get_today_schedule,
    execute_get_next_class,
    execute_get_subject_attendance,
    execute_simulate_absence,
    execute_calculate_recovery,
    execute_get_gpa_summary,
    execute_calculate_target_sgpa,
)


class AgentOrchestrator:
    @classmethod
    async def process_user_query(
        cls,
        message: str,
        user_id: int,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Processes a conversational voice/text query from the student.
        Orchestrates tool execution and returns a natural language response.
        """
        start_time = time.time()
        msg_lower = message.strip().lower()

        tool_invoked: Optional[str] = None
        tool_result: Optional[Dict[str, Any]] = None
        reply: str = ""

        # Check if Gemini API key is configured
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GEMINI_API_KEY)

                # Tool declarations for Gemini
                tools = [
                    execute_get_today_schedule,
                    execute_get_next_class,
                    execute_get_subject_attendance,
                    execute_simulate_absence,
                    execute_calculate_recovery,
                    execute_get_gpa_summary,
                    execute_calculate_target_sgpa,
                ]

                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=CAMPUSPILOT_SYSTEM_PROMPT,
                    tools=tools,
                )

                chat = model.start_chat(enable_automatic_function_calling=True)
                response = chat.send_message(message)
                reply = response.text

                # Check if a function was called in the interaction
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            tool_invoked = part.function_call.name

                elapsed = round((time.time() - start_time) * 1000, 2)
                return {
                    "reply": reply,
                    "tool_invoked": tool_invoked,
                    "tool_result": tool_result,
                    "latency_ms": elapsed,
                    "provider": "gemini-1.5-flash",
                }
            except Exception as e:
                # Log error and fallback to deterministic intent router
                pass

        # Smart Deterministic Fallback & Evaluation Router
        # Enables 100% offline development, CI/CD testing, and evaluation
        reply, tool_invoked, tool_result = await cls._route_deterministic_intent(
            msg_lower=msg_lower, user_id=user_id, db=db
        )

        elapsed = round((time.time() - start_time) * 1000, 2)
        return {
            "reply": reply,
            "tool_invoked": tool_invoked,
            "tool_result": tool_result,
            "latency_ms": elapsed,
            "provider": "deterministic-engine",
        }

    @classmethod
    async def _route_deterministic_intent(
        cls, msg_lower: str, user_id: int, db: AsyncSession
    ):
        """
        Parses student intent using deterministic rules and executes the verified tool.
        """
        # Intent 1: Next Class
        if any(k in msg_lower for k in ["next class", "agli class", "room number", "kahan hai", "next lecture"]):
            res = await execute_get_next_class(db, user_id)
            if res.get("has_upcoming"):
                mins = res.get("minutes_remaining")
                if mins is not None:
                    reply = (
                        f"Aapki next class {res['subject_name']} ({res['subject_code']}) hai, "
                        f"jo {res['room']} mein {mins} minute mein shuru hogi."
                    )
                else:
                    reply = res.get("message", "Aapka schedule updated hai.")
            else:
                reply = "Aaj aapki koi aur classes nahi hain! Enjoy your break."
            return reply, "get_next_class", res

        # Helper to dynamically identify subject from student message or active curriculum
        async def _find_query_subject(msg: str) -> str:
            known_tokens = [
                "daa", "algorithm", "algo", "scala", "cloud", "machine learning", "ml",
                "technical skills", "skills", "event", "internship", "dbms", "database",
                "os", "operating systems", "cn", "networks", "toc", "theory", "maths"
            ]
            for token in known_tokens:
                if token in msg:
                    return token

            # Search active semester subjects
            from apps.api.src.models.academic import Subject, Semester
            from sqlalchemy import select
            sub_res = await db.execute(
                select(Subject)
                .join(Semester, Subject.semester_id == Semester.id)
                .where(Semester.user_id == user_id, Semester.is_active.is_(True))
            )
            subs = sub_res.scalars().all()
            for s in subs:
                if s.code.lower() in msg or any(w in msg for w in s.name.lower().split() if len(w) > 3):
                    return s.code

            return subs[0].code if subs else "CS35303"

        # Intent 2: Absence Simulation (Miss / Bunk / Chutti)
        if any(k in msg_lower for k in ["miss", "bunk", "chutti", "na jaun", "skip"]):
            # Extract number of classes
            num_match = re.search(r"(\d+)\s*(class|lecture|din)", msg_lower)
            sessions_to_miss = int(num_match.group(1)) if num_match else 1

            subject_query = await _find_query_subject(msg_lower)

            res = await execute_simulate_absence(
                db, user_id, subject_name_or_code=subject_query, sessions_to_miss=sessions_to_miss
            )

            if "error" in res:
                return res["error"], "simulate_absence", res

            cur_pct = res["current_percentage"]
            proj_pct = res["projected_percentage"]
            safe_rem = res["safe_absences_remaining_after"]
            is_safe = res["is_safe"]

            if is_safe:
                reply = (
                    f"Agar aap {res['subject_name']} ki {sessions_to_miss} class miss karte hain, "
                    f"toh aapki attendance {cur_pct}% se girkar {proj_pct}% ho jayegi. "
                    f"Aap abhi bhi safe zone mein hain aur semester mein {safe_rem} classes aur miss kar sakte hain."
                )
            else:
                reply = (
                    f"Warning: {sessions_to_miss} class miss karne par aapki {res['subject_name']} attendance "
                    f"{proj_pct}% par aa jayegi, jo 75% rule se niche hai! Is class ko miss mat kijiye."
                )
            return reply, "simulate_absence", res

        # Intent 3: Attendance Recovery (Recover / 75%)
        if any(k in msg_lower for k in ["recover", "75%", "danger zone", "kitni attend karni", "maintain"]):
            subject_query = await _find_query_subject(msg_lower)

            res = await execute_calculate_recovery(db, user_id, subject_name_or_code=subject_query)
            if "error" in res:
                return res["error"], "calculate_recovery", res

            needed = res["classes_needed_consecutively"]
            is_rec = res["is_recoverable"]

            if is_rec:
                reply = (
                    f"{res['subject_name']} mein 75% attendance par wapas aane ke liye "
                    f"aapko agli {needed} classes lagataar attend karni padengi."
                )
            else:
                reply = (
                    f"{res['subject_name']} attendance mathematically recover nahi ho sakti. "
                    f"Maximum attend karne par bhi attendance {res['max_possible_percentage']}% hi banegi."
                )
            return reply, "calculate_recovery", res

        # Intent 4: Subject Attendance Check
        if any(k in msg_lower for k in ["attendance", "kitni attendance", "percentage"]):
            subject_query = await _find_query_subject(msg_lower)

            res = await execute_get_subject_attendance(db, user_id, subject_name_or_code=subject_query)
            if "error" in res:
                return res["error"], "get_subject_attendance", res

            reply = (
                f"Aapki {res['subject_name']} attendance abhi {res['current_percentage']}% hai "
                f"({int(res['classes_attended'])}/{int(res['classes_conducted'])} classes attended). "
                f"Aap safe zone mein hain aur aage {res['safe_future_absences']} classes bina tension miss kar sakte hain."
            )
            return reply, "get_subject_attendance", res

        # Intent 5: Today's Schedule
        if (
            any(k in msg_lower for k in ["schedule", "classes today", "kitni class", "kitne lecture", "aaj ki class"])
            or ("aaj" in msg_lower and any(w in msg_lower for w in ["class", "lecture"]))
        ):
            res = await execute_get_today_schedule(db, user_id)
            total = res.get("total_classes", 0)
            day = res.get("day_name", "Today")
            reply = (
                f"Aaj {day} ko aapki total {total} classes scheduled hain. "
                f"Aap dashboard par timeline view dekh sakte hain."
            )
            return reply, "get_today_schedule", res

        # Intent 6: CGPA / SGPA
        if any(k in msg_lower for k in ["cgpa", "sgpa", "gpa", "grade"]):
            num_match = re.search(r"(\d+(\.\d+)?)", msg_lower)
            if num_match and float(num_match.group(1)) > 5.0:
                target = float(num_match.group(1))
                res = await execute_calculate_target_sgpa(db, user_id, target_cgpa=target)
                if res["is_achievable"]:
                    reply = (
                        f"{target} CGPA achieve karne ke liye aapko bache hue credits mein "
                        f"average {res['required_future_sgpa']} SGPA maintain karna hoga."
                    )
                else:
                    reply = (
                        f"{target} CGPA mathematically possible nahi hai. Aapka maximum attainable CGPA "
                        f"{res['max_possible_cgpa']} hai."
                    )
                return reply, "calculate_target_sgpa", res
            else:
                res = await execute_get_gpa_summary(db, user_id)
                reply = f"Aapka current CGPA {res['current_cgpa']} hai across {int(res['completed_credits'])} credits."
                return reply, "get_gpa_summary", res

        # Default conversational greeting
        return (
            "Hey! Main aapka CampusPilot personal assistant hoon. "
            "Aap mujhse puchh sakte hain: 'Meri next class kaunsi hai?', "
            "'Aaj DBMS miss karun toh attendance kitni hogi?', ya '75% ke liye kitni classes chahiye?'",
            None,
            None,
        )
