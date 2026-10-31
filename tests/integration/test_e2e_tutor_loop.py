"""End-to-End System Integration & Verification: 5-step Adaptive Tutor Loop."""

from fastapi.testclient import TestClient
from deeptutor.api.app import app

client = TestClient(app)


def test_full_adaptive_exam_prep_cycle():
    # 1. Diagnostic test establishes baseline P(L)
    diag = client.post("/api/diagnostic/start", json={"syllabus": "class10_physics"}).json()
    q_diag = diag["questions"][0]
    client.post(
        f"/api/diagnostic/{diag['session_id']}/submit",
        json={"answers": {q_diag["question_id"]: {"answer": "wrong", "reasoning": "guessed"}}},
    )

    # 2. Next question generated targets detected weak concept in ZPD
    next_q = client.post("/api/learning/next-question", json={"student_id": "std_1"}).json()
    assert next_q["concept_id"] in ["c_electric_current", "c_potential_difference"]
    assert next_q["difficulty"] in ["conceptual_1", "application_2"]

    # 3. Student answers with reasoning containing known misconception
    ans_resp = client.post(
        "/api/learning/submit-answer",
        json={
            "student_id": "std_1",
            "question_id": next_q["question_id"],
            "answer": "Resistance doubles",
            "reasoning": "R = V / I so if V doubles R doubles",
        },
    ).json()
    assert ans_resp["misconception_detected"] is True
    assert "ohm" in ans_resp["misconception_id"]

    # 4. BKT mastery updates deterministically
    assert ans_resp["bkt_mastery"] < 0.35

    # 5. Teacher dashboard aggregates this student's gap into cohort view
    teacher_summary = client.get("/api/teacher/cohorts/class-10-a/summary").json()
    assert any(gap["concept_id"] == next_q["concept_id"] for gap in teacher_summary["top_gaps"])


def test_sound_reasoning_increases_mastery():
    # Student with prerequisites mastered gets Ohm's Law question
    from deeptutor.services.cohort.service import get_cohort_service

    cohort_service = get_cohort_service()
    cohort_service.get_or_create_student(
        "std_sound",
        default_mastery={
            "c_electric_charge": 0.90,
            "c_electric_current": 0.85,
            "c_potential_difference": 0.85,
            "c_ohms_law": 0.30,
        },
    )
    next_q = client.post("/api/learning/next-question", json={"student_id": "std_sound"}).json()
    assert next_q["concept_id"] == "c_ohms_law"
    assert next_q["difficulty"] == "conceptual_1"

    ans_resp = client.post(
        "/api/learning/submit-answer",
        json={
            "student_id": "std_sound",
            "question_id": next_q["question_id"],
            "answer": "Remains constant",
            "reasoning": "Resistance depends on resistivity, length, and cross-sectional area, not on V or I.",
        },
    ).json()

    assert ans_resp["is_correct"] is True
    assert ans_resp["reasoning_valid"] is True
    assert ans_resp["misconception_detected"] is False
    assert ans_resp["misconception_id"] is None
    # Prior was ~0.30, sound correct update brings it to > 0.65
    assert ans_resp["bkt_mastery"] > 0.65


def test_lucky_guess_with_flawed_reasoning():
    # Student guesses correct answer but reasoning contains active misconception
    from deeptutor.services.cohort.service import get_cohort_service

    cohort_service = get_cohort_service()
    cohort_service.get_or_create_student(
        "std_guess",
        default_mastery={
            "c_electric_charge": 0.90,
            "c_electric_current": 0.85,
            "c_potential_difference": 0.85,
            "c_ohms_law": 0.30,
        },
    )
    next_q = client.post("/api/learning/next-question", json={"student_id": "std_guess"}).json()
    assert next_q["concept_id"] == "c_ohms_law"

    ans_resp = client.post(
        "/api/learning/submit-answer",
        json={
            "student_id": "std_guess",
            "question_id": next_q["question_id"],
            "answer": "Remains constant",
            "reasoning": "Because V cancels out current completely to zero.",
        },
    ).json()

    assert ans_resp["is_correct"] is True
    assert ans_resp["reasoning_valid"] is False
    assert ans_resp["misconception_detected"] is True
    assert ans_resp["misconception_id"] is not None
    # Because reasoning was flawed, BKT updates as unlearned/incorrect (< 0.25)
    assert ans_resp["bkt_mastery"] < 0.25


def test_cohort_heatmap_reflects_student_progress():
    # Check that students who submitted answers are tracked in the cohort heatmap
    heatmap = client.get("/api/teacher/cohorts/class-10-a/heatmap").json()
    student_ids = {s["student_id"] for s in heatmap["students"]}
    assert "std_1" in student_ids
    assert "std_sound" in student_ids
    assert "std_1" in heatmap["matrix"]
    assert "c_electric_current" in heatmap["matrix"]["std_1"]

