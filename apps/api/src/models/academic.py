"""
Academic Relational Database Models
SQLAlchemy 2.0 models for Semesters, Subjects, Timetables, Attendance, and Grades.
"""

from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.api.src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    program: Mapped[str] = mapped_column(String(255), default="B.Tech Computer Science & Engineering")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    semesters: Mapped[List["Semester"]] = relationship("Semester", back_populates="user", cascade="all, delete-orphan")


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    semester_number: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g. 5
    name: Mapped[str] = mapped_column(String(100), default="Semester 5")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="semesters")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="semester", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id", ondelete="CASCADE"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. CS501
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. Database Management Systems
    credits: Mapped[float] = mapped_column(Float, default=4.0)
    attendance_threshold: Mapped[float] = mapped_column(Float, default=75.0)  # Standard 75%
    instructor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    default_room: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_planned_sessions: Mapped[int] = mapped_column(Integer, default=40)  # Planned semester sessions

    # Relationships
    semester: Mapped["Semester"] = relationship("Semester", back_populates="subjects")
    timetable_sessions: Mapped[List["TimetableSession"]] = relationship(
        "TimetableSession", back_populates="subject", cascade="all, delete-orphan"
    )
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship(
        "AttendanceRecord", back_populates="subject", cascade="all, delete-orphan"
    )
    grade_record: Mapped[Optional["GradeRecord"]] = relationship(
        "GradeRecord", back_populates="subject", uselist=False, cascade="all, delete-orphan"
    )


class TimetableSession(Base):
    __tablename__ = "timetable_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, ..., 6=Sunday
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)  # "09:00"
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)  # "10:00"
    session_type: Mapped[str] = mapped_column(String(50), default="lecture")  # lecture, lab, tutorial
    room: Mapped[str] = mapped_column(String(100), default="Room 304")
    building: Mapped[str] = mapped_column(String(100), default="Academic Block B")

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="timetable_sessions")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timetable_sessions.id", ondelete="SET NULL"), nullable=True)
    class_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # attended, missed, cancelled, duty_leave
    session_weight: Mapped[float] = mapped_column(Float, default=1.0)  # e.g. 1.0 for 1-hr lecture, 2.0 for 2-hr lab
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="attendance_records")


class GradeRecord(Base):
    __tablename__ = "grade_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), unique=True, nullable=False)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id", ondelete="CASCADE"), index=True, nullable=False)
    grade_point: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 10.0
    grade_letter: Mapped[str] = mapped_column(String(10), default="A")  # O, A+, A, B+, B, C, P, F
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="grade_record")
