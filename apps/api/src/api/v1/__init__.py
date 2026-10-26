from fastapi import APIRouter
from .timetable import router as timetable_router
from .attendance import router as attendance_router
from .gpa import router as gpa_router
from .qums import router as qums_router
from .agent import router as agent_router

api_router = APIRouter()
api_router.include_router(timetable_router)
api_router.include_router(attendance_router)
api_router.include_router(gpa_router)
api_router.include_router(qums_router)
api_router.include_router(agent_router)

__all__ = ["api_router"]
