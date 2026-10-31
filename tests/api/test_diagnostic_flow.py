from fastapi.testclient import TestClient
from deeptutor.api.app import app

client = TestClient(app)


def test_diagnostic_lifecycle():
    # 1. Start diagnostic
    resp = client.post("/api/diagnostic/start", json={"syllabus": "class10_physics"})
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]
    assert len(data["questions"]) == 6
    assert data["status"] == "in_progress"

    # 2. Submit answers
    answers = {
        q["question_id"]: {"answer": q["expected_answer"], "reasoning": "Standard derivation"}
        for q in data["questions"][:3]
    }
    # Other 3 wrong
    for q in data["questions"][3:]:
        answers[q["question_id"]] = {"answer": "wrong", "reasoning": "incorrect guess"}

    sub_resp = client.post(f"/api/diagnostic/{session_id}/submit", json={"answers": answers})
    assert sub_resp.status_code == 200
    result = sub_resp.json()
    assert result["status"] == "completed"
    assert "concept_mastery" in result
    # Mastered concepts should have P(L) > 0.6, unmastered P(L) < 0.25
    assert result["concept_mastery"]["c_electric_current"] > 0.5

    # 3. Get report
    report_resp = client.get(f"/api/diagnostic/{session_id}/report")
    assert report_resp.status_code == 200
    report = report_resp.json()
    assert report["session_id"] == session_id
    assert report["status"] == "completed"
    assert "concept_mastery" in report
    assert report["score"] == 0.5


def test_diagnostic_not_found():
    resp = client.get("/api/diagnostic/nonexistent_session_id/report")
    assert resp.status_code == 404

    submit_resp = client.post(
        "/api/diagnostic/nonexistent_session_id/submit",
        json={"answers": {}},
    )
    assert submit_resp.status_code == 404
