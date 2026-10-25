"""
Attendance Domain Schemas
Pydantic v2 models for attendance calculations, simulations, and recovery plans.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AttendanceStatus(str, Enum):
    ATTENDED = "attended"
    MISSED = "missed"
    CANCELLED = "cancelled"
    DUTY_LEAVE = "duty_leave"  # Medical / college official duty (counted as attended/excused)


class RiskCategory(str, Enum):
    SAFE = "safe"              # >= 80% (Comfortable buffer)
    CAUTION = "caution"        # 75% to 79.9% (In danger if 1-2 classes missed)
    CRITICAL = "critical"      # < 75% (Currently barred from exams unless recovered)
    UNRECOVERABLE = "unrecoverable"  # Even attending 100% of remaining classes cannot reach 75%


class SubjectAttendanceSummary(BaseModel):
    subject_code: str = Field(..., description="Course code, e.g. CS501")
    subject_name: str = Field(..., description="Course name, e.g. Database Management Systems")
    classes_conducted: float = Field(..., ge=0, description="Total classes/sessions conducted so far (T)")
    classes_attended: float = Field(..., ge=0, description="Total classes/sessions attended so far (A)")
    classes_missed: float = Field(..., ge=0, description="Total classes missed")
    current_percentage: float = Field(..., ge=0.0, le=100.0, description="Current percentage (A/T * 100)")
    required_threshold: float = Field(default=75.0, ge=0.0, le=100.0, description="Mandatory minimum percentage (p)")
    remaining_planned_sessions: int = Field(default=0, ge=0, description="Estimated sessions left in semester (R)")
    safe_future_absences: int = Field(..., ge=0, description="Max remaining classes student can miss safely")
    risk_category: RiskCategory
    explanation: str = Field(..., description="Natural language breakdown of the status")


class SimulateAbsenceRequest(BaseModel):
    classes_conducted: float = Field(..., ge=0, description="Classes conducted so far (T)")
    classes_attended: float = Field(..., ge=0, description="Classes attended so far (A)")
    remaining_planned_sessions: int = Field(..., ge=0, description="Total remaining sessions (R)")
    sessions_to_miss: int = Field(default=1, ge=1, description="Number of upcoming sessions considered to miss (y)")
    required_threshold: float = Field(default=75.0, ge=0.0, le=100.0, description="Required percentage threshold")

    @field_validator("classes_attended")
    @classmethod
    def validate_attended_le_conducted(cls, v: float, info) -> float:
        conducted = info.data.get("classes_conducted")
        if conducted is not None and v > conducted:
            raise ValueError("classes_attended cannot exceed classes_conducted")
        return v

    @field_validator("sessions_to_miss")
    @classmethod
    def validate_miss_le_remaining(cls, v: int, info) -> int:
        remaining = info.data.get("remaining_planned_sessions")
        if remaining is not None and v > remaining:
            raise ValueError(f"Cannot simulate missing {v} sessions when only {remaining} remain in semester")
        return v


class SimulateAbsenceResponse(BaseModel):
    current_percentage: float
    projected_percentage: float
    threshold_percentage: float
    sessions_missed_in_sim: int
    safe_absences_remaining_after: int
    risk_category_after: RiskCategory
    is_safe: bool
    explanation: str


class AttendanceRecoveryRequest(BaseModel):
    classes_conducted: float = Field(..., ge=0, description="Classes conducted so far (T)")
    classes_attended: float = Field(..., ge=0, description="Classes attended so far (A)")
    remaining_planned_sessions: int = Field(..., ge=0, description="Total remaining sessions (R)")
    target_threshold: float = Field(default=75.0, ge=0.0, le=100.0, description="Target recovery percentage")

    @field_validator("classes_attended")
    @classmethod
    def validate_attended_le_conducted(cls, v: float, info) -> float:
        conducted = info.data.get("classes_conducted")
        if conducted is not None and v > conducted:
            raise ValueError("classes_attended cannot exceed classes_conducted")
        return v


class AttendanceRecoveryResponse(BaseModel):
    current_percentage: float
    target_threshold: float
    classes_needed_consecutively: int
    remaining_sessions_available: int
    is_recoverable: bool
    max_possible_percentage: float
    explanation: str
