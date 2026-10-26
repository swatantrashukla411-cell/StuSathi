"""
API Request and Response Schemas
Pydantic v2 schemas for Timetable, Attendance, and Dashboard endpoints.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class TodaySessionOut(BaseModel):
    session_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    start_time: str
    end_time: str
    session_type: str
    room: str
    building: str
    instructor: Optional[str] = None
    status: str = Field(..., description="'completed', 'ongoing', or 'upcoming'")


class TodayScheduleResponse(BaseModel):
    date: str
    day_name: str
    day_of_week: int
    total_classes: int
    sessions: List[TodaySessionOut]


class NextClassResponse(BaseModel):
    has_upcoming: bool
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    start_time: Optional[str] = None
    room: Optional[str] = None
    building: Optional[str] = None
    instructor: Optional[str] = None
    minutes_remaining: Optional[int] = None
    message: str


class RecordAttendanceInput(BaseModel):
    subject_id: int = Field(..., description="ID of the subject")
    class_date: date = Field(default_factory=date.today, description="Date of the session")
    status: str = Field(..., description="'attended', 'missed', or 'duty_leave'")
    session_weight: float = Field(default=1.0, ge=0.5, le=4.0)
    note: Optional[str] = None


class RecordAttendanceResponse(BaseModel):
    success: bool
    message: str
    record_id: int
    subject_name: str
    new_attendance_pct: float
