"""
Student Authentication and Multi-Tenant Profile Router
Handles student registration, login, profile switching, and auto-initialization.
"""

from typing import List, Optional
from datetime import date, datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.src.core.database import get_db
from apps.api.src.models.academic import (
    User,
    Semester,
    Subject,
    TimetableSession,
    AttendanceRecord,
    GradeRecord,
)

router = APIRouter(prefix="/auth", tags=["Student Authentication"])


class StudentRegisterInput(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Student's real name")
    email_or_qid: str = Field(..., min_length=3, max_length=150, description="College QID or Email ID")
    password: Optional[str] = Field("student123", description="Password")
    program: str = Field("B.Tech Computer Science & Engineering (AI/ML)", description="Academic branch")
    semester_number: int = Field(5, ge=1, le=8, description="Current semester number")


class StudentLoginInput(BaseModel):
    email_or_qid: str = Field(..., description="College QID or Email ID")
    password: Optional[str] = Field(None, description="Password")


class StudentProfile(BaseModel):
    user_id: int
    full_name: str
    email: str
    program: str
    active_semester: int
    created_at: str


class StudentListResponse(BaseModel):
    students: List[StudentProfile]


async def initialize_new_student_curriculum(db: AsyncSession, user: User, sem_num: int):
    """
    Auto-initializes active semester, standard B.Tech subjects, timetable,
    and historical attendance records for any newly registered student.
    """
    today = date.today()
    sem = Semester(
        user_id=user.id,
        semester_number=sem_num,
        name=f"Semester {sem_num} ({today.year})",
        start_date=date(today.year, 8, 1) if today.month >= 7 else date(today.year, 1, 10),
        end_date=date(today.year, 12, 15) if today.month >= 7 else date(today.year, 5, 25),
        is_active=True,
    )
    db.add(sem)
    await db.flush()

    # Standard Engineering Subjects
    standard_subjects = [
        {"code": "CS301", "name": "Database Management Systems", "credits": 4.0, "total": 35, "attended": 30},
        {"code": "CS302", "name": "Operating Systems", "credits": 4.0, "total": 32, "attended": 24},
        {"code": "CS303", "name": "Computer Networks", "credits": 3.0, "total": 28, "attended": 22},
        {"code": "CS304", "name": "Theory of Computation", "credits": 4.0, "total": 30, "attended": 25},
        {"code": "CS305P", "name": "DBMS Practical Lab", "credits": 1.5, "total": 12, "attended": 11},
    ]

    for s_info in standard_subjects:
        subj = Subject(
            semester_id=sem.id,
            code=s_info["code"],
            name=s_info["name"],
            credits=s_info["credits"],
            total_planned_sessions=45,
            attendance_threshold=75.0,
        )
        db.add(subj)
        await db.flush()

        # Seed initial attendance records matching conducted & attended count
        for i in range(s_info["total"]):
            st = "attended" if i < s_info["attended"] else "missed"
            db.add(AttendanceRecord(
                subject_id=subj.id,
                class_date=today - timedelta(days=2 * (s_info["total"] - i)),
                status=st,
                session_weight=1.0,
                note="Curriculum initialization",
            ))

    # Seed weekly schedule
    subjects_res = await db.execute(select(Subject).where(Subject.semester_id == sem.id))
    created_subjects = subjects_res.scalars().all()
    sub_map = {s.code: s.id for s in created_subjects}

    schedule_templates = [
        # Monday
        (0, "09:00", "10:00", "CS301", "Lecture", "Room 302", "Block A"),
        (0, "10:00", "11:00", "CS302", "Lecture", "Room 304", "Block A"),
        (0, "11:30", "13:30", "CS305P", "Lab", "Lab 201", "Block B"),
        # Tuesday
        (1, "09:00", "10:00", "CS303", "Lecture", "Room 105", "Block C"),
        (1, "10:00", "11:00", "CS304", "Lecture", "Room 202", "Block A"),
        (1, "12:00", "13:00", "CS301", "Lecture", "Room 302", "Block A"),
        # Wednesday
        (2, "09:00", "10:00", "CS302", "Lecture", "Room 304", "Block A"),
        (2, "10:00", "11:00", "CS303", "Lecture", "Room 105", "Block C"),
        # Thursday
        (3, "11:00", "12:00", "CS304", "Lecture", "Room 202", "Block A"),
        (3, "12:00", "13:00", "CS301", "Lecture", "Room 302", "Block A"),
        # Friday
        (4, "09:00", "10:00", "CS303", "Lecture", "Room 105", "Block C"),
        (4, "10:00", "11:00", "CS302", "Lecture", "Room 304", "Block A"),
    ]

    for day, start_t, end_t, code, s_type, room, bldg in schedule_templates:
        if code in sub_map:
            session = TimetableSession(
                subject_id=sub_map[code],
                day_of_week=day,
                start_time=start_t,
                end_time=end_t,
                session_type=s_type,
                room=room,
                building=bldg,
            )
            db.add(session)

    await db.commit()


@router.post("/register", response_model=StudentProfile)
async def register_student(
    payload: StudentRegisterInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a new student profile and seeds active semester with subjects & timetable.
    """
    email_clean = payload.email_or_qid.strip().lower()
    if "@" not in email_clean:
        email_clean = f"{email_clean}@quantumuniversity.edu.in"

    # Check if student already exists
    existing = await db.execute(select(User).where(User.email == email_clean))
    user = existing.scalar_one_or_none()

    if user:
        # Return existing student profile
        sem_res = await db.execute(select(Semester).where(Semester.user_id == user.id, Semester.is_active == True))
        active_sem = sem_res.scalar_one_or_none()
        return StudentProfile(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            program=user.program,
            active_semester=active_sem.semester_number if active_sem else 5,
            created_at=user.created_at.isoformat() if user.created_at else str(date.today()),
        )

    # Create new student
    new_user = User(
        full_name=payload.full_name.strip(),
        email=email_clean,
        program=payload.program.strip(),
    )
    db.add(new_user)
    await db.flush()

    # Initialize their curriculum
    await initialize_new_student_curriculum(db=db, user=new_user, sem_num=payload.semester_number)

    return StudentProfile(
        user_id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        program=new_user.program,
        active_semester=payload.semester_number,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/login", response_model=StudentProfile)
async def login_student(
    payload: StudentLoginInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Logs in an existing student or automatically creates their student account if first time.
    """
    identifier = payload.email_or_qid.strip().lower()
    if "@" not in identifier:
        email_target = f"{identifier}@quantumuniversity.edu.in"
    else:
        email_target = identifier

    query = select(User).where((User.email == email_target) | (User.email == identifier))
    res = await db.execute(query)
    user = res.scalar_one_or_none()

    if not user:
        # Auto-create for seamless friction-free onboarding!
        name_guess = identifier.split("@")[0].replace(".", " ").title()
        new_user = User(
            full_name=name_guess if len(name_guess) > 2 else "Quantum Student",
            email=email_target,
            program="B.Tech Computer Science & Engineering (AI/ML)",
        )
        db.add(new_user)
        await db.flush()
        await initialize_new_student_curriculum(db=db, user=new_user, sem_num=5)
        user = new_user

    sem_res = await db.execute(select(Semester).where(Semester.user_id == user.id, Semester.is_active == True))
    active_sem = sem_res.scalar_one_or_none()

    return StudentProfile(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        program=user.program,
        active_semester=active_sem.semester_number if active_sem else 5,
        created_at=user.created_at.isoformat() if user.created_at else str(date.today()),
    )


@router.get("/students", response_model=StudentListResponse)
async def list_registered_students(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns list of all registered student profiles for instant profile switching.
    """
    res = await db.execute(select(User).order_by(User.id.asc()))
    users = res.scalars().all()

    profiles: List[StudentProfile] = []
    for u in users:
        sem_res = await db.execute(select(Semester).where(Semester.user_id == u.id, Semester.is_active == True))
        active_sem = sem_res.scalar_one_or_none()
        profiles.append(
            StudentProfile(
                user_id=u.id,
                full_name=u.full_name,
                email=u.email,
                program=u.program,
                active_semester=active_sem.semester_number if active_sem else 5,
                created_at=u.created_at.isoformat() if u.created_at else str(date.today()),
            )
        )

    return StudentListResponse(students=profiles)


@router.get("/me", response_model=StudentProfile)
async def get_current_student(
    user_id: int = 1,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns current student's active profile by user_id.
    """
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Student profile not found")

    sem_res = await db.execute(select(Semester).where(Semester.user_id == user.id, Semester.is_active == True))
    active_sem = sem_res.scalar_one_or_none()

    return StudentProfile(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        program=user.program,
        active_semester=active_sem.semester_number if active_sem else 5,
        created_at=user.created_at.isoformat() if user.created_at else str(date.today()),
    )
