import pytest
from deeptutor.learning.bkt import (
    BKTParameters,
    update_bkt,
    compute_bkt_mastery,
    calculate_concept_mastery,
)
from deeptutor.learning.mastery import compute_mastery
from deeptutor.learning.models import KnowledgePoint, KnowledgeType, LearningModule, LearningProgress, QuizAttempt
from deeptutor.learning.service import LearningService
from deeptutor.learning.storage import LearningStore


def test_bkt_update_on_correct():
    params = BKTParameters(p_l0=0.2, p_t=0.15, p_s=0.10, p_g=0.20)
    p_l1 = update_bkt(p_l_prev=0.2, is_correct=True, params=params)
    # P(L|correct) = (0.2 * 0.9) / (0.2 * 0.9 + 0.8 * 0.2) = 0.18 / (0.18 + 0.16) = 0.5294
    # P(L_next) = 0.5294 + (1 - 0.5294) * 0.15 = 0.60096
    assert 0.59 <= p_l1 <= 0.61


def test_bkt_update_on_incorrect():
    params = BKTParameters(p_l0=0.5, p_t=0.15, p_s=0.10, p_g=0.20)
    p_l1 = update_bkt(p_l_prev=0.5, is_correct=False, params=params)
    # P(L|incorrect) = (0.5 * 0.1) / (0.5 * 0.1 + 0.5 * 0.8) = 0.05 / (0.05 + 0.40) = 0.1111
    # P(L_next) = 0.1111 + (1 - 0.1111) * 0.15 = 0.2444
    assert p_l1 < 0.5
    assert 0.24 <= p_l1 <= 0.25


def test_bkt_streak_convergence():
    params = BKTParameters()
    p = 0.2
    for _ in range(5):
        p = update_bkt(p, is_correct=True, params=params)
    assert p > 0.95
    assert p <= 0.9999  # bounded


def test_bkt_wrong_streak_convergence():
    params = BKTParameters()
    p = 0.5
    for _ in range(10):
        p = update_bkt(p, is_correct=False, params=params)
    assert p >= 0.0001  # bounded lower clamp


def test_compute_bkt_mastery_empty():
    assert compute_bkt_mastery([]) == 0.0


def test_compute_bkt_mastery_sequence():
    params = BKTParameters(p_l0=0.2, p_t=0.15, p_s=0.10, p_g=0.20)
    seq = [True, True, False]
    # Replay manual step-by-step
    p = params.p_l0
    for outcome in seq:
        p = update_bkt(p, is_correct=outcome, params=params)
    mastery = compute_bkt_mastery(seq, params=params)
    assert pytest.approx(mastery, abs=1e-5) == p


def test_compute_bkt_mastery_partial_credit():
    # Partial credit 0.5 should be between incorrect and correct updates
    params = BKTParameters(p_l0=0.2, p_t=0.15, p_s=0.10, p_g=0.20)
    mastery_wrong = compute_bkt_mastery([0.0], params=params)
    mastery_partial = compute_bkt_mastery([0.5], params=params)
    mastery_correct = compute_bkt_mastery([1.0], params=params)
    assert mastery_wrong < mastery_partial < mastery_correct


def test_compute_mastery_backward_compatibility():
    # compute_mastery in mastery.py uses BKT
    res_empty = compute_mastery([])
    assert res_empty == 0.0
    res_correct = compute_mastery([True])
    assert 0.59 <= res_correct <= 0.61


def test_calculate_concept_mastery_with_quiz_attempts():
    attempts = [
        QuizAttempt(question_id="q1", knowledge_point_id="kp1", is_correct=True),
        QuizAttempt(question_id="q2", knowledge_point_id="kp1", is_correct=True),
        QuizAttempt(question_id="q3", knowledge_point_id="kp1", is_correct=False, voided=True),  # voided skipped
    ]
    mastery = calculate_concept_mastery(attempts)
    expected = compute_bkt_mastery([True, True])
    assert pytest.approx(mastery, abs=1e-5) == expected


def test_learning_service_calculate_mastery(tmp_path):
    store = LearningStore(root=tmp_path)
    service = LearningService(store)
    progress = LearningProgress(book_id="b1")
    progress.modules = [
        LearningModule(
            id="m1",
            name="M1",
            order=0,
            knowledge_points=[KnowledgePoint(id="kp1", name="KP1", type=KnowledgeType.CONCEPT, module_id="m1")],
        )
    ]
    progress.current_module_id = "m1"
    # No attempts -> 0.0
    assert service.calculate_mastery(progress, "kp1") == 0.0

    # 1 correct attempt -> BKT mastery ~0.60
    progress.quiz_attempts.append(
        QuizAttempt(question_id="q1", knowledge_point_id="kp1", is_correct=True)
    )
    mastery = service.calculate_mastery(progress, "kp1")
    assert 0.59 <= mastery <= 0.61
