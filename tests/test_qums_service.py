"""
QUMS Integration Tests
Tests HTML attendance table parsing, session lifecycle, and error handling.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.main import app
from apps.api.src.services.qums_service import QUMSService


SAMPLE_QUMS_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div id="content">
        <h3>Current Semester Attendance Status</h3>
        <table class="table table-bordered table-striped" id="tblAttendance">
            <thead>
                <tr>
                    <th>S.No</th>
                    <th>Subject Code & Name</th>
                    <th>Conducted</th>
                    <th>Attended</th>
                    <th>Absent</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>CS501 - Database Management Systems</td>
                    <td>30</td>
                    <td>26</td>
                    <td>4</td>
                    <td>86.67%</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>CS502 - Operating Systems</td>
                    <td>28</td>
                    <td>21</td>
                    <td>7</td>
                    <td>75.00%</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>CS503 - Computer Networks</td>
                    <td>25</td>
                    <td>22</td>
                    <td>3</td>
                    <td>88.00%</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>CS504 - Theory of Computation</td>
                    <td>26</td>
                    <td>16</td>
                    <td>10</td>
                    <td>61.54%</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""


class TestQUMSHTMLParsing:
    def test_parse_sample_attendance_table(self):
        parsed = QUMSService._parse_attendance_from_html(SAMPLE_QUMS_DASHBOARD_HTML)
        assert len(parsed) == 4

        # Subject 1 check
        s1 = parsed[0]
        assert s1["subject_code"] == "CS501"
        assert "Database Management Systems" in s1["subject_name"]
        assert s1["classes_conducted"] == 30.0
        assert s1["classes_attended"] == 26.0
        assert s1["percentage"] == 86.67

        # Subject 4 (critical risk) check
        s4 = parsed[3]
        assert s4["subject_code"] == "CS504"
        assert s4["classes_conducted"] == 26.0
        assert s4["classes_attended"] == 16.0
        assert s4["percentage"] == 61.54

    def test_parse_jqgrid_attendance_structure(self):
        sample_jqgrid_html = """
        <table id="jqgrdSubject" class="ui-jqgrid-btable">
            <tbody>
                <tr class="jqgfirstrow"><td></td></tr>
                <tr class="jqgrow ui-widget-content">
                    <td aria-describedby="jqgrdSubject_Subject">Design and Analysis of Algorithm (S)</td>
                    <td aria-describedby="jqgrdSubject_SubjectCode">CS35303</td>
                    <td aria-describedby="jqgrdSubject_EMPNAME">VINEET KUMAR SALAR</td>
                    <td aria-describedby="jqgrdSubject_TotalLecture">32</td>
                    <td aria-describedby="jqgrdSubject_TotalPresent">26</td>
                    <td aria-describedby="jqgrdSubject_Percentage">81.25</td>
                </tr>
                <tr class="jqgrow ui-widget-content">
                    <td aria-describedby="jqgrdSubject_Subject">Event Management(L)</td>
                    <td aria-describedby="jqgrdSubject_SubjectCode">JM3015</td>
                    <td aria-describedby="jqgrdSubject_EMPNAME">KAVITA VERMA</td>
                    <td aria-describedby="jqgrdSubject_TotalLecture">23</td>
                    <td aria-describedby="jqgrdSubject_TotalPresent">20</td>
                    <td aria-describedby="jqgrdSubject_Percentage">86.96</td>
                </tr>
            </tbody>
        </table>
        """
        parsed = QUMSService._parse_attendance_from_html(sample_jqgrid_html)
        assert len(parsed) == 2
        assert parsed[0]["subject_code"] == "CS35303"
        assert parsed[0]["classes_conducted"] == 32.0
        assert parsed[0]["classes_attended"] == 26.0
        assert parsed[0]["percentage"] == 81.25
        assert parsed[0]["instructor"] == "VINEET KUMAR SALAR"
        assert parsed[1]["subject_code"] == "JM3015"
        assert parsed[1]["classes_attended"] == 20.0


class TestQUMSEndpoints:
    @pytest.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_get_captcha_endpoint(self, client: AsyncClient):
        """Tests live QUMS captcha generation endpoint."""
        response = await client.get("/api/v1/integrations/qums/captcha")
        # If QUMS is reachable online, returns 200 with data URL
        if response.status_code == 200:
            data = response.json()
            assert "session_token" in data
            assert data["captcha_image"].startswith("data:image/png;base64,")
            assert len(data["captcha_image"]) > 100
        else:
            # If network or campus portal has intermittent connectivity, must return 502 gracefully
            assert response.status_code == 502

    @pytest.mark.asyncio
    async def test_sync_invalid_session_token(self, client: AsyncClient):
        payload = {
            "session_token": "non-existent-session-id",
            "qid": "220101001",
            "password": "fakepassword",
            "captcha": "XYZ1",
        }
        response = await client.post("/api/v1/integrations/qums/sync", json=payload)
        assert response.status_code == 400
        assert "expired or invalid" in response.json()["detail"].lower()
