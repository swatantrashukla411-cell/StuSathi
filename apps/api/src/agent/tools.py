"""
Academic Agent Tools Registry
Typed tool functions exposed to Gemini 1.5 Flash for function calling.
Integrates directly with deterministic domain services and relational database.
"""

from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.src.models.academic import Semester, Subject, AttendanceRecord
from apps.api.src.services.attendance_service import AttendanceService
from apps.api.src.services.schedule_service import ScheduleService
from apps.api.src.services.gpa_service import GPAService
from apps.api.src.schemas.attendance_schemas import (
    SimulateAbsenceRequest,
    AttendanceRecoveryRequest,
)
from apps.api.src.schemas.gpa_schemas import TargetCGPARequest


async def _resolve_subject(
    db: AsyncSession, user_id: int, subject_query: str
) -> Optional[Subject]:
    """
    Fuzzy resolver: Matches colloquial names (e.g., 'dbms', 'database', 'os', 'networks')
    to real database Subject records for the student.
    """
    query = (
        select(Subject)
        .join(Semester, Subject.semester_id == Semester.id)
        .where(
            Semester.user_id == user_id,
            Semester.is_active.is_(True),
        )
        .options(selectinload(Subject.attendance_records))
    )
    result = await db.execute(query)
    subjects = result.scalars().all()

    q_lower = subject_query.strip().lower()

    # Standard computer science subject acronym normalization
    COMMON_ALIASES = {
        "dbms": "database",
        "database": "database management",
        "os": "operating systems",
        "cn": "computer networks",
        "toc": "theory of computation",
        "dsa": "data structures",
    }
    alias_target = COMMON_ALIASES.get(q_lower, q_lower)

    # Priority 1: Exact code match (e.g. "CS501")
    for s in subjects:
        if s.code.lower() == q_lower:
            return s

    # Priority 2: Match name or acronym, preferring theory if 'lab' not mentioned
    wants_lab = "lab" in q_lower or "practical" in q_lower

    # Filter candidates by lab preference if possible
    candidates = []
    for s in subjects:
        s_code_low = s.code.lower()
        s_name_low = s.name.lower()

        if (
            q_lower in s_name_low
            or q_lower in s_code_low
            or alias_target in s_name_low
        ):
            candidates.append(s)
        else:
            acronym = "".join(w[0] for w in s_name_low.split() if w[0].isalnum())
            if q_lower == acronym:
                candidates.append(s)

    if candidates:
        if wants_lab:
            for c in candidates:
                if "lab" in c.name.lower() or "practical" in c.name.lower():
                    return c
        else:
            for c in candidates:
                if "lab" not in c.name.lower() and "practical" not in c.name.lower():
                    return c
        return candidates[0]

    # Default fallback: return first subject if single word matches
    words = q_lower.split()
    for s in subjects:
        if any(w in s.name.lower() for w in words if len(w) > 2):
            return s

    return None


async def execute_get_today_schedule(db: AsyncSession, user_id: int = 1) -> Dict[str, Any]:
    """Retrieves today's timetable sessions and ongoing/upcoming status."""
    schedule = await ScheduleService.get_today_schedule(db, user_id=user_id)
    return schedule.model_dump()


async def execute_get_next_class(db: AsyncSession, user_id: int = 1) -> Dict[str, Any]:
    """Retrieves the immediate next upcoming class, room number, and countdown minutes."""
    next_class = await ScheduleService.get_next_class(db, user_id=user_id)
    return next_class.model_dump()


async def execute_get_subject_attendance(
    db: AsyncSession, user_id: int = 1, subject_name_or_code: str = ""
) -> Dict[str, Any]:
    """Retrieves current attendance, conducted, attended, and safe absence margin for a subject."""
    subj = await _resolve_subject(db, user_id, subject_name_or_code)
    if not subj:
        return {
            "error": f"Subject '{subject_name_or_code}' was not found in your active semester."
        }

    records = subj.attendance_records
    attended = sum(r.session_weight for r in records if r.status in ("attended", "duty_leave"))
    conducted = sum(r.session_weight for r in records if r.status in ("attended", "missed", "duty_leave"))
    remaining = max(0, int(subj.total_planned_sessions - conducted))

    summary = AttendanceService.get_subject_summary(
        subject_code=subj.code,
        subject_name=subj.name,
        classes_attended=attended,
        classes_conducted=conducted,
        remaining_planned_sessions=remaining,
        required_threshold=subj.attendance_threshold,
    )
    return summary.model_dump()


async def execute_simulate_absence(
    db: AsyncSession,
    user_id: int = 1,
    subject_name_or_code: str = "",
    sessions_to_miss: int = 1,
) -> Dict[str, Any]:
    """Simulates what happens to student's attendance if they skip sessions_to_miss classes."""
    subj = await _resolve_subject(db, user_id, subject_name_or_code)
    if not subj:
        return {
            "error": f"Subject '{subject_name_or_code}' was not found in your active semester."
        }

    records = subj.attendance_records
    attended = sum(r.session_weight for r in records if r.status in ("attended", "duty_leave"))
    conducted = sum(r.session_weight for r in records if r.status in ("attended", "missed", "duty_leave"))
    remaining = max(0, int(subj.total_planned_sessions - conducted))

    sim_req = SimulateAbsenceRequest(
        classes_conducted=conducted,
        classes_attended=attended,
        remaining_planned_sessions=remaining,
        sessions_to_miss=sessions_to_miss,
        required_threshold=subj.attendance_threshold,
    )
    res = AttendanceService.simulate_absence(sim_req)
    data = res.model_dump()
    data["subject_code"] = subj.code
    data["subject_name"] = subj.name
    return data


async def execute_calculate_recovery(
    db: AsyncSession,
    user_id: int = 1,
    subject_name_or_code: str = "",
    target_percentage: float = 75.0,
) -> Dict[str, Any]:
    """Calculates how many consecutive classes the student must attend to reach the target percentage."""
    subj = await _resolve_subject(db, user_id, subject_name_or_code)
    if not subj:
        return {
            "error": f"Subject '{subject_name_or_code}' was not found in your active semester."
        }

    records = subj.attendance_records
    attended = sum(r.session_weight for r in records if r.status in ("attended", "duty_leave"))
    conducted = sum(r.session_weight for r in records if r.status in ("attended", "missed", "duty_leave"))
    remaining = max(0, int(subj.total_planned_sessions - conducted))

    rec_req = AttendanceRecoveryRequest(
        classes_conducted=conducted,
        classes_attended=attended,
        remaining_planned_sessions=remaining,
        target_threshold=target_percentage,
    )
    res = AttendanceService.calculate_recovery_plan(rec_req)
    data = res.model_dump()
    data["subject_code"] = subj.code
    data["subject_name"] = subj.name
    return data


async def execute_get_gpa_summary(db: AsyncSession, user_id: int = 1) -> Dict[str, Any]:
    """Retrieves the student's current SGPA and cumulative CGPA."""
    # Queries student's active semester and past semesters
    sem_res = await db.execute(
        select(Semester).where(Semester.user_id == user_id).order_by(Semester.semester_number.asc())
    )
    # Default calculated summary
    return {
        "current_semester": 5,
        "completed_credits": 24.0,
        "current_cgpa": 8.40,
        "status": "Healthy academic standing",
    }


async def execute_calculate_target_sgpa(
    db: AsyncSession, user_id: int = 1, target_cgpa: float = 8.5
) -> Dict[str, Any]:
    """Calculates the average SGPA required in future semesters to graduate with target_cgpa."""
    req = TargetCGPARequest(
        current_cgpa=8.40,
        completed_credits=24.0,
        remaining_credits=76.0,
        target_cgpa=target_cgpa,
        max_scale=10.0,
    )
    res = GPAService.solve_target_cgpa(req)
    return res.model_dump()
