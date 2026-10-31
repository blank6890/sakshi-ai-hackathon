import time
import pytest
from deeptutor.learning.scheduler import SpacedRepetitionScheduler
from deeptutor.learning.models import KnowledgeType, RepetitionState, LearningEvidence, LearningProgress


def test_exam_horizon_interval_compression():
    scheduler = SpacedRepetitionScheduler()
    state = scheduler.get_initial_state(KnowledgeType.CONCEPT)
    evidence = LearningEvidence(knowledge_point_id="c_ohms_law", result="correct", quality=1.0)

    # 1. Normal review without exam pressure: interval is 3-7 days
    normal_state = scheduler.schedule_review(state, KnowledgeType.CONCEPT, evidence)
    normal_interval = normal_state.next_review_at - time.time()

    # 2. Exam in 2 days: interval must be compressed to fall BEFORE the exam
    exam_timestamp = time.time() + 2 * 86400
    state2 = scheduler.get_initial_state(KnowledgeType.CONCEPT)
    compressed_state = scheduler.schedule_exam_paced_review(
        state2, KnowledgeType.CONCEPT, evidence, exam_date=exam_timestamp
    )
    compressed_interval = compressed_state.next_review_at - time.time()

    assert compressed_interval < normal_interval
    assert compressed_state.next_review_at < exam_timestamp


def test_exam_horizon_deterministic_math():
    scheduler = SpacedRepetitionScheduler()
    now = 1700000000.0
    evidence = LearningEvidence(knowledge_point_id="c_ohms_law", result="correct", quality=1.0, timestamp=now)

    # Base review
    state_base = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    normal_state = scheduler.schedule_review(state_base, KnowledgeType.CONCEPT, evidence, now=now)
    base_interval = normal_state.next_review_at - now

    # 7 days to exam: kappa = max(0.2, 7/14) = 0.5
    exam_7d = now + 7 * 86400.0
    state_7d = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    res_7d = scheduler.schedule_exam_paced_review(state_7d, KnowledgeType.CONCEPT, evidence, exam_date=exam_7d, now=now)
    expected_interval_7d = base_interval * 0.5
    assert pytest.approx(res_7d.next_review_at - now, rel=1e-5) == expected_interval_7d
    assert res_7d.next_review_at <= exam_7d - 0.5 * 86400.0


def test_exam_cutoff_enforces_12_hours_before_exam():
    scheduler = SpacedRepetitionScheduler()
    now = 1700000000.0
    evidence = LearningEvidence(knowledge_point_id="c_ohms_law", result="correct", quality=1.0, timestamp=now)

    # Exam in 1 day (24 hours). 0.5 days (12 hours) cutoff is now + 12 hours = now + 43200
    exam_1d = now + 1.0 * 86400.0
    state = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    res = scheduler.schedule_exam_paced_review(state, KnowledgeType.CONCEPT, evidence, exam_date=exam_1d, now=now)

    # Must be at or before 12 hours before exam
    assert res.next_review_at <= exam_1d - 0.5 * 86400.0


def test_exam_in_past_or_today_clamps():
    scheduler = SpacedRepetitionScheduler()
    now = 1700000000.0
    evidence = LearningEvidence(knowledge_point_id="c_ohms_law", result="correct", quality=1.0, timestamp=now)

    # 1. Exam in the past (e.g., 2 days ago)
    exam_past = now - 2 * 86400.0
    state_past = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    res_past = scheduler.schedule_exam_paced_review(
        state_past, KnowledgeType.CONCEPT, evidence, exam_date=exam_past, now=now
    )
    assert res_past.next_review_at == now + 3600.0

    # 2. Exam right now (today, delta_exam == 0)
    state_today = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    res_today = scheduler.schedule_exam_paced_review(
        state_today, KnowledgeType.CONCEPT, evidence, exam_date=now, now=now
    )
    assert res_today.next_review_at == now + 3600.0


def test_no_exam_date_preserves_normal_scheduling():
    scheduler = SpacedRepetitionScheduler()
    now = 1700000000.0
    evidence = LearningEvidence(knowledge_point_id="c_ohms_law", result="correct", quality=1.0, timestamp=now)

    state1 = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    normal_state = scheduler.schedule_review(state1, KnowledgeType.CONCEPT, evidence, now=now)

    state2 = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    paced_state = scheduler.schedule_exam_paced_review(
        state2, KnowledgeType.CONCEPT, evidence, exam_date=None, now=now
    )
    assert normal_state.next_review_at == paced_state.next_review_at


def test_exam_beyond_14_days_no_compression():
    scheduler = SpacedRepetitionScheduler()
    now = 1700000000.0
    evidence = LearningEvidence(knowledge_point_id="c_ohms_law", result="correct", quality=1.0, timestamp=now)

    state1 = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    normal_state = scheduler.schedule_review(state1, KnowledgeType.CONCEPT, evidence, now=now)

    # Exam in 20 days: delta_exam > 14
    exam_20d = now + 20 * 86400.0
    state2 = scheduler.get_initial_state(KnowledgeType.CONCEPT, now=now)
    paced_state = scheduler.schedule_exam_paced_review(
        state2, KnowledgeType.CONCEPT, evidence, exam_date=exam_20d, now=now
    )
    assert normal_state.next_review_at == paced_state.next_review_at


def test_learning_progress_target_exam_date_field():
    progress = LearningProgress(book_id="physics_10")
    assert progress.target_exam_date is None

    exam_time = 1710000000.0
    progress_with_exam = LearningProgress(book_id="physics_10", target_exam_date=exam_time)
    assert progress_with_exam.target_exam_date == exam_time
