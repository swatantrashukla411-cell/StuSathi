"""
GPA Domain Schemas
Pydantic v2 models for SGPA, CGPA calculations, grade points, and target CGPA solvers.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator


# Standard UGC / AICTE 10-point grading system default
DEFAULT_GRADE_SCALE: Dict[str, float] = {
    "O": 10.0,
    "A+": 9.0,
    "A": 8.0,
    "B+": 7.0,
    "B": 6.0,
    "C": 5.0,
    "P": 4.0,
    "F": 0.0,
    "Ab": 0.0,
}


class CourseGradeInput(BaseModel):
    course_code: str = Field(..., description="Course code, e.g. CS501")
    course_name: str = Field(..., description="Course name, e.g. Operating Systems")
    credits: float = Field(..., gt=0, description="Course credits, e.g. 4.0, 3.0, 1.5")
    grade_point: Optional[float] = Field(None, ge=0.0, le=10.0, description="Grade point (0.0 to 10.0)")
    grade_letter: Optional[str] = Field(None, description="Letter grade, e.g. 'A+', 'O', 'B'")

    @field_validator("grade_point")
    @classmethod
    def validate_grade_input(cls, v: Optional[float], info) -> Optional[float]:
        # If grade_point is provided, it's valid
        return v


class SGPACalculationRequest(BaseModel):
    courses: List[CourseGradeInput] = Field(..., min_length=1, description="List of courses in the semester")
    custom_grade_scale: Optional[Dict[str, float]] = Field(
        default=None, 
        description="Optional university custom grade scale mapping letter to points"
    )


class SGPASummary(BaseModel):
    semester_number: Optional[int] = None
    total_credits: float = Field(..., gt=0)
    total_grade_points: float = Field(..., ge=0)
    sgpa: float = Field(..., ge=0.0, le=10.0)
    course_count: int
    breakdown: List[Dict[str, float | str]]


class SemesterProgress(BaseModel):
    semester_number: int = Field(..., ge=1, le=12)
    credits: float = Field(..., gt=0)
    sgpa: float = Field(..., ge=0.0, le=10.0)


class CGPACalculationRequest(BaseModel):
    semesters: List[SemesterProgress] = Field(..., min_length=1, description="Completed semesters history")


class CGPASummary(BaseModel):
    total_completed_credits: float = Field(..., gt=0)
    cumulative_grade_points: float = Field(..., ge=0)
    cgpa: float = Field(..., ge=0.0, le=10.0)
    semesters_count: int


class TargetCGPARequest(BaseModel):
    current_cgpa: float = Field(..., ge=0.0, le=10.0, description="Current CGPA (C)")
    completed_credits: float = Field(..., ge=0.0, description="Credits earned so far (Ec)")
    remaining_credits: float = Field(..., gt=0.0, description="Credits yet to be completed (Er)")
    target_cgpa: float = Field(..., ge=0.0, le=10.0, description="Goal CGPA (G)")
    max_scale: float = Field(default=10.0, ge=4.0, le=10.0, description="Max grade scale (default 10.0)")


class TargetCGPAResponse(BaseModel):
    current_cgpa: float
    target_cgpa: float
    completed_credits: float
    remaining_credits: float
    required_future_sgpa: float
    is_achievable: bool
    max_possible_cgpa: float
    explanation: str
