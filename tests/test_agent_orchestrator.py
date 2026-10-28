"""
AI Agent & Tool Orchestrator Benchmark Tests
Evaluates natural language intent parsing, tool selection, parameter extraction,
and conversational response generation in Hindi, Hinglish, and English.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.main import app
from apps.api.src.core.database import AsyncSessionLocal
from apps.api.src.agent.orchestrator import AgentOrchestrator


class TestAgentConversationalIntents:
    @pytest.mark.asyncio
    async def test_next_class_query_hinglish(self):
        """Student asks: 'Meri next class kaunsi hai aur room number kya hai?'"""
        async with AsyncSessionLocal() as session:
            res = await AgentOrchestrator.process_user_query(
                message="Meri next class kaunsi hai aur room number kya hai?",
                user_id=1,
                db=session,
            )
            assert res["tool_invoked"] == "get_next_class"
            assert "class" in res["reply"].lower()
            assert res["latency_ms"] > 0

    @pytest.mark.asyncio
    async def test_simulate_absence_query_hinglish(self):
        """Student asks about missing a class"""
        async with AsyncSessionLocal() as session:
            from apps.api.src.models.academic import Subject, Semester
            from sqlalchemy import select
            sub_res = await session.execute(
                select(Subject)
                .join(Semester, Subject.semester_id == Semester.id)
                .where(Semester.user_id == 1, Semester.is_active.is_(True))
            )
            subj = sub_res.scalars().first()
            query_word = subj.code if subj else "DBMS"

            res = await AgentOrchestrator.process_user_query(
                message=f"Aaj {query_word} ki class miss karun toh attendance kitni ho jayegi?",
                user_id=1,
                db=session,
            )
            assert res["tool_invoked"] == "simulate_absence"
            assert res["tool_result"] is not None
            assert "%" in res["reply"]

    @pytest.mark.asyncio
    async def test_recovery_plan_query_hinglish(self):
        """Student asks about recovery plan to maintain 75% attendance"""
        async with AsyncSessionLocal() as session:
            from apps.api.src.models.academic import Subject, Semester
            from sqlalchemy import select
            sub_res = await session.execute(
                select(Subject)
                .join(Semester, Subject.semester_id == Semester.id)
                .where(Semester.user_id == 1, Semester.is_active.is_(True))
            )
            subjects = sub_res.scalars().all()
            target = next((s for s in subjects if s.code in ["CS504", "SE35369", "CS35364", "CS35365"]), subjects[0] if subjects else None)
            query_word = target.code if target else "TOC"

            res = await AgentOrchestrator.process_user_query(
                message=f"{query_word} mein 75% attendance maintain karne ke liye kitni classes attend karni hongi?",
                user_id=1,
                db=session,
            )
            assert res["tool_invoked"] == "calculate_recovery"
            assert "classes" in res["reply"].lower()

    @pytest.mark.asyncio
    async def test_attendance_status_query(self):
        """Student asks about attendance percentage"""
        async with AsyncSessionLocal() as session:
            from apps.api.src.models.academic import Subject, Semester
            from sqlalchemy import select
            sub_res = await session.execute(
                select(Subject)
                .join(Semester, Subject.semester_id == Semester.id)
                .where(Semester.user_id == 1, Semester.is_active.is_(True))
            )
            subj = sub_res.scalars().first()
            query_word = subj.code if subj else "DBMS"

            res = await AgentOrchestrator.process_user_query(
                message=f"Meri {query_word} attendance kitni hai?",
                user_id=1,
                db=session,
            )
            assert res["tool_invoked"] == "get_subject_attendance"
            assert res["tool_result"] is not None
            assert "current_percentage" in res["tool_result"]

    @pytest.mark.asyncio
    async def test_today_schedule_query(self):
        """Student asks: 'Hey CampusPilot, aaj meri kitni classes hain?'"""
        async with AsyncSessionLocal() as session:
            res = await AgentOrchestrator.process_user_query(
                message="Hey CampusPilot, aaj meri kitni classes hain?",
                user_id=1,
                db=session,
            )
            assert res["tool_invoked"] == "get_today_schedule"
            assert "classes" in res["reply"].lower()

    @pytest.mark.asyncio
    async def test_target_gpa_query(self):
        """Student asks: 'Mujhe 8.8 CGPA achieve karne ke liye kitna SGPA chahiye?'"""
        async with AsyncSessionLocal() as session:
            res = await AgentOrchestrator.process_user_query(
                message="Mujhe 8.8 CGPA achieve karne ke liye kitna SGPA chahiye?",
                user_id=1,
                db=session,
            )
            assert res["tool_invoked"] == "calculate_target_sgpa"
            assert "sgpa" in res["reply"].lower()
            assert res["tool_result"]["is_achievable"] is True


class TestAgentChatAPIEndpoint:
    @pytest.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_agent_chat_endpoint_e2e(self, client: AsyncClient):
        payload = {
            "message": "Next class kaunsi hai?",
            "user_id": 1,
        }
        response = await client.post("/api/v1/agent/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 5
        assert data["tool_invoked"] == "get_next_class"
        assert data["latency_ms"] > 0
        assert "provider" in data
