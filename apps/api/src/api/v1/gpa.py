"""
GPA REST Endpoints
Provides credit-weighted SGPA, CGPA calculations, and target future grade solvers.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.src.core.database import get_db
from apps.api.src.models.academic import Semester, Subject, GradeRecord
from apps.api.src.schemas.gpa_schemas import (
    CourseGradeInput,
    SGPACalculationRequest,
    SGPASummary,
    SemesterProgress,
    CGPACalculationRequest,
    CGPASummary,
    TargetCGPARequest,
    TargetCGPAResponse,
)
from apps.api.src.services.gpa_service import GPAService

router = APIRouter(prefix="/gpa", tags=["GPA"])


@router.get("/summary")
async def get_gpa_summary(
    user_id: int = Query(default=1, description="Student user ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes current semester SGPA and cumulative CGPA from stored academic records.
    """
    # Fetch all semesters for this student
    query = (
        select(Semester)
        .where(Semester.user_id == user_id)
        .options(
            selectinload(Semester.subjects).selectinload(Subject.grade_record)
        )
        .order_by(Semester.semester_number.asc())
    )
    result = await db.execute(query)
    semesters = result.scalars().all()

    completed_semesters_progress: List[SemesterProgress] = []
    current_sem_summary: Optional[SGPASummary] = None

    for sem in semesters:
        courses_in_sem: List[CourseGradeInput] = []
        for subj in sem.subjects:
            gr = subj.grade_record
            if gr and gr.grade_point is not None:
                courses_in_sem.append(
                    CourseGradeInput(
                        course_code=subj.code,
                        course_name=subj.name,
                        credits=subj.credits,
                        grade_point=gr.grade_point,
                        grade_letter=gr.grade_letter,
                    )
                )

        if courses_in_sem:
            sgpa_res = GPAService.calculate_sgpa(SGPACalculationRequest(courses=courses_in_sem))
            if sem.is_active:
                current_sem_summary = sgpa_res
            else:
                completed_semesters_progress.append(
                    SemesterProgress(
                        semester_number=sem.semester_number,
                        credits=sgpa_res.total_credits,
                        sgpa=sgpa_res.sgpa,
                    )
                )

    # Compute overall CGPA
    cgpa_summary: Optional[CGPASummary] = None
    all_completed = completed_semesters_progress.copy()
    if current_sem_summary and current_sem_summary.total_credits > 0:
        all_completed.append(
            SemesterProgress(
                semester_number=5,
                credits=current_sem_summary.total_credits,
                sgpa=current_sem_summary.sgpa,
            )
        )

    if all_completed:
        cgpa_summary = GPAService.calculate_cgpa(CGPACalculationRequest(semesters=all_completed))

    return {
        "current_semester_sgpa": current_sem_summary,
        "cumulative_cgpa": cgpa_summary,
        "semesters_evaluated": len(all_completed),
    }


@router.post("/target", response_model=TargetCGPAResponse)
async def solve_target_cgpa(request: TargetCGPARequest):
    """
    Deterministic Target CGPA Solver:
    'What average SGPA do I need in future semesters to graduate with G CGPA?'
    """
    return GPAService.solve_target_cgpa(request)
