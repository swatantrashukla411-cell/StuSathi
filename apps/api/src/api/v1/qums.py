"""
QUMS Integration REST Endpoints
Handles live captcha retrieval and in-memory credential sync from QUMS.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.src.core.database import get_db
from apps.api.src.services.qums_service import QUMSService

router = APIRouter(prefix="/integrations/qums", tags=["QUMS Integration"])


class QUMSCaptchaResponse(BaseModel):
    session_token: str
    captcha_image: str = Field(..., description="Base64 encoded PNG data URL")
    form_token: str


class QUMSSyncRequest(BaseModel):
    session_token: str = Field(..., description="Session token received from captcha endpoint")
    qid: str = Field(..., description="Quantum ID / User Name")
    password: str = Field(..., description="Password (ephemeral in-memory only)")
    captcha: str = Field(..., description="Captcha text entered by student")
    user_id: int = Field(default=1, description="Target student user ID in CampusPilot")


class QUMSSyncResponse(BaseModel):
    success: bool
    message: str
    synced_subjects: list


@router.get("/captcha", response_model=QUMSCaptchaResponse)
async def get_qums_captcha():
    """
    Connects to QUMS portal live, creates an active session,
    and returns a fresh Captcha image for the student to solve.
    """
    try:
        data = await QUMSService.get_captcha_session()
        return QUMSCaptchaResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to reach QUMS server: {str(e)}",
        )


@router.post("/sync", response_model=QUMSSyncResponse)
async def sync_qums_data(
    payload: QUMSSyncRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticates with QUMS using the student's credentials and captcha,
    extracts their dashboard attendance table, and syncs into CampusPilot.
    Credentials are processed strictly in-memory and never stored.
    """
    try:
        result = await QUMSService.sync_student_data(
            session_token=payload.session_token,
            qid=payload.qid,
            password=payload.password,
            captcha=payload.captcha,
            user_id=payload.user_id,
            db=db,
        )
        return QUMSSyncResponse(**result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"QUMS Sync Error: {str(e)}",
        )
