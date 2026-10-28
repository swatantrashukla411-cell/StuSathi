"""
Timetable REST Endpoints
Provides today's schedule and next class countdown.
"""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.src.core.database import get_db
from apps.api.src.schemas.api_schemas import TodayScheduleResponse, NextClassResponse
from apps.api.src.services.schedule_service import ScheduleService

router = APIRouter(prefix="/timetable", tags=["Timetable"])


@router.get("/today", response_model=TodayScheduleResponse)
async def get_today_schedule(
    user_id: int = Query(default=1, description="Student user ID"),
    target_date: Optional[date] = Query(default=None, description="Optional target date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns today's or target date's schedule ordered chronologically,
    indicating completed, ongoing, and upcoming classes.
    """
    return await ScheduleService.get_today_schedule(db=db, user_id=user_id, target_date=target_date)


@router.get("/tomorrow", response_model=TodayScheduleResponse)
async def get_tomorrow_schedule(
    user_id: int = Query(default=1, description="Student user ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns tomorrow's schedule for students planning ahead at night.
    """
    tomorrow = date.today() + timedelta(days=1)
    return await ScheduleService.get_today_schedule(db=db, user_id=user_id, target_date=tomorrow)


@router.get("/next", response_model=NextClassResponse)
async def get_next_class(
    user_id: int = Query(default=1, description="Student user ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the immediate next upcoming class, room number,
    and a real-time countdown in minutes.
    """
    return await ScheduleService.get_next_class(db=db, user_id=user_id)
