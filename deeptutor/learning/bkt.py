"""Bayesian Knowledge Tracing (BKT) learner model.

Standard 4-parameter BKT:
- p_l0: Prior probability of mastery before any interaction
- p_t: Probability of transitioning from unmastered to mastered state (learning rate)
- p_s: Probability of slipping (making a mistake despite being in mastered state)
- p_g: Probability of guessing correctly (correct response despite being unmastered)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from deeptutor.learning.models import QuizAttempt


@dataclass
class BKTParameters:
    """Parameters for Bayesian Knowledge Tracing."""

    p_l0: float = 0.20  # prior mastery probability
    p_t: float = 0.15  # transition / learning probability
    p_s: float = 0.10  # slip probability
    p_g: float = 0.20  # guess probability


_DEFAULT_PARAMS = BKTParameters()


def update_bkt(
    p_l_prev: float,
    is_correct: bool | float,
    params: BKTParameters | None = None,
) -> float:
    """Calculate Bayesian posterior on observation, then apply learning transition.

    Clamps output strictly to [0.0001, 0.9999].
    """
    if params is None:
        params = _DEFAULT_PARAMS

    p_l = max(0.0001, min(0.9999, float(p_l_prev)))
    p_s = params.p_s
    p_g = params.p_g
    p_t = params.p_t

    # Posterior if correct
    num_corr = p_l * (1.0 - p_s)
    den_corr = num_corr + (1.0 - p_l) * p_g
    p_corr = num_corr / den_corr if den_corr > 0.0 else p_l

    # Posterior if incorrect
    num_inc = p_l * p_s
    den_inc = num_inc + (1.0 - p_l) * (1.0 - p_g)
    p_inc = num_inc / den_inc if den_inc > 0.0 else p_l

    if isinstance(is_correct, bool):
        p_obs = p_corr if is_correct else p_inc
    else:
        weight = max(0.0, min(1.0, float(is_correct)))
        p_obs = weight * p_corr + (1.0 - weight) * p_inc

    # Transition / learning step
    p_next = p_obs + (1.0 - p_obs) * p_t
    return max(0.0001, min(0.9999, p_next))


def compute_bkt_mastery(
    correctness_sequence: list[bool | float],
    params: BKTParameters | None = None,
) -> float:
    """Replay chronological sequence of attempt outcomes starting from p_l0.

    If sequence is empty, returns 0.0.
    """
    if not correctness_sequence:
        return 0.0

    if params is None:
        params = _DEFAULT_PARAMS

    p_l = params.p_l0
    for outcome in correctness_sequence:
        p_l = update_bkt(p_l, outcome, params=params)
    return p_l


def calculate_concept_mastery(
    attempts: list[QuizAttempt] | list[Any],
    params: BKTParameters | None = None,
) -> float:
    """Calculate BKT mastery from a sequence of QuizAttempt objects."""
    correctness = [
        0.5 if getattr(a, "result", None) == "partial" else getattr(a, "is_correct", False)
        for a in attempts
        if not getattr(a, "voided", False) and getattr(a, "independent", True)
    ]
    return compute_bkt_mastery(correctness, params=params)


__all__ = [
    "BKTParameters",
    "calculate_concept_mastery",
    "compute_bkt_mastery",
    "update_bkt",
]
