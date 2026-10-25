"""
Unit Tests for GPA Deterministic Service
Verifies 100% mathematical accuracy of credit-weighted SGPA, CGPA,
and target future SGPA requirement planning.
"""

import pytest
from apps.api.src.schemas.gpa_schemas import (
    CourseGradeInput,
    SGPACalculationRequest,
    SemesterProgress,
    CGPACalculationRequest,
    TargetCGPARequest,
)
from apps.api.src.services.gpa_service import GPAService


class TestSGPACalculations:
    def test_standard_semester_sgpa(self):
        """
        Courses:
            DBMS: 4 credits, Grade O (10.0) -> 40 points
            OS: 4 credits, Grade A+ (9.0) -> 36 points
            CN: 3 credits, Grade A (8.0) -> 24 points
            OS Lab: 1.5 credits, Grade O (10.0) -> 15 points
        Total Credits = 4 + 4 + 3 + 1.5 = 12.5
        Total Points = 40 + 36 + 24 + 15 = 115.0
        Expected SGPA = 115.0 / 12.5 = 9.20
        """
        courses = [
            CourseGradeInput(course_code="CS501", course_name="DBMS", credits=4.0, grade_letter="O"),
            CourseGradeInput(course_code="CS502", course_name="OS", credits=4.0, grade_letter="A+"),
            CourseGradeInput(course_code="CS503", course_name="CN", credits=3.0, grade_letter="A"),
            CourseGradeInput(course_code="CS504", course_name="OS Lab", credits=1.5, grade_letter="O"),
        ]
        req = SGPACalculationRequest(courses=courses)
        summary = GPAService.calculate_sgpa(req)

        assert summary.total_credits == 12.5
        assert summary.total_grade_points == 115.0
        assert summary.sgpa == 9.20
        assert summary.course_count == 4

    def test_direct_grade_points_input(self):
        courses = [
            CourseGradeInput(course_code="MTH101", course_name="Maths", credits=4.0, grade_point=7.5),
            CourseGradeInput(course_code="PHY101", course_name="Physics", credits=4.0, grade_point=8.5),
        ]
        summary = GPAService.calculate_sgpa(SGPACalculationRequest(courses=courses))
        assert summary.sgpa == 8.00


class TestCGPACalculations:
    def test_multi_semester_cgpa(self):
        """
        Sem 1: 20 credits, SGPA = 8.0 -> 160 points
        Sem 2: 22 credits, SGPA = 8.5 -> 187 points
        Sem 3: 20 credits, SGPA = 9.0 -> 180 points
        Total Credits = 62
        Total Points = 527.0
        CGPA = 527.0 / 62 = 8.50
        """
        semesters = [
            SemesterProgress(semester_number=1, credits=20.0, sgpa=8.0),
            SemesterProgress(semester_number=2, credits=22.0, sgpa=8.5),
            SemesterProgress(semester_number=3, credits=20.0, sgpa=9.0),
        ]
        summary = GPAService.calculate_cgpa(CGPACalculationRequest(semesters=semesters))
        assert summary.total_completed_credits == 62.0
        assert summary.cgpa == 8.50
        assert summary.semesters_count == 3


class TestTargetCGPASolver:
    def test_achievable_target(self):
        """
        Current CGPA (C) = 8.0
        Completed Credits (Ec) = 60
        Remaining Credits (Er) = 40
        Target CGPA (G) = 8.5
        Calculation:
            Points needed = 8.5 * 100 - 8.0 * 60 = 850 - 480 = 370
            Required Future SGPA = 370 / 40 = 9.25
        """
        req = TargetCGPARequest(
            current_cgpa=8.0,
            completed_credits=60.0,
            remaining_credits=40.0,
            target_cgpa=8.5,
        )
        resp = GPAService.solve_target_cgpa(req)

        assert resp.is_achievable is True
        assert resp.required_future_sgpa == 9.25
        assert resp.max_possible_cgpa == round((480 + 10.0 * 40) / 100, 2)  # 8.80

    def test_infeasible_target_and_ceiling_calculation(self):
        """
        Student has 6.0 CGPA after 80 credits. Only 20 credits remain. Target = 8.5.
        Calculation:
            Points needed = 8.5 * 100 - 6.0 * 80 = 850 - 480 = 370
            Required SGPA = 370 / 20 = 18.5 (Impossible!)
            Max possible CGPA with perfect 10 in all 20 remaining:
            (480 + 200) / 100 = 6.80
        """
        req = TargetCGPARequest(
            current_cgpa=6.0,
            completed_credits=80.0,
            remaining_credits=20.0,
            target_cgpa=8.5,
        )
        resp = GPAService.solve_target_cgpa(req)

        assert resp.is_achievable is False
        assert resp.required_future_sgpa == 18.5
        assert resp.max_possible_cgpa == 6.80
        assert "target infeasible" in resp.explanation.lower()

    def test_already_secured_target(self):
        """
        Current CGPA = 9.0 after 80 credits. 20 credits left. Target = 7.0.
        Student has already secured target.
        """
        req = TargetCGPARequest(
            current_cgpa=9.0,
            completed_credits=80.0,
            remaining_credits=20.0,
            target_cgpa=7.0,
        )
        resp = GPAService.solve_target_cgpa(req)

        assert resp.is_achievable is True
        assert resp.required_future_sgpa == 0.0
        assert "already secured" in resp.explanation.lower()


class TestGPAEdgeCasesAndCustomScales:
    def test_custom_grading_scale(self):
        # Suppose a college uses A=10, B=8, C=6
        custom_scale = {"A": 10.0, "B": 8.0, "C": 6.0}
        courses = [
            CourseGradeInput(course_code="C1", course_name="Subject 1", credits=3.0, grade_letter="B"),
        ]
        req = SGPACalculationRequest(courses=courses, custom_grade_scale=custom_scale)
        summary = GPAService.calculate_sgpa(req)
        assert summary.sgpa == 8.00

    def test_unrecognized_letter_grade_raises_error(self):
        courses = [
            CourseGradeInput(course_code="C1", course_name="Subject 1", credits=3.0, grade_letter="Z"),
        ]
        with pytest.raises(ValueError, match="Unrecognized letter grade"):
            GPAService.calculate_sgpa(SGPACalculationRequest(courses=courses))

    def test_remaining_credits_zero_raises_error(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError, match="Input should be greater than 0"):
            TargetCGPARequest(
                current_cgpa=8.0,
                completed_credits=100.0,
                remaining_credits=0.0,
                target_cgpa=8.5,
            )

