"""
GPA Deterministic Calculation Service
Pure Python domain logic for credit-weighted SGPA, cumulative CGPA,
and target future SGPA requirement planning.
"""

from typing import List, Dict, Optional
from apps.api.src.schemas.gpa_schemas import (
    DEFAULT_GRADE_SCALE,
    CourseGradeInput,
    SGPACalculationRequest,
    SGPASummary,
    CGPACalculationRequest,
    CGPASummary,
    TargetCGPARequest,
    TargetCGPAResponse,
)


class GPAService:
    """
    Deterministic domain service for SGPA and CGPA arithmetic.
    Complies with standard credit-based semester grading ordinances (UGC/AICTE).
    """

    @staticmethod
    def resolve_grade_point(
        grade_point: Optional[float],
        grade_letter: Optional[str],
        grade_scale: Dict[str, float] = DEFAULT_GRADE_SCALE,
    ) -> float:
        """
        Resolves numerical grade point from either direct point or letter grade.
        """
        if grade_point is not None:
            return float(grade_point)

        if grade_letter:
            upper_letter = grade_letter.strip().upper()
            if upper_letter in grade_scale:
                return grade_scale[upper_letter]
            raise ValueError(f"Unrecognized letter grade: '{grade_letter}'. Supported: {list(grade_scale.keys())}")

        raise ValueError("Either grade_point or grade_letter must be provided")

    @classmethod
    def calculate_sgpa(cls, req: SGPACalculationRequest) -> SGPASummary:
        """
        Calculates credit-weighted Semester Grade Point Average (SGPA).

        Formula:
            SGPA = sum(credits * grade_point) / sum(credits)
        """
        scale = req.custom_grade_scale or DEFAULT_GRADE_SCALE
        total_credits = 0.0
        total_grade_points = 0.0
        breakdown: List[Dict[str, float | str]] = []

        for course in req.courses:
            gp = cls.resolve_grade_point(course.grade_point, course.grade_letter, scale)
            course_points = course.credits * gp

            total_credits += course.credits
            total_grade_points += course_points

            breakdown.append({
                "course_code": course.course_code,
                "course_name": course.course_name,
                "credits": course.credits,
                "grade_point": gp,
                "earned_points": round(course_points, 2),
            })

        if total_credits <= 0:
            raise ValueError("Total semester credits must be greater than zero")

        sgpa = round(total_grade_points / total_credits, 2)

        return SGPASummary(
            total_credits=round(total_credits, 2),
            total_grade_points=round(total_grade_points, 2),
            sgpa=sgpa,
            course_count=len(req.courses),
            breakdown=breakdown,
        )

    @classmethod
    def calculate_cgpa(cls, req: CGPACalculationRequest) -> CGPASummary:
        """
        Calculates cumulative CGPA across completed semesters.

        Formula:
            CGPA = sum(semester_credits * semester_sgpa) / sum(semester_credits)
        """
        total_credits = 0.0
        cumulative_points = 0.0

        for sem in req.semesters:
            sem_points = sem.credits * sem.sgpa
            total_credits += sem.credits
            cumulative_points += sem_points

        if total_credits <= 0:
            raise ValueError("Total completed credits must be greater than zero")

        cgpa = round(cumulative_points / total_credits, 2)

        return CGPASummary(
            total_completed_credits=round(total_credits, 2),
            cumulative_grade_points=round(cumulative_points, 2),
            cgpa=cgpa,
            semesters_count=len(req.semesters),
        )

    @classmethod
    def solve_target_cgpa(cls, req: TargetCGPARequest) -> TargetCGPAResponse:
        """
        Solves for required average SGPA across remaining semesters to reach target CGPA.

        Formula:
            Required Future Average = [G * (Ec + Er) - C * Ec] / Er
        Where:
            G = Target CGPA
            C = Current CGPA
            Ec = Completed Credits
            Er = Remaining Credits
            M = Max Grade Scale (typically 10.0)
        """
        C = req.current_cgpa
        Ec = req.completed_credits
        Er = req.remaining_credits
        G = req.target_cgpa
        M = req.max_scale

        if Er <= 0:
            raise ValueError("Remaining credits must be strictly positive to plan future GPA")

        total_credits = Ec + Er
        total_target_points = G * total_credits
        current_earned_points = C * Ec
        needed_future_points = total_target_points - current_earned_points

        raw_required_sgpa = needed_future_points / Er
        required_sgpa = round(raw_required_sgpa, 2)

        # Theoretical maximum CGPA if student scores a perfect M (10.0) in all remaining credits
        max_possible_points = current_earned_points + (M * Er)
        max_possible_cgpa = round(max_possible_points / total_credits, 2)

        # Feasibility bounds
        is_achievable = required_sgpa <= M

        if not is_achievable:
            explanation = (
                f"Target Infeasible: To achieve a {G} CGPA, you would need an average SGPA of {required_sgpa} "
                f"across your remaining {Er} credits, which exceeds the maximum possible scale of {M}.0. "
                f"The highest CGPA you can possibly achieve (with perfect {M}.0 in all remaining credits) is {max_possible_cgpa}."
            )
        elif required_sgpa <= 0:
            explanation = (
                f"Goal already secured: Your current CGPA of {C} across {Ec} credits guarantees you will stay "
                f"above {G} CGPA as long as you pass all remaining {Er} credits."
            )
        else:
            explanation = (
                f"To reach your target CGPA of {G}, you need to maintain an average SGPA of {required_sgpa} "
                f"across your remaining {Er} credits. (Your theoretical ceiling is {max_possible_cgpa})."
            )

        return TargetCGPAResponse(
            current_cgpa=C,
            target_cgpa=G,
            completed_credits=Ec,
            remaining_credits=Er,
            required_future_sgpa=max(0.0, required_sgpa),
            is_achievable=is_achievable,
            max_possible_cgpa=max_possible_cgpa,
            explanation=explanation,
        )
