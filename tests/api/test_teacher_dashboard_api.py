from fastapi.testclient import TestClient
from deeptutor.api.app import app

client = TestClient(app)


def test_teacher_cohort_gap_analysis():
    # Fetch class summary for demo cohort
    resp = client.get("/api/teacher/cohorts/class-10-a/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cohort_id"] == "class-10-a"
    assert data["total_students"] >= 5
    assert "class_average_mastery" in data
    assert 0.0 <= data["class_average_mastery"] <= 1.0

    # Verify class-wide gaps list
    assert len(data["top_gaps"]) >= 1
    worst_concept = data["top_gaps"][0]
    assert "concept_id" in worst_concept
    assert "concept_name" in worst_concept
    assert "average_mastery" in worst_concept
    assert "struggling_student_count" in worst_concept
    assert "struggling_percentage" in worst_concept
    assert "common_misconceptions" in worst_concept
    # Top gaps should be sorted ascending by average mastery
    for i in range(len(data["top_gaps"]) - 1):
        assert (
            data["top_gaps"][i]["average_mastery"]
            <= data["top_gaps"][i + 1]["average_mastery"]
        )

    # Verify frequent misconceptions list
    assert "frequent_misconceptions" in data
    assert len(data["frequent_misconceptions"]) >= 1
    top_misconception = data["frequent_misconceptions"][0]
    assert "misconception_id" in top_misconception
    assert "name" in top_misconception
    assert "count" in top_misconception
    assert "affected_students" in top_misconception


def test_teacher_cohort_heatmap():
    resp = client.get("/api/teacher/cohorts/class-10-a/heatmap")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cohort_id"] == "class-10-a"
    assert "students" in data
    assert "concepts" in data
    assert "matrix" in data

    assert len(data["students"]) >= 15
    student = data["students"][0]
    assert "student_id" in student
    assert "student_name" in student
    assert "overall_mastery" in student

    assert len(data["concepts"]) >= 10
    concept = data["concepts"][0]
    assert "concept_id" in concept
    assert "concept_name" in concept
    assert "chapter" in concept

    # Verify matrix structure: matrix[student_id][concept_id] -> float
    matrix = data["matrix"]
    first_student_id = student["student_id"]
    assert first_student_id in matrix
    first_concept_id = concept["concept_id"]
    assert first_concept_id in matrix[first_student_id]
    assert isinstance(matrix[first_student_id][first_concept_id], (float, int))


def test_teacher_cohort_gaps_endpoint():
    resp = client.get("/api/teacher/cohorts/class-10-a/gaps")
    assert resp.status_code == 200
    gaps = resp.json()
    assert isinstance(gaps, list)
    assert len(gaps) >= 1
    assert "concept_id" in gaps[0]
    assert "average_mastery" in gaps[0]
    # Verify sorted ascending by mastery
    for i in range(len(gaps) - 1):
        assert gaps[i]["average_mastery"] <= gaps[i + 1]["average_mastery"]


def test_teacher_list_cohorts():
    resp = client.get("/api/teacher/cohorts")
    assert resp.status_code == 200
    cohorts = resp.json()
    assert isinstance(cohorts, list)
    assert any(c["cohort_id"] == "class-10-a" for c in cohorts)


def test_empty_cohort_edge_case():
    # Empty cohort summary returns 200 with 0 students, no division by zero
    resp = client.get("/api/teacher/cohorts/empty-cohort/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cohort_id"] == "empty-cohort"
    assert data["total_students"] == 0
    assert data["class_average_mastery"] == 0.0
    assert data["top_gaps"] == []
    assert data["frequent_misconceptions"] == []

    # Empty cohort heatmap returns 200 with empty matrix
    resp_heat = client.get("/api/teacher/cohorts/empty-cohort/heatmap")
    assert resp_heat.status_code == 200
    heat_data = resp_heat.json()
    assert heat_data["cohort_id"] == "empty-cohort"
    assert heat_data["students"] == []
    assert heat_data["matrix"] == {}


def test_nonexistent_cohort_returns_404():
    resp = client.get("/api/teacher/cohorts/nonexistent-cohort-id/summary")
    assert resp.status_code == 404
