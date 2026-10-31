import pytest
from deeptutor.learning.curriculum import CurriculumGraph


def test_load_class10_physics_dag():
    graph = CurriculumGraph.load_default("class10_physics")
    assert len(graph.concepts) >= 12
    assert "c_ohms_law" in graph.concepts
    prereqs = graph.get_prerequisites("c_ohms_law")
    assert "c_potential_difference" in prereqs
    assert "c_electric_current" in prereqs


def test_frontier_calculation():
    graph = CurriculumGraph.load_default("class10_physics")
    # With no prerequisites mastered, only root concepts are eligible
    frontier = graph.get_eligible_frontier(mastered_ids=set())
    assert "c_electric_current" in frontier
    assert "c_ohms_law" not in frontier

    # Once prerequisites mastered, ohms law unlocks
    frontier_unlocked = graph.get_eligible_frontier(
        mastered_ids={"c_electric_charge", "c_electric_current", "c_potential_difference"}
    )
    assert "c_ohms_law" in frontier_unlocked


def test_cycle_detection():
    cyclic_data = {
        "concepts": [
            {"id": "a", "name": "A", "prerequisites": ["b"]},
            {"id": "b", "name": "B", "prerequisites": ["a"]},
        ]
    }
    with pytest.raises(ValueError, match="Prerequisite cycle detected"):
        CurriculumGraph.from_dict(cyclic_data)


def test_get_concept():
    graph = CurriculumGraph.load_default("class10_physics")
    concept = graph.get_concept("c_ohms_law")
    assert concept is not None
    assert concept["id"] == "c_ohms_law"
    assert "name" in concept

    with pytest.raises(KeyError):
        graph.get_concept("c_nonexistent")


def test_frontier_all_mastered():
    graph = CurriculumGraph.load_default("class10_physics")
    all_ids = set(graph.concepts.keys())
    frontier = graph.get_eligible_frontier(mastered_ids=all_ids)
    assert frontier == set()


def test_topological_sort():
    graph = CurriculumGraph.load_default("class10_physics")
    order = graph.topological_sort()
    assert len(order) == len(graph.concepts)
    # Check that prerequisites come before the concept in sorted order
    pos = {cid: idx for idx, cid in enumerate(order)}
    for cid in graph.concepts:
        for prereq in graph.get_prerequisites(cid):
            assert pos[prereq] < pos[cid]


def test_load_default_missing():
    with pytest.raises(FileNotFoundError):
        CurriculumGraph.load_default("nonexistent_curriculum")

