"""Deterministic answer grading + coarse error classification for Mastery Path."""

from __future__ import annotations

from difflib import SequenceMatcher
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deeptutor.learning.models import ErrorType


def grade_answer(user_answer: str, expected_answer: str, question_type: str = "short") -> bool:
    """Grade user answer against expected answer.

    Args:
        user_answer: The user's submitted answer.
        expected_answer: The stored expected answer.
        question_type: One of "choice", "short", "open".

    Returns:
        True if answer is correct.
    """
    user = user_answer.strip().lower()
    expected = expected_answer.strip().lower()

    if not expected:
        return False

    if question_type == "choice":
        user_norm = user.replace(" ", "")
        expected_norm = expected.replace(" ", "")
        return user_norm == expected_norm

    if question_type == "short":
        if user == expected:
            return True
        if len(expected) <= 30:
            return SequenceMatcher(None, user, expected).ratio() >= 0.85
        return False

    if question_type == "open":
        keywords = [k.strip() for k in re.split(r"[,;，；。\n]+", expected) if k.strip()]
        if not keywords:
            return False
        matched = sum(1 for kw in keywords if kw in user)
        return matched / len(keywords) >= 0.6

    return False


def classify_error(
    user_answer: str,
    user_reasoning: str = "",
    concept_id: str = "",
    expected_answer: str = "",
) -> ErrorType:
    """Classify error type for a learner response.

    A blank answer signals the student did not know (metacognitive).
    If an active misconception is detected in reasoning or answer, it is classified
    as understanding deviation. Otherwise it is treated as a wrong application.
    """
    from deeptutor.learning.models import ErrorType

    if not user_answer.strip():
        return ErrorType.METACOGNITIVE

    if user_reasoning or concept_id:
        from deeptutor.learning.misconception import analyze_reasoning_and_misconceptions

        analysis = analyze_reasoning_and_misconceptions(
            concept_id=concept_id,
            question="",
            expected_answer=expected_answer,
            student_answer=user_answer,
            student_reasoning=user_reasoning,
        )
        if analysis.misconception_id is not None:
            return ErrorType.UNDERSTANDING_DEVIATION

    return ErrorType.APPLICATION_ERROR


def diagnose_error(
    user_answer: str,
    user_reasoning: str = "",
    concept_id: str = "",
    expected_answer: str = "",
    question: str = "",
) -> tuple[ErrorType, str, str | None]:
    """Diagnose error type, ai_confirmation message, and misconception_id.

    Returns:
        tuple of (error_type, ai_confirmation, misconception_id)
    """
    from deeptutor.learning.models import ErrorType
    from deeptutor.learning.misconception import analyze_reasoning_and_misconceptions

    if not user_answer.strip():
        return ErrorType.METACOGNITIVE, "No answer provided.", None

    analysis = analyze_reasoning_and_misconceptions(
        concept_id=concept_id,
        question=question,
        expected_answer=expected_answer,
        student_answer=user_answer,
        student_reasoning=user_reasoning,
    )
    if analysis.misconception_id is not None:
        return (
            ErrorType.UNDERSTANDING_DEVIATION,
            analysis.remedial_feedback,
            analysis.misconception_id,
        )

    return (
        ErrorType.APPLICATION_ERROR,
        "Calculation or application error.",
        None,
    )


def create_error_record(
    question_id: str,
    knowledge_point_id: str,
    module_id: str,
    user_answer: str,
    user_reasoning: str = "",
    expected_answer: str = "",
    question: str = "",
    error_id: str | None = None,
):
    """Create an ErrorRecord with error_type and ai_confirmation inferred from misconception diagnosis."""
    import uuid
    from deeptutor.learning.models import ErrorRecord

    error_type, ai_confirmation, _ = diagnose_error(
        user_answer=user_answer,
        user_reasoning=user_reasoning,
        concept_id=knowledge_point_id,
        expected_answer=expected_answer,
        question=question,
    )
    return ErrorRecord(
        id=error_id or uuid.uuid4().hex,
        question_id=question_id,
        knowledge_point_id=knowledge_point_id,
        module_id=module_id,
        error_type=error_type,
        ai_confirmation=ai_confirmation,
        status="active",
    )


__all__ = ["grade_answer", "classify_error", "diagnose_error", "create_error_record"]
