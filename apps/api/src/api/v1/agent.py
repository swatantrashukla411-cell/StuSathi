"""
Conversational Agent REST Endpoints
Handles natural language questions, tool orchestration, and multi-lingual responses.
"""

import re
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import edge_tts

from apps.api.src.core.database import get_db
from apps.api.src.agent.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/agent", tags=["AI Agent"])


class ChatMessageInput(BaseModel):
    message: str = Field(..., description="User voice transcript or text query")
    user_id: int = Field(default=1, description="Student user ID")


class ChatMessageResponse(BaseModel):
    reply: str = Field(..., description="Natural language agent response")
    tool_invoked: Optional[str] = Field(None, description="Name of backend academic tool executed")
    tool_result: Optional[Dict[str, Any]] = Field(None, description="Raw structured JSON returned by tool")
    latency_ms: float = Field(..., description="End-to-end response time in milliseconds")
    provider: str = Field(..., description="Agent engine provider (gemini or deterministic)")


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_agent(
    payload: ChatMessageInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Primary conversational agent interface:
    Processes user query in Hinglish/English, executes appropriate academic tools,
    and returns verified conversational response.
    """
    result = await AgentOrchestrator.process_user_query(
        message=payload.message,
        user_id=payload.user_id,
        db=db,
    )
    return ChatMessageResponse(**result)


@router.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="Text to speak in Hindi/Hinglish/English"),
    voice: Optional[str] = Query("hi-IN-SwaraNeural", description="Neural voice identifier"),
):
    """
    Streams high-fidelity neural MP3 audio using edge-tts.
    Zero dependency on client OS speech voices. Guaranteed playback on all devices.
    """
    # Clean text: remove markdown symbols, bullets, asterisks, urls
    clean = re.sub(r"[*_#`~[\]()]", "", text)
    clean = re.sub(r"https?://\S+", "", clean).strip()
    if not clean:
        clean = "Main sun raha hoon."

    communicate = edge_tts.Communicate(clean, voice)

    async def audio_stream():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(
        audio_stream(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": "inline; filename=speech.mp3",
        },
    )
