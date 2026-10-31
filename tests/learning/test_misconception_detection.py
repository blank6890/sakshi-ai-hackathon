import pytest
from deeptutor.learning.misconception import (
    MisconceptionAnalysis,
    analyze_reasoning_and_misconceptions,
    PHYSICS_MISCONCEPTIONS,
)
from deeptutor.learning.grading import (
    classify_error,
    diagnose_error,
    create_error_record,
)
from deeptutor.learning.models import ErrorType, ErrorRecord
from deeptutor.learning.semantic_assessment import Verdict, judge_answers


def test_detect_ohms_law_misconception():
    concept_id = "c_ohms_law"
    question = "If voltage V across an ohmic conductor doubles, what happens to resistance R?"
    student_reasoning = "Since R = V/I, if V doubles, R is directly proportional to V, so resistance doubles."
    student_answer = "Resistance doubles"

    result = analyze_reasoning_and_misconceptions(
        concept_id=concept_id,
        question=question,
        expected_answer="Resistance remains constant",
        student_answer=student_answer,
        student_reasoning=student_reasoning,
    )
    assert result.is_correct is False
    assert result.misconception_id == "ohm_r_depends_on_v"
    assert "conductor's material and dimensions" in result.remedial_feedback


def test_lucky_guess_with_flawed_reasoning():
    # Student states correct answer but reasons incorrectly with misconception
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_ohms_law",
        question="If V doubles, what happens to R?",
        expected_answer="Remains constant",
        student_answer="Remains constant",
        student_reasoning="Because V cancels out current completely to zero.",
    )
    assert result.is_correct is True
    assert result.reasoning_valid is False
    assert result.misconception_id is not None


def test_valid_reasoning_with_correct_answer():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_ohms_law",
        question="If voltage V across an ohmic conductor doubles, what happens to resistance R?",
        expected_answer="Resistance remains constant",
        student_answer="Resistance remains constant",
        student_reasoning="Resistance depends on resistivity, length, and cross-sectional area, not on V or I.",
    )
    assert result.is_correct is True
    assert result.reasoning_valid is True
    assert result.misconception_id is None
    assert result.remedial_feedback == ""


def test_catalog_misconceptions_coverage():
    catalog_ids = {
        "ohm_r_depends_on_v",
        "series_current_consumed",
        "parallel_resistor_additive",
        "mirror_lens_formula_confusion",
        "refraction_density_speed",
        "magnetic_monopole",
        "electromagnet_charge_flow",
    }
    for m_id in catalog_ids:
        assert m_id in PHYSICS_MISCONCEPTIONS
        meta = PHYSICS_MISCONCEPTIONS[m_id]
        assert "id" in meta
        assert "name" in meta
        assert "remedial_feedback" in meta


def test_series_current_consumed_detection():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_series_circuits",
        question="What is the current through the second resistor compared to the first?",
        expected_answer="Current is the same through both resistors",
        student_answer="Current is less in second resistor",
        student_reasoning="Current decreases after passing through the first resistor because it gets used up.",
    )
    assert result.is_correct is False
    assert result.misconception_id == "series_current_consumed"
    assert "conservation of charge" in result.remedial_feedback.lower()


def test_parallel_resistor_additive_detection():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_parallel_circuits",
        question="What happens to the total resistance when another resistor is added in parallel?",
        expected_answer="Total resistance decreases",
        student_answer="Total resistance increases",
        student_reasoning="Adding resistors increases total resistance because parallel resistors add up.",
    )
    assert result.is_correct is False
    assert result.misconception_id == "parallel_resistor_additive"
    assert "additional pathways" in result.remedial_feedback.lower()


def test_mirror_lens_formula_confusion_detection():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_refraction_lenses",
        question="State the relationship between focal length f, image distance v, and object distance u for a thin lens.",
        expected_answer="1/f = 1/v - 1/u",
        student_answer="1/f = 1/v + 1/u",
        student_reasoning="The lens formula is 1/v + 1/u just like mirrors.",
    )
    assert result.is_correct is False
    assert result.misconception_id == "mirror_lens_formula_confusion"
    assert "minus sign" in result.remedial_feedback.lower()


def test_refraction_density_speed_detection():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_refraction",
        question="How does the speed of light change when entering water from air?",
        expected_answer="Speed of light decreases",
        student_answer="Speed increases",
        student_reasoning="Light travels faster in optically denser medium with higher refractive index.",
    )
    assert result.is_correct is False
    assert result.misconception_id == "refraction_density_speed"
    assert "slower" in result.remedial_feedback.lower()


def test_magnetic_monopole_detection():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_magnetic_field_lines",
        question="What happens if you cut a bar magnet in half?",
        expected_answer="Two magnets each with north and south poles",
        student_answer="Separates the north and south poles",
        student_reasoning="Cutting the magnet creates an isolated north pole and an isolated south pole.",
    )
    assert result.is_correct is False
    assert result.misconception_id == "magnetic_monopole"
    assert "bipolar" in result.remedial_feedback.lower()


def test_electromagnet_charge_flow_detection():
    result = analyze_reasoning_and_misconceptions(
        concept_id="c_magnetic_effects",
        question="What do magnetic field lines represent?",
        expected_answer="Direction and strength of magnetic force",
        student_answer="Flow of electric charge",
        student_reasoning="Magnetic field lines are electric charge flow and current discharge.",
    )
    assert result.is_correct is False
    assert result.misconception_id == "electromagnet_charge_flow"
    assert "magnetic force" in result.remedial_feedback.lower()


def test_classify_error_with_misconception():
    # Blank answer -> METACOGNITIVE
    assert classify_error("") is ErrorType.METACOGNITIVE
    assert classify_error("   ") is ErrorType.METACOGNITIVE

    # Normal application error
    assert classify_error("The value is 100") is ErrorType.APPLICATION_ERROR

    # Flawed reasoning exhibiting misconception -> UNDERSTANDING_DEVIATION
    err = classify_error(
        user_answer="Resistance doubles",
        user_reasoning="R = V/I so resistance is proportional to V and doubles",
        concept_id="c_ohms_law",
        expected_answer="Resistance remains constant",
    )
    assert err is ErrorType.UNDERSTANDING_DEVIATION


def test_diagnose_error_and_create_error_record():
    error_type, ai_confirmation, misconception_id = diagnose_error(
        user_answer="Resistance doubles",
        user_reasoning="R is directly proportional to V",
        concept_id="c_ohms_law",
        expected_answer="Resistance remains constant",
        question="If V doubles, what happens to R?",
    )
    assert error_type is ErrorType.UNDERSTANDING_DEVIATION
    assert misconception_id == "ohm_r_depends_on_v"
    assert "material and dimensions" in ai_confirmation

    # Test create_error_record
    record = create_error_record(
        question_id="q101",
        knowledge_point_id="c_ohms_law",
        module_id="mod_electricity",
        user_answer="Resistance doubles",
        user_reasoning="R is directly proportional to V",
        expected_answer="Resistance remains constant",
        question="If V doubles, what happens to R?",
    )
    assert isinstance(record, ErrorRecord)
    assert record.question_id == "q101"
    assert record.knowledge_point_id == "c_ohms_law"
    assert record.error_type is ErrorType.UNDERSTANDING_DEVIATION
    assert "material and dimensions" in record.ai_confirmation
    assert record.status == "active"


@pytest.mark.asyncio
async def test_judge_answers_misconception_integration(monkeypatch):
    from deeptutor.learning import semantic_assessment

    # Mock _request to return initial LLM verdicts
    async def mock_request(config, prompt, items, native_images=None, sources=None):
        return {
            "verdicts": [
                {
                    "question_id": "q_lucky",
                    "result": "correct",
                    "confidence": 0.9,
                    "feedback": "Correct value stated.",
                },
                {
                    "question_id": "q_wrong",
                    "result": "incorrect",
                    "confidence": 0.95,
                    "feedback": "Incorrect value.",
                },
            ]
        }

    monkeypatch.setattr(semantic_assessment, "_request", mock_request)

    items = [
        {
            "question_id": "q_lucky",
            "prompt": "If V doubles across an ohmic conductor, what happens to R?",
            "expected_answer": "Remains constant",
            "answer": "Remains constant",
            "reasoning": "Because V cancels out current completely to zero.",
            "knowledge_point_id": "c_ohms_law",
        },
        {
            "question_id": "q_wrong",
            "prompt": "If V doubles across an ohmic conductor, what happens to R?",
            "expected_answer": "Remains constant",
            "answer": "Resistance doubles",
            "reasoning": "R is directly proportional to V",
            "knowledge_point_id": "c_ohms_law",
        },
    ]

    verdicts = await judge_answers(None, items)
    assert "q_lucky" in verdicts
    assert "q_wrong" in verdicts

    # Lucky guess check
    lucky_verdict = verdicts["q_lucky"]
    assert lucky_verdict.misconception_id == "ohm_r_depends_on_v"
    assert lucky_verdict.reasoning_valid is False
    assert "Lucky guess detected" in lucky_verdict.feedback

    # Wrong answer check
    wrong_verdict = verdicts["q_wrong"]
    assert wrong_verdict.misconception_id == "ohm_r_depends_on_v"
    assert wrong_verdict.reasoning_valid is False
    assert "material and dimensions" in wrong_verdict.feedback
