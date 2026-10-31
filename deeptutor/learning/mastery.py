"""Mastery scoring policy — intentionally simple and swappable.

``compute_mastery`` maps a knowledge point's attempt history to a 0..1 mastery
score. The current policy is a recency-weighted accuracy with a low-confidence
cap: a single lucky answer cannot "master" a point — mastery is capped until
there is enough evidence.

This is the one place the pedagogy math lives. To plug in a richer model
(e.g. an IRT/BKT estimate or a tuned spec), replace ``compute_mastery`` alone;
callers (`LearningService.calculate_mastery`) need not change.
"""

from __future__ import annotations

from deeptutor.learning.bkt import BKTParameters, compute_bkt_mastery


def compute_mastery(
    correctness: list[bool | float],
    params: BKTParameters | None = None,
) -> float:
    """Return a 0..1 mastery score from a knowledge point's attempt outcomes using BKT.

    Args:
        correctness: per-attempt correctness or bounded partial credit, chronologically.
        params: optional BKT parameters (prior, transition, slip, guess).
    """
    return compute_bkt_mastery(correctness, params=params)


__all__ = ["compute_bkt_mastery", "compute_mastery"]
