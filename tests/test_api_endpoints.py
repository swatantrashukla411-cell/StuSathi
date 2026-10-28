"""
FastAPI REST API Integration Tests
Tests all HTTP endpoints against the seeded database using httpx.AsyncClient.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestSystemHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "CampusPilot" in data["service"]

    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        assert "CampusPilot" in response.json()["message"]


class TestTimetableEndpoints:
    @pytest.mark.asyncio
    async def test_get_today_schedule(self, client: AsyncClient):
        response = await client.get("/api/v1/timetable/today?user_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "day_name" in data
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    @pytest.mark.asyncio
    async def test_get_next_class(self, client: AsyncClient):
        response = await client.get("/api/v1/timetable/next?user_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "has_upcoming" in data
        assert "message" in data


class TestAttendanceEndpoints:
    @pytest.mark.asyncio
    async def test_get_attendance_summary(self, client: AsyncClient):
        response = await client.get("/api/v1/attendance/summary?user_id=1")
        assert response.status_code == 200
        subjects = response.json()
        assert len(subjects) >= 5

        # Check fields in first subject
        sub = subjects[0]
        assert "subject_name" in sub
        assert "classes_conducted" in sub
        assert "classes_attended" in sub
        assert "current_percentage" in sub
        assert "risk_category" in sub

    @pytest.mark.asyncio
    async def test_simulate_absence_endpoint(self, client: AsyncClient):
        payload = {
            "classes_conducted": 28,
            "classes_attended": 23,
            "remaining_planned_sessions": 12,
            "sessions_to_miss": 1,
            "required_threshold": 75.0,
        }
        response = await client.post("/api/v1/attendance/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["current_percentage"] == 82.14
        assert data["projected_percentage"] == 85.0
        assert data["is_safe"] is True

    @pytest.mark.asyncio
    async def test_attendance_recovery_endpoint(self, client: AsyncClient):
        # 17 attended out of 25 conducted (68%)
        payload = {
            "classes_conducted": 25,
            "classes_attended": 17,
            "remaining_planned_sessions": 15,
            "target_threshold": 75.0,
        }
        response = await client.post("/api/v1/attendance/recover", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_recoverable"] is True
        assert data["classes_needed_consecutively"] == 7

    @pytest.mark.asyncio
    async def test_record_attendance_endpoint(self, client: AsyncClient):
        payload = {
            "subject_id": 1,
            "class_date": "2026-10-27",
            "status": "attended",
            "session_weight": 1.0,
            "note": "Attended lecture on SQL indexing",
        }
        response = await client.post("/api/v1/attendance/record", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subject_name"] == "Database Management Systems"
        assert data["new_attendance_pct"] > 82.0


class TestGPAEndpoints:
    @pytest.mark.asyncio
    async def test_get_gpa_summary(self, client: AsyncClient):
        response = await client.get("/api/v1/gpa/summary?user_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "cumulative_cgpa" in data
        assert data["cumulative_cgpa"]["cgpa"] == 8.40

    @pytest.mark.asyncio
    async def test_solve_target_cgpa_endpoint(self, client: AsyncClient):
        payload = {
            "current_cgpa": 8.40,
            "completed_credits": 24.0,
            "remaining_credits": 76.0,
            "target_cgpa": 8.80,
            "max_scale": 10.0,
        }
        response = await client.post("/api/v1/gpa/target", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_achievable"] is True
        assert data["required_future_sgpa"] > 8.80
