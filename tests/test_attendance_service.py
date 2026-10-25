"""
Unit Tests for Attendance Deterministic Service
Verifies 100% mathematical accuracy on boundary conditions, what-if simulations,
and recovery formulations.
"""

import pytest
from apps.api.src.schemas.attendance_schemas import (
    RiskCategory,
    SimulateAbsenceRequest,
    AttendanceRecoveryRequest,
)
from apps.api.src.services.attendance_service import AttendanceService


class TestAttendanceServicePercentages:
    def test_zero_classes_conducted(self):
        """When semester just began, attendance should default to 100%, not crash with ZeroDivisionError."""
        pct = AttendanceService.calculate_current_percentage(attended=0, conducted=0)
        assert pct == 100.0

    def test_exact_75_percent_threshold(self):
        """15 attended out of 20 conducted must be exactly 75.0%."""
        pct = AttendanceService.calculate_current_percentage(attended=15, conducted=20)
        assert pct == 75.0

    def test_above_and_below_threshold(self):
        above = AttendanceService.calculate_current_percentage(attended=16, conducted=20)
        below = AttendanceService.calculate_current_percentage(attended=14, conducted=20)
        assert above == 80.0
        assert below == 70.0


class TestMaxSafeAbsencesFormula:
    def test_safe_absences_calculation(self):
        """
        Given:
            Attended (A) = 24
            Conducted (T) = 28
            Remaining (R) = 12
            Total semester sessions = 40
            Required (p = 0.75) = 0.75 * 40 = 30
            Raw formula: floor(A + R - p*(T+R)) = floor(24 + 12 - 30) = 6
        """
        max_absences = AttendanceService.calculate_max_safe_absences(
            attended=24,
            conducted=28,
            remaining=12,
            threshold_fraction=0.75,
        )
        assert max_absences == 6

        # Mathematical verification:
        # If student misses 6 out of 12 remaining, they attend 6.
        # Total attended = 24 + 6 = 30.
        # Total conducted = 40.
        # Final attendance = 30 / 40 = 75.0%
        final_pct = (24 + (12 - 6)) / 40
        assert final_pct >= 0.75

    def test_safe_absences_when_at_critical_risk(self):
        """When student is already below threshold and cannot afford to miss any class, safe absences must clamp to 0."""
        max_absences = AttendanceService.calculate_max_safe_absences(
            attended=10,
            conducted=20,
            remaining=10,
            threshold_fraction=0.75,
        )
        assert max_absences == 0

    def test_zero_remaining_sessions(self):
        """When semester has concluded (R=0), safe absences must be 0."""
        max_absences = AttendanceService.calculate_max_safe_absences(
            attended=30,
            conducted=35,
            remaining=0,
            threshold_fraction=0.75,
        )
        assert max_absences == 0


class TestSimulateAbsence:
    def test_simulate_single_absence_staying_safe(self):
        req = SimulateAbsenceRequest(
            classes_attended=24,
            classes_conducted=28,
            remaining_planned_sessions=12,
            sessions_to_miss=1,
            required_threshold=75.0,
        )
        resp = AttendanceService.simulate_absence(req)

        # Attended = 24, Remaining = 12. Miss 1 => attends 11.
        # Total attended = 24 + 11 = 35. Total = 40.
        # Projected = 35 / 40 = 87.5%
        assert resp.current_percentage == round((24 / 28) * 100, 2)
        assert resp.projected_percentage == 87.5
        assert resp.is_safe is True
        assert resp.safe_absences_remaining_after == 5  # Was 6, now 5

    def test_simulate_absence_causing_breach(self):
        """
        Attended = 15, Conducted = 20 (75%).
        Remaining = 10. Total = 30.
        If student misses 3 sessions, they can at most attend 15 + 7 = 22 sessions.
        Max possible = 22 / 30 = 73.33% < 75%.
        This accurately puts the student into UNRECOVERABLE status because even
        attending all remaining 7 sessions cannot reach the 75% threshold.
        """
        req = SimulateAbsenceRequest(
            classes_attended=15,
            classes_conducted=20,
            remaining_planned_sessions=10,
            sessions_to_miss=3,
            required_threshold=75.0,
        )
        resp = AttendanceService.simulate_absence(req)
        assert resp.projected_percentage == 73.33
        assert resp.is_safe is False
        assert resp.risk_category_after == RiskCategory.UNRECOVERABLE


class TestAttendanceRecovery:
    def test_achievable_recovery_plan(self):
        """
        Student has 12 attended out of 20 conducted (60%).
        Remaining sessions = 20.
        Threshold = 75%.
        Formula: ceil((0.75 * 20 - 12) / (1 - 0.75)) = ceil((15 - 12) / 0.25) = 12 classes.
        Verification: (12 + 12) / (20 + 12) = 24 / 32 = 75.0%.
        """
        req = AttendanceRecoveryRequest(
            classes_attended=12,
            classes_conducted=20,
            remaining_planned_sessions=20,
            target_threshold=75.0,
        )
        resp = AttendanceService.calculate_recovery_plan(req)

        assert resp.is_recoverable is True
        assert resp.classes_needed_consecutively == 12
        assert resp.remaining_sessions_available == 20

    def test_impossible_recovery(self):
        """
        Student has 5 attended out of 30 conducted (16.67%).
        Remaining sessions = 10.
        Max possible = (5 + 10) / (30 + 10) = 15 / 40 = 37.5%.
        Cannot ever hit 75%.
        """
        req = AttendanceRecoveryRequest(
            classes_attended=5,
            classes_conducted=30,
            remaining_planned_sessions=10,
            target_threshold=75.0,
        )
        resp = AttendanceService.calculate_recovery_plan(req)

        assert resp.is_recoverable is False
        assert resp.max_possible_percentage == 37.5
        assert "mathematically unrecoverable" in resp.explanation.lower()

    def test_already_above_threshold(self):
        """If student already has 90%, 0 recovery classes needed."""
        req = AttendanceRecoveryRequest(
            classes_attended=18,
            classes_conducted=20,
            remaining_planned_sessions=15,
            target_threshold=75.0,
        )
        resp = AttendanceService.calculate_recovery_plan(req)

        assert resp.is_recoverable is True
        assert resp.classes_needed_consecutively == 0


class TestSubjectSummaryScenarios:
    def test_summary_safe_status(self):
        summary = AttendanceService.get_subject_summary(
            subject_code="CS501",
            subject_name="DBMS",
            classes_attended=25,
            classes_conducted=28,
            remaining_planned_sessions=12,
            required_threshold=75.0,
        )
        assert summary.risk_category == RiskCategory.SAFE
        assert summary.classes_missed == 3
        assert summary.current_percentage == round((25 / 28) * 100, 2)
        assert summary.safe_future_absences > 0

    def test_summary_caution_status(self):
        # 19 / 25 = 76% (in caution range between 75% and 80%)
        summary = AttendanceService.get_subject_summary(
            subject_code="CS502",
            subject_name="OS",
            classes_attended=19,
            classes_conducted=25,
            remaining_planned_sessions=10,
            required_threshold=75.0,
        )
        assert summary.risk_category == RiskCategory.CAUTION
        assert summary.current_percentage == 76.0

    def test_summary_critical_status(self):
        summary = AttendanceService.get_subject_summary(
            subject_code="CS503",
            subject_name="Maths",
            classes_attended=12,
            classes_conducted=20,
            remaining_planned_sessions=15,
            required_threshold=75.0,
        )
        assert summary.risk_category == RiskCategory.CRITICAL

    def test_summary_unrecoverable_status(self):
        summary = AttendanceService.get_subject_summary(
            subject_code="CS504",
            subject_name="Physics",
            classes_attended=5,
            classes_conducted=30,
            remaining_planned_sessions=5,
            required_threshold=75.0,
        )
        assert summary.risk_category == RiskCategory.UNRECOVERABLE

    def test_summary_validation_attended_greater_than_conducted(self):
        with pytest.raises(ValueError, match="cannot exceed conducted"):
            AttendanceService.get_subject_summary(
                subject_code="ERR",
                subject_name="Error Course",
                classes_attended=25,
                classes_conducted=20,
            )

