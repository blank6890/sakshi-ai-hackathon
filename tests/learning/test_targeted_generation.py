"""Tests for targeted question generation and difficulty calibration based on ZPD."""

from deeptutor.learning.curriculum import CurriculumGraph
from deeptutor.learning.models import ErrorRecord, ErrorType, LearningProgress
from deeptutor.learning.question_generator import (
    DifficultyLevel,
    QuestionSelector,
    TargetedQuestionTarget,
)
from deeptutor.learning.service import LearningService
from deeptutor.learning.storage import LearningStore


def test_select_next_weak_concept():
    graph = CurriculumGraph.load_default("class10_physics")
    # c_electric_current and c_potential_difference are mastered (0.85)
    # c_ohms_law is weak (0.35)
    mastery = {
        "c_electric_charge": 0.90,
        "c_electric_current": 0.85,
        "c_potential_difference": 0.85,
        "c_ohms_law": 0.35,
        "c_resistance_series_parallel": 0.10,
    }
    selector = QuestionSelector(graph)
    target = selector.select_next_target(mastery)
    assert target.concept_id == "c_ohms_law"
    assert target.difficulty == DifficultyLevel.CONCEPTUAL_LEVEL_1


def test_calibrate_difficulty_as_mastery_rises():
    graph = CurriculumGraph.load_default("class10_physics")
    selector = QuestionSelector(graph)

    # Mastery 0.55 -> Level 2 Application
    d1 = selector.calibrate_difficulty(mastery_p_l=0.55)
    assert d1 == DifficultyLevel.APPLICATION_LEVEL_2

    # Mastery 0.80 -> Level 3 Complex Numerical
    d2 = selector.calibrate_difficulty(mastery_p_l=0.80)
    assert d2 == DifficultyLevel.CALCULATION_LEVEL_3


def test_difficulty_calibration_across_all_tiers():
    graph = CurriculumGraph.load_default("class10_physics")
    selector = QuestionSelector(graph)

    # Tier 1: P(L) < 0.40
    assert selector.calibrate_difficulty(0.0) == DifficultyLevel.CONCEPTUAL_LEVEL_1
    assert selector.calibrate_difficulty(0.20) == DifficultyLevel.CONCEPTUAL_LEVEL_1
    assert selector.calibrate_difficulty(0.39) == DifficultyLevel.CONCEPTUAL_LEVEL_1

    # Tier 2: 0.40 <= P(L) < 0.70
    assert selector.calibrate_difficulty(0.40) == DifficultyLevel.APPLICATION_LEVEL_2
    assert selector.calibrate_difficulty(0.55) == DifficultyLevel.APPLICATION_LEVEL_2
    assert selector.calibrate_difficulty(0.699) == DifficultyLevel.APPLICATION_LEVEL_2

    # Tier 3: P(L) >= 0.70
    assert selector.calibrate_difficulty(0.70) == DifficultyLevel.CALCULATION_LEVEL_3
    assert selector.calibrate_difficulty(0.85) == DifficultyLevel.CALCULATION_LEVEL_3
    assert selector.calibrate_difficulty(1.0) == DifficultyLevel.CALCULATION_LEVEL_3


def test_prioritizing_concepts_with_active_misconceptions():
    graph = CurriculumGraph.load_default("class10_physics")
    selector = QuestionSelector(graph)

    # Both c_ohms_law and c_magnetic_fields are in eligible frontier
    # (prereqs c_electric_current & c_potential_difference are mastered >= 0.70).
    # c_ohms_law has higher P(L) (0.50 vs 0.45), but has an active misconception!
    mastery = {
        "c_electric_charge": 0.90,
        "c_electric_current": 0.85,
        "c_potential_difference": 0.85,
        "c_ohms_law": 0.50,
        "c_magnetic_fields": 0.45,
    }
    active_misconceptions = {
        "c_ohms_law": ["ohm_r_depends_on_v"],
    }
    target = selector.select_next_target(mastery, active_misconceptions=active_misconceptions)
    assert target.concept_id == "c_ohms_law"
    assert "ohm_r_depends_on_v" in target.active_misconceptions
    assert target.difficulty == DifficultyLevel.APPLICATION_LEVEL_2


def test_generate_calibrated_question():
    graph = CurriculumGraph.load_default("class10_physics")
    selector = QuestionSelector(graph)

    target = TargetedQuestionTarget(
        concept_id="c_ohms_law",
        concept_name="Ohm's Law and Resistance",
        difficulty=DifficultyLevel.APPLICATION_LEVEL_2,
        active_misconceptions=["ohm_r_depends_on_v"],
    )
    question = selector.generate_question(target)

    assert isinstance(question, dict)
    assert question["concept_id"] == "c_ohms_law"
    assert question["concept_name"] == "Ohm's Law and Resistance"
    assert question["difficulty"] in (DifficultyLevel.APPLICATION_LEVEL_2.value, DifficultyLevel.APPLICATION_LEVEL_2)
    assert "step" in question["prompt"].lower() or "reasoning" in question["prompt"].lower()
    assert question.get("expected_answer")
    assert "ohm_r_depends_on_v" in question.get("misconception_targets", [])


def test_learning_service_get_next_targeted_question(tmp_path):
    store = LearningStore(root=tmp_path)
    service = LearningService(store)
    progress = LearningProgress(book_id="book_physics_10")
    progress.mastery_levels = {
        "c_electric_charge": 0.90,
        "c_electric_current": 0.85,
        "c_potential_difference": 0.85,
        "c_ohms_law": 0.35,
        "c_resistance_series_parallel": 0.10,
    }

    # Add an active error record for c_ohms_law with misconception
    progress.error_records.append(
        ErrorRecord(
            id="err1",
            question_id="q1",
            knowledge_point_id="c_ohms_law",
            module_id="m1",
            error_type=ErrorType.UNDERSTANDING_DEVIATION,
            self_attribution="Resistance doubles because R = V/I",
            ai_confirmation="Resistance R is an intrinsic property determined by material and dimensions",
            status="active",
        )
    )

    question = service.get_next_targeted_question(progress)
    assert isinstance(question, dict)
    assert question["concept_id"] == "c_ohms_law"
    assert question["difficulty"] == DifficultyLevel.CONCEPTUAL_LEVEL_1.value
    assert "ohm_r_depends_on_v" in question["misconception_targets"]
