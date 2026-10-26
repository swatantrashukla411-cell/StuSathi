"""
Database Seed Script
Populates a realistic engineering student profile, active semester, subjects,
weekly timetable, and 6-week historical attendance records.
"""

import asyncio
from datetime import date, timedelta
from sqlalchemy import select
from apps.api.src.core.database import engine, Base, AsyncSessionLocal
from apps.api.src.models.academic import (
    User,
    Semester,
    Subject,
    TimetableSession,
    AttendanceRecord,
    GradeRecord,
)


async def seed_database():
    print("[*] Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("[*] Creating student profile: Swatantra Shukla...")
        user = User(
            id=1,
            full_name="Swatantra Shukla",
            email="swatantrashukla411@gmail.com",
            program="B.Tech Computer Science & Engineering (AI/ML)",
        )
        session.add(user)
        await session.flush()

        print("[*] Creating Semesters...")
        # Previous Semester 4 (for CGPA calculation)
        sem4 = Semester(
            id=1,
            user_id=user.id,
            semester_number=4,
            name="Spring Semester 2026",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 5, 25),
            is_active=False,
        )
        # Current Active Semester 5
        sem5 = Semester(
            id=2,
            user_id=user.id,
            semester_number=5,
            name="Autumn Semester 2026",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 12, 15),
            is_active=True,
        )
        session.add_all([sem4, sem5])
        await session.flush()

        print("[*] Creating 5th Semester Subjects...")
        s_dbms = Subject(
            id=1,
            semester_id=sem5.id,
            code="CS501",
            name="Database Management Systems",
            credits=4.0,
            attendance_threshold=75.0,
            instructor_name="Dr. R. K. Sharma",
            default_room="Room 304, Block B",
            total_planned_sessions=40,
        )
        s_os = Subject(
            id=2,
            semester_id=sem5.id,
            code="CS502",
            name="Operating Systems",
            credits=4.0,
            attendance_threshold=75.0,
            instructor_name="Prof. Priya Verma",
            default_room="Room 201, Block A",
            total_planned_sessions=40,
        )
        s_cn = Subject(
            id=3,
            semester_id=sem5.id,
            code="CS503",
            name="Computer Networks",
            credits=3.0,
            attendance_threshold=75.0,
            instructor_name="Dr. A. K. Gupta",
            default_room="Room 105, Block B",
            total_planned_sessions=35,
        )
        s_toc = Subject(
            id=4,
            semester_id=sem5.id,
            code="CS504",
            name="Theory of Computation",
            credits=4.0,
            attendance_threshold=75.0,
            instructor_name="Prof. S. Sengupta",
            default_room="Room 302, Block B",
            total_planned_sessions=40,
        )
        s_lab = Subject(
            id=5,
            semester_id=sem5.id,
            code="CS505",
            name="DBMS Practical Lab",
            credits=1.5,
            attendance_threshold=75.0,
            instructor_name="Dr. R. K. Sharma",
            default_room="Lab 304, Block B",
            total_planned_sessions=14,
        )
        session.add_all([s_dbms, s_os, s_cn, s_toc, s_lab])
        await session.flush()

        print("[*] Creating Weekly Timetable Sessions (Mon - Fri)...")
        # Monday (0)
        sessions_mon = [
            TimetableSession(subject_id=s_dbms.id, day_of_week=0, start_time="09:00", end_time="10:00", session_type="lecture", room="Room 304", building="Block B"),
            TimetableSession(subject_id=s_os.id, day_of_week=0, start_time="10:15", end_time="11:15", session_type="lecture", room="Room 201", building="Block A"),
            TimetableSession(subject_id=s_lab.id, day_of_week=0, start_time="11:30", end_time="13:00", session_type="lab", room="Lab 304", building="Block B"),
            TimetableSession(subject_id=s_cn.id, day_of_week=0, start_time="14:00", end_time="15:00", session_type="lecture", room="Room 105", building="Block B"),
        ]
        # Tuesday (1)
        sessions_tue = [
            TimetableSession(subject_id=s_toc.id, day_of_week=1, start_time="09:00", end_time="10:00", session_type="lecture", room="Room 302", building="Block B"),
            TimetableSession(subject_id=s_dbms.id, day_of_week=1, start_time="10:15", end_time="11:15", session_type="lecture", room="Room 304", building="Block B"),
            TimetableSession(subject_id=s_os.id, day_of_week=1, start_time="11:30", end_time="12:30", session_type="lecture", room="Room 201", building="Block A"),
        ]
        # Wednesday (2)
        sessions_wed = [
            TimetableSession(subject_id=s_cn.id, day_of_week=2, start_time="09:00", end_time="10:00", session_type="lecture", room="Room 105", building="Block B"),
            TimetableSession(subject_id=s_toc.id, day_of_week=2, start_time="10:15", end_time="11:15", session_type="lecture", room="Room 302", building="Block B"),
            TimetableSession(subject_id=s_dbms.id, day_of_week=2, start_time="14:00", end_time="15:00", session_type="lecture", room="Room 304", building="Block B"),
        ]
        # Thursday (3)
        sessions_thu = [
            TimetableSession(subject_id=s_os.id, day_of_week=3, start_time="09:00", end_time="10:00", session_type="lecture", room="Room 201", building="Block A"),
            TimetableSession(subject_id=s_cn.id, day_of_week=3, start_time="10:15", end_time="11:15", session_type="lecture", room="Room 105", building="Block B"),
            TimetableSession(subject_id=s_toc.id, day_of_week=3, start_time="11:30", end_time="12:30", session_type="lecture", room="Room 302", building="Block B"),
        ]
        # Friday (4)
        sessions_fri = [
            TimetableSession(subject_id=s_dbms.id, day_of_week=4, start_time="09:00", end_time="10:00", session_type="lecture", room="Room 304", building="Block B"),
            TimetableSession(subject_id=s_os.id, day_of_week=4, start_time="10:15", end_time="11:15", session_type="lecture", room="Room 201", building="Block A"),
            TimetableSession(subject_id=s_lab.id, day_of_week=4, start_time="11:30", end_time="13:00", session_type="lab", room="Lab 304", building="Block B"),
        ]
        session.add_all(sessions_mon + sessions_tue + sessions_wed + sessions_thu + sessions_fri)
        await session.flush()

        print("[*] Generating Attendance History...")
        # 1. DBMS: 23 attended / 28 conducted = 82.14% (SAFE)
        start_cal = date(2026, 8, 15)
        for i in range(28):
            st = "attended" if i < 23 else "missed"
            session.add(AttendanceRecord(
                subject_id=s_dbms.id,
                class_date=start_cal + timedelta(days=i * 2),
                status=st,
                session_weight=1.0,
            ))

        # 2. OS: 19 attended / 25 conducted = 76.0% (CAUTION: 1 missed away from danger!)
        for i in range(25):
            st = "attended" if i < 19 else "missed"
            session.add(AttendanceRecord(
                subject_id=s_os.id,
                class_date=start_cal + timedelta(days=i * 2),
                status=st,
                session_weight=1.0,
            ))

        # 3. CN: 22 attended / 25 conducted = 88.0% (SAFE)
        for i in range(25):
            st = "attended" if i < 22 else "missed"
            session.add(AttendanceRecord(
                subject_id=s_cn.id,
                class_date=start_cal + timedelta(days=i * 2),
                status=st,
                session_weight=1.0,
            ))

        # 4. TOC: 17 attended / 25 conducted = 68.0% (CRITICAL: Below 75% threshold!)
        for i in range(25):
            st = "attended" if i < 17 else "missed"
            session.add(AttendanceRecord(
                subject_id=s_toc.id,
                class_date=start_cal + timedelta(days=i * 2),
                status=st,
                session_weight=1.0,
            ))

        # 5. DBMS Lab: 8 attended / 8 conducted = 100% (SAFE)
        for i in range(8):
            session.add(AttendanceRecord(
                subject_id=s_lab.id,
                class_date=start_cal + timedelta(days=i * 7),
                status="attended",
                session_weight=1.5,
            ))

        print("[*] Adding Grade Records for Past Semester...")
        # Add Sem 4 course for historical CGPA
        s_past = Subject(
            semester_id=sem4.id,
            code="CS401",
            name="Data Structures & Algorithms",
            credits=24.0,
            attendance_threshold=75.0,
        )
        session.add(s_past)
        await session.flush()

        session.add(GradeRecord(
            subject_id=s_past.id,
            semester_id=sem4.id,
            grade_point=8.40,
            grade_letter="A",
            is_completed=True,
        ))

        await session.commit()
        print("[SUCCESS] Database seeding successfully completed!")


if __name__ == "__main__":
    asyncio.run(seed_database())
