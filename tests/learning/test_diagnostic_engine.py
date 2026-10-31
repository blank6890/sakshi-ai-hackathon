import pytest
from deeptutor.learning.diagnostic import (
    DiagnosticEngine,
    DiagnosticSession,
    CLASS10_PHYSICS_MILESTONES,
    get_diagnostic_engine,
)


def test_milestone_questions_structure():
    assert len(CLASS10_PHYSICS_MILESTONES) == 6
    for q in CLASS10_PHYSICS_MILESTONES:
        assert "question_id" in q
        assert "concept_id" in q
        assert "prompt" in q
        assert "expected_answer" in q
        assert "chapter" in q


def test_create_session():
    engine = DiagnosticEngine()
    session = engine.create_session("class10_physics")
    assert isinstance(session, DiagnosticSession)
    assert session.status == "in_progress"
    assert len(session.questions) == 6
    assert session.session_id.startswith("diag_")
    assert engine.get_session(session.session_id) is session


def test_submit_all_correct():
    engine = DiagnosticEngine()
    session = engine.create_session("class10_physics")
    answers = {
        q["question_id"]: {"answer": q["expected_answer"]}
        for q in session.questions
    }
    result = engine.submit_answers(session.session_id, answers)
    assert result["status"] == "completed"
    assert result["score"] == 1.0
    # All tested concepts should have P(L) >= 0.6
    for q in session.questions:
        cid = q["concept_id"]
        assert result["concept_mastery"][cid] >= 0.6


def test_submit_all_incorrect():
    engine = DiagnosticEngine()
    session = engine.create_session("class10_physics")
    answers = {
        q["question_id"]: {"answer": "totally wrong answer"}
        for q in session.questions
    }
    result = engine.submit_answers(session.session_id, answers)
    assert result["status"] == "completed"
    assert result["score"] == 0.0
    # Tested concepts should have P(L) < 0.25
    for q in session.questions:
        cid = q["concept_id"]
        assert result["concept_mastery"][cid] < 0.25


def test_session_not_found():
    engine = DiagnosticEngine()
    with pytest.raises(KeyError):
        engine.submit_answers("unknown_id", {})
    with pytest.raises(KeyError):
        engine.get_report("unknown_id")


def test_get_report():
    engine = DiagnosticEngine()
    session = engine.create_session("class10_physics")
    # Submit first 3 correct, last 3 wrong
    answers = {
        q["question_id"]: {"answer": q["expected_answer"]}
        for q in session.questions[:3]
    }
    for q in session.questions[3:]:
        answers[q["question_id"]] = {"answer": "wrong"}

    engine.submit_answers(session.session_id, answers)
    report = engine.get_report(session.session_id)
    assert report["session_id"] == session.session_id
    assert report["status"] == "completed"
    assert report["score"] == 0.5
    assert len(report["concept_mastery"]) == 15
    assert "recommendations" in report
    assert isinstance(report["recommendations"], list)
