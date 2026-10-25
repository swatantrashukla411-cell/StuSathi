"""
Attendance Deterministic Calculation Service
Pure Python domain logic. Zero probabilistic LLM arithmetic.
Implements standard university attendance rules, what-if absence simulations,
and consecutive recovery calculations.
"""

import math
from typing import Optional
from apps.api.src.schemas.attendance_schemas import (
    RiskCategory,
    SubjectAttendanceSummary,
    SimulateAbsenceRequest,
    SimulateAbsenceResponse,
    AttendanceRecoveryRequest,
    AttendanceRecoveryResponse,
)


class AttendanceService:
    """
    Deterministic domain service for student attendance arithmetic.
    Every calculation is mathematically proven and handles zero-division and boundary cases.
    """

    @staticmethod
    def calculate_current_percentage(attended: float, conducted: float) -> float:
        """
        Calculates current attendance percentage.
        Edge case: If 0 classes have been conducted (T=0), default to 100.0%.
        """
        if conducted <= 0:
            return 100.0
        return round((attended / conducted) * 100.0, 2)

    @staticmethod
    def calculate_max_safe_absences(
        attended: float,
        conducted: float,
        remaining: int,
        threshold_fraction: float = 0.75,
    ) -> int:
        """
        Calculates the maximum number of future sessions that can be missed
        while still satisfying the attendance threshold p (e.g. 0.75).

        Formula:
            Raw Max Absences = floor(A + R - p * (T + R))
        Clamped between 0 and R.
        """
        if remaining <= 0:
            return 0

        total_sessions = conducted + remaining
        # Exact threshold attended units needed across the whole semester
        required_attended = threshold_fraction * total_sessions
        raw_max = math.floor(attended + remaining - required_attended)

        # Clamping logic: Cannot be negative, and cannot miss more than remaining sessions
        clamped = max(0, min(remaining, raw_max))
        return clamped

    @staticmethod
    def determine_risk_category(
        current_pct: float,
        safe_absences: int,
        attended: float,
        conducted: float,
        remaining: int,
        threshold_pct: float = 75.0,
    ) -> RiskCategory:
        """
        Determines the student's risk category based on threshold and remaining buffer.
        - UNRECOVERABLE: Even 100% attendance in all remaining classes cannot reach threshold.
        - CRITICAL: Currently < threshold_pct.
        - CAUTION: Between threshold_pct and 80.0%, or safe absences <= 1.
        - SAFE: >= 80.0% and has a comfortable absence buffer.
        """
        threshold_fraction = threshold_pct / 100.0
        total_sessions = conducted + remaining
        max_possible_attended = attended + remaining

        # Check if mathematically unrecoverable
        if total_sessions > 0 and (max_possible_attended / total_sessions) < threshold_fraction:
            return RiskCategory.UNRECOVERABLE

        if current_pct < threshold_pct:
            return RiskCategory.CRITICAL

        if current_pct < 80.0 or safe_absences <= 1:
            return RiskCategory.CAUTION

        return RiskCategory.SAFE

    @classmethod
    def get_subject_summary(
        cls,
        subject_code: str,
        subject_name: str,
        classes_attended: float,
        classes_conducted: float,
        remaining_planned_sessions: int = 0,
        required_threshold: float = 75.0,
    ) -> SubjectAttendanceSummary:
        """
        Generates a comprehensive summary for a single subject.
        """
        if classes_attended > classes_conducted:
            raise ValueError("Attended classes cannot exceed conducted classes")

        missed = round(classes_conducted - classes_attended, 2)
        current_pct = cls.calculate_current_percentage(classes_attended, classes_conducted)
        threshold_fraction = required_threshold / 100.0

        safe_absences = cls.calculate_max_safe_absences(
            attended=classes_attended,
            conducted=classes_conducted,
            remaining=remaining_planned_sessions,
            threshold_fraction=threshold_fraction,
        )

        risk = cls.determine_risk_category(
            current_pct=current_pct,
            safe_absences=safe_absences,
            attended=classes_attended,
            conducted=classes_conducted,
            remaining=remaining_planned_sessions,
            threshold_pct=required_threshold,
        )

        # Build clear human-friendly explanation
        if risk == RiskCategory.SAFE:
            explanation = (
                f"Your attendance is healthy at {current_pct}%. "
                f"You can safely miss up to {safe_absences} of the remaining {remaining_planned_sessions} sessions "
                f"and still maintain above {required_threshold}%."
            )
        elif risk == RiskCategory.CAUTION:
            explanation = (
                f"Caution: Your attendance is {current_pct}%. You have a narrow margin: "
                f"you can only miss {safe_absences} more class before dropping below {required_threshold}%."
            )
        elif risk == RiskCategory.CRITICAL:
            explanation = (
                f"Danger Zone: Your attendance is currently {current_pct}%, which is below the mandatory {required_threshold}%. "
                f"You must attend upcoming classes to recover."
            )
        else:
            max_possible = round(((classes_attended + remaining_planned_sessions) / (classes_conducted + remaining_planned_sessions)) * 100.0, 2)
            explanation = (
                f"Mathematically Unrecoverable: Even with 100% attendance in the remaining {remaining_planned_sessions} sessions, "
                f"your maximum possible attendance is {max_possible}%, which cannot reach the required {required_threshold}%."
            )

        return SubjectAttendanceSummary(
            subject_code=subject_code,
            subject_name=subject_name,
            classes_conducted=classes_conducted,
            classes_attended=classes_attended,
            classes_missed=missed,
            current_percentage=current_pct,
            required_threshold=required_threshold,
            remaining_planned_sessions=remaining_planned_sessions,
            safe_future_absences=safe_absences,
            risk_category=risk,
            explanation=explanation,
        )

    @classmethod
    def simulate_absence(cls, req: SimulateAbsenceRequest) -> SimulateAbsenceResponse:
        """
        Simulates missing 'sessions_to_miss' upcoming classes.
        Calculates projected semester-end attendance assuming student attends all other remaining classes.

        Formula:
            Projected Attendance = (A + R - y) / (T + R) * 100
        """
        A = req.classes_attended
        T = req.classes_conducted
        R = req.remaining_planned_sessions
        y = req.sessions_to_miss
        threshold = req.required_threshold
        threshold_frac = threshold / 100.0

        current_pct = cls.calculate_current_percentage(A, T)

        # Semester total sessions
        total_sessions = T + R
        if total_sessions <= 0:
            projected_pct = 100.0
        else:
            # Assuming student attends all remaining EXCEPT the y missed sessions
            projected_pct = round(((A + R - y) / total_sessions) * 100.0, 2)

        # What will the safe absences margin be AFTER skipping y sessions?
        # New remaining is R - y, new conducted is T + y, attended is A
        remaining_after = R - y
        conducted_after = T + y
        safe_remaining_after = cls.calculate_max_safe_absences(
            attended=A,
            conducted=conducted_after,
            remaining=remaining_after,
            threshold_fraction=threshold_frac,
        )

        risk_after = cls.determine_risk_category(
            current_pct=projected_pct,
            safe_absences=safe_remaining_after,
            attended=A,
            conducted=conducted_after,
            remaining=remaining_after,
            threshold_pct=threshold,
        )

        is_safe = projected_pct >= threshold

        if is_safe:
            explanation = (
                f"If you miss {y} session(s), your projected attendance will be {projected_pct}%. "
                f"You will still be above the {threshold}% threshold with {safe_remaining_after} safe absences remaining."
            )
        else:
            explanation = (
                f"Warning: Missing {y} session(s) will drop your projected attendance to {projected_pct}%, "
                f"which falls below the required {threshold}% threshold."
            )

        return SimulateAbsenceResponse(
            current_percentage=current_pct,
            projected_percentage=projected_pct,
            threshold_percentage=threshold,
            sessions_missed_in_sim=y,
            safe_absences_remaining_after=safe_remaining_after,
            risk_category_after=risk_after,
            is_safe=is_safe,
            explanation=explanation,
        )

    @classmethod
    def calculate_recovery_plan(cls, req: AttendanceRecoveryRequest) -> AttendanceRecoveryResponse:
        """
        Calculates how many consecutive classes the student must attend to reach the target threshold.

        Mathematical Derivation:
            (A + k) / (T + k) >= p
            A + k >= p*T + p*k
            k * (1 - p) >= p*T - A
            k = ceil((p*T - A) / (1 - p))
        """
        A = req.classes_attended
        T = req.classes_conducted
        R = req.remaining_planned_sessions
        p = req.target_threshold / 100.0

        current_pct = cls.calculate_current_percentage(A, T)

        # If already at or above target threshold
        if current_pct >= req.target_threshold:
            return AttendanceRecoveryResponse(
                current_percentage=current_pct,
                target_threshold=req.target_threshold,
                classes_needed_consecutively=0,
                remaining_sessions_available=R,
                is_recoverable=True,
                max_possible_percentage=round(((A + R) / (T + R) * 100.0), 2) if (T + R) > 0 else 100.0,
                explanation=f"You are already at {current_pct}%, which satisfies the {req.target_threshold}% requirement.",
            )

        # Edge case: If threshold is 100% and student already missed a class (A < T)
        if p >= 1.0:
            return AttendanceRecoveryResponse(
                current_percentage=current_pct,
                target_threshold=req.target_threshold,
                classes_needed_consecutively=-1,
                remaining_sessions_available=R,
                is_recoverable=False,
                max_possible_percentage=round(((A + R) / (T + R) * 100.0), 2) if (T + R) > 0 else 100.0,
                explanation="100% attendance cannot be achieved because classes have already been missed.",
            )

        # Standard recovery formula
        numerator = (p * T) - A
        denominator = 1.0 - p
        k_needed = math.ceil(numerator / denominator)

        total_sessions = T + R
        max_possible_pct = round(((A + R) / total_sessions * 100.0), 2) if total_sessions > 0 else 100.0
        is_recoverable = (R >= k_needed) and (max_possible_pct >= req.target_threshold)

        if is_recoverable:
            explanation = (
                f"To recover to {req.target_threshold}%, you must attend the next {k_needed} classes consecutively. "
                f"You have {R} sessions remaining in the semester, so this is achievable."
            )
        else:
            explanation = (
                f"Attendance is mathematically unrecoverable. You need {k_needed} consecutive classes, "
                f"but only {R} sessions remain. Even with 100% attendance from now on, your maximum possible attendance will be {max_possible_pct}%."
            )

        return AttendanceRecoveryResponse(
            current_percentage=current_pct,
            target_threshold=req.target_threshold,
            classes_needed_consecutively=k_needed,
            remaining_sessions_available=R,
            is_recoverable=is_recoverable,
            max_possible_percentage=max_possible_pct,
            explanation=explanation,
        )
