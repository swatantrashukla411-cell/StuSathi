"""
Attendance REST Endpoints
Provides real-time attendance calculations, what-if absence simulations,
and recovery plans backed by relational history and deterministic math.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.src.core.database import get_db
from apps.api.src.models.academic import Semester, Subject, AttendanceRecord
from apps.api.src.schemas.attendance_schemas import (
    SubjectAttendanceSummary,
    SimulateAbsenceRequest,
    SimulateAbsenceResponse,
    AttendanceRecoveryRequest,
    AttendanceRecoveryResponse,
)
from apps.api.src.schemas.api_schemas import (
    RecordAttendanceInput,
    RecordAttendanceResponse,
)
from apps.api.src.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/summary", response_model=List[SubjectAttendanceSummary])
async def get_attendance_summary(
    user_id: int = Query(default=1, description="Student user ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes real-time attendance summary for all subjects in the active semester.
    Runs deterministic safe-absence formulas on real database attendance logs.
    """
    # Fetch active semester and its subjects with their attendance records
    query = (
        select(Subject)
        .join(Semester, Subject.semester_id == Semester.id)
        .where(
            Semester.user_id == user_id,
            Semester.is_active.is_(True),
        )
        .options(selectinload(Subject.attendance_records))
        .order_by(Subject.code.asc())
    )
    result = await db.execute(query)
    subjects = result.scalars().all()

    summaries: List[SubjectAttendanceSummary] = []
    for subj in subjects:
        records = subj.attendance_records
        attended_units = 0.0
        conducted_units = 0.0

        for r in records:
            if r.status in ("attended", "missed", "duty_leave"):
                conducted_units += r.session_weight
            if r.status in ("attended", "duty_leave"):
                attended_units += r.session_weight

        conducted_units = round(conducted_units, 2)
        attended_units = round(attended_units, 2)

        # Remaining planned classes
        remaining = max(0, int(subj.total_planned_sessions - conducted_units))

        summary = AttendanceService.get_subject_summary(
            subject_code=subj.code,
            subject_name=subj.name,
            classes_attended=attended_units,
            classes_conducted=conducted_units,
            remaining_planned_sessions=remaining,
            required_threshold=subj.attendance_threshold,
        )
        summaries.append(summary)

    return summaries


@router.post("/record", response_model=RecordAttendanceResponse)
async def log_attendance(
    input_data: RecordAttendanceInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Logs an attendance record for a subject and returns the updated percentage.
    """
    subj = await db.get(Subject, input_data.subject_id)
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")

    new_record = AttendanceRecord(
        subject_id=input_data.subject_id,
        class_date=input_data.class_date,
        status=input_data.status.lower(),
        session_weight=input_data.session_weight,
        note=input_data.note,
    )
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    # Recalculate new percentage
    query = select(AttendanceRecord).where(AttendanceRecord.subject_id == input_data.subject_id)
    res = await db.execute(query)
    all_recs = res.scalars().all()

    attended = sum(r.session_weight for r in all_recs if r.status in ("attended", "duty_leave"))
    conducted = sum(r.session_weight for r in all_recs if r.status in ("attended", "missed", "duty_leave"))
    new_pct = AttendanceService.calculate_current_percentage(attended, conducted)

    return RecordAttendanceResponse(
        success=True,
        message=f"Attendance recorded as '{input_data.status}'.",
        record_id=new_record.id,
        subject_name=subj.name,
        new_attendance_pct=new_pct,
    )


@router.post("/simulate", response_model=SimulateAbsenceResponse)
async def simulate_absence(request: SimulateAbsenceRequest):
    """
    Deterministic what-if simulation:
    'If I miss y upcoming classes, what will my semester-end attendance be?'
    """
    return AttendanceService.simulate_absence(request)


@router.post("/recover", response_model=AttendanceRecoveryResponse)
async def calculate_recovery(request: AttendanceRecoveryRequest):
    """
    Deterministic recovery solver:
    'How many consecutive classes must I attend to recover to target %?'
    """
    return AttendanceService.calculate_recovery_plan(request)
