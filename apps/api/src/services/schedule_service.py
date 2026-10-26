"""
Schedule Domain Service
Resolves current, upcoming, and next-class schedules from relational timetable tables.
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.src.models.academic import Semester, Subject, TimetableSession
from apps.api.src.schemas.api_schemas import (
    TodaySessionOut,
    TodayScheduleResponse,
    NextClassResponse,
)


DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class ScheduleService:
    @staticmethod
    def _parse_time_to_minutes(time_str: str) -> int:
        """Converts '09:30' or '14:15' to total minutes from midnight."""
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])

    @classmethod
    async def get_today_schedule(
        cls,
        db: AsyncSession,
        user_id: int = 1,
        target_date: Optional[date] = None,
        reference_time: Optional[datetime] = None,
    ) -> TodayScheduleResponse:
        """
        Retrieves today's timetable sessions ordered by start time.
        Categorizes each session as 'completed', 'ongoing', or 'upcoming'.
        """
        ref_dt = reference_time or datetime.now()
        cur_date = target_date or ref_dt.date()
        day_of_week = cur_date.weekday()  # 0=Monday, 6=Sunday
        current_minutes = ref_dt.hour * 60 + ref_dt.minute

        # Query active semester sessions for this user on this day
        query = (
            select(TimetableSession)
            .join(Subject, TimetableSession.subject_id == Subject.id)
            .join(Semester, Subject.semester_id == Semester.id)
            .where(
                Semester.user_id == user_id,
                Semester.is_active.is_(True),
                TimetableSession.day_of_week == day_of_week,
            )
            .options(selectinload(TimetableSession.subject))
            .order_by(TimetableSession.start_time.asc())
        )
        result = await db.execute(query)
        sessions = result.scalars().all()

        formatted_sessions: List[TodaySessionOut] = []
        for sess in sessions:
            start_min = cls._parse_time_to_minutes(sess.start_time)
            end_min = cls._parse_time_to_minutes(sess.end_time)

            if current_minutes > end_min:
                status = "completed"
            elif start_min <= current_minutes <= end_min:
                status = "ongoing"
            else:
                status = "upcoming"

            formatted_sessions.append(
                TodaySessionOut(
                    session_id=sess.id,
                    subject_id=sess.subject_id,
                    subject_code=sess.subject.code,
                    subject_name=sess.subject.name,
                    start_time=sess.start_time,
                    end_time=sess.end_time,
                    session_type=sess.session_type,
                    room=sess.room,
                    building=sess.building,
                    instructor=sess.subject.instructor_name,
                    status=status,
                )
            )

        return TodayScheduleResponse(
            date=cur_date.isoformat(),
            day_name=DAY_NAMES[day_of_week],
            day_of_week=day_of_week,
            total_classes=len(formatted_sessions),
            sessions=formatted_sessions,
        )

    @classmethod
    async def get_next_class(
        cls,
        db: AsyncSession,
        user_id: int = 1,
        reference_time: Optional[datetime] = None,
    ) -> NextClassResponse:
        """
        Finds the immediate next class and computes minutes remaining.
        If today's lectures have ended, seamlessly looks ahead to tomorrow.
        """
        ref_dt = reference_time or datetime.now()
        current_minutes = ref_dt.hour * 60 + ref_dt.minute
        today_date = ref_dt.date()

        # Step 1: Check remaining classes today
        today_schedule = await cls.get_today_schedule(
            db, user_id=user_id, target_date=today_date, reference_time=ref_dt
        )

        upcoming_today = [
            s for s in today_schedule.sessions 
            if s.status == "upcoming" or s.status == "ongoing"
        ]

        if upcoming_today:
            next_s = upcoming_today[0]
            start_min = cls._parse_time_to_minutes(next_s.start_time)
            mins_left = max(0, start_min - current_minutes)

            if next_s.status == "ongoing":
                msg = f"{next_s.subject_name} is currently ONGOING in {next_s.room}."
            elif mins_left <= 15:
                msg = f"Hurry! Next class is {next_s.subject_name} in {mins_left} minutes in {next_s.room}."
            else:
                msg = f"Your next class is {next_s.subject_name} at {next_s.start_time} in {next_s.room}."

            return NextClassResponse(
                has_upcoming=True,
                subject_name=next_s.subject_name,
                subject_code=next_s.subject_code,
                start_time=next_s.start_time,
                room=next_s.room,
                building=next_s.building,
                instructor=next_s.instructor,
                minutes_remaining=mins_left,
                message=msg,
            )

        # Step 2: No more classes today -> check tomorrow
        tomorrow_date = today_date + timedelta(days=1)
        tomorrow_dt = datetime.combine(tomorrow_date, datetime.min.time())
        tomorrow_schedule = await cls.get_today_schedule(
            db, user_id=user_id, target_date=tomorrow_date, reference_time=tomorrow_dt
        )

        if tomorrow_schedule.sessions:
            first_tomorrow = tomorrow_schedule.sessions[0]
            msg = (
                f"No more classes today! Your next class is {first_tomorrow.subject_name} "
                f"tomorrow ({tomorrow_schedule.day_name}) at {first_tomorrow.start_time} in {first_tomorrow.room}."
            )
            return NextClassResponse(
                has_upcoming=True,
                subject_name=first_tomorrow.subject_name,
                subject_code=first_tomorrow.subject_code,
                start_time=first_tomorrow.start_time,
                room=first_tomorrow.room,
                building=first_tomorrow.building,
                instructor=first_tomorrow.instructor,
                minutes_remaining=None,
                message=msg,
            )

        return NextClassResponse(
            has_upcoming=False,
            message="No upcoming classes scheduled for today or tomorrow. Enjoy your break!",
        )
