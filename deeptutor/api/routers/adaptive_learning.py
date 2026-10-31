"""Adaptive learning endpoints for ZPD targeted question selection and misconception-aware evaluation."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from deeptutor.learning.bkt import update_bkt
from deeptutor.learning.curriculum import CurriculumGraph
from deeptutor.learning.diagnostic import get_diagnostic_engine
from deeptutor.learning.misconception import analyze_reasoning_and_misconceptions
from deeptutor.learning.models import KnowledgeType, LearningEvidence
from deeptutor.learning.question_generator import QuestionSelector
from deeptutor.learning.scheduler import SpacedRepetitionScheduler
from deeptutor.services.cohort.service import get_cohort_service

router = APIRouter(tags=["adaptive_learning"])

# In-memory question registry for active learning turns
_ACTIVE_QUESTIONS: dict[str, dict[str, Any]] = {}


class NextQuestionRequest(BaseModel):
    student_id: str
    syllabus: str = Field(default="class10_physics")


class SubmitAnswerRequest(BaseModel):
    student_id: str
    question_id: str
    answer: str
    reasoning: str


@router.post("/api/learning/next-question")
@router.post("/learning/next-question")
async def get_next_question(
    body: NextQuestionRequest = Body(...),
) -> dict[str, Any]:
    """Retrieve next targeted question in the student's Zone of Proximal Development (ZPD)."""
    cohort_service = get_cohort_service()
    student = cohort_service.find_student(body.student_id)

    mastery_levels: dict[str, float] = {}
    active_misconceptions: dict[str, list[str]] = {}

    if student is not None:
        mastery_levels = dict(student.get("mastery_levels", {}))
        for m_id in student.get("active_misconceptions", []):
            # Map known misconception back to its trigger concept if possible
            active_misconceptions.setdefault("c_ohms_law", []).append(m_id)
    else:
        # Check if student completed a recent diagnostic assessment
        diag_engine = get_diagnostic_engine()
        latest_diag = diag_engine.get_latest_completed_session()
        if latest_diag and latest_diag.concept_mastery:
            mastery_levels = dict(latest_diag.concept_mastery)
        # Register new student in cohort service
        student = cohort_service.get_or_create_student(
            student_id=body.student_id,
            default_mastery=mastery_levels,
        )

    # Load curriculum DAG and instantiate QuestionSelector
    try:
        graph = CurriculumGraph.load_default(body.syllabus)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to load syllabus '{body.syllabus}': {exc}"
        ) from exc

    selector = QuestionSelector(graph)
    target = selector.select_next_target(
        mastery_levels=mastery_levels,
        active_misconceptions=active_misconceptions if active_misconceptions else None,
    )

    question_data = selector.generate_question(target)
    question_id = f"q_{target.concept_id}_{uuid.uuid4().hex[:8]}"
    question_data["question_id"] = question_id
    question_data["student_id"] = body.student_id
    question_data["created_at"] = time.time()

    # Cache question for subsequent answer submission
    _ACTIVE_QUESTIONS[question_id] = question_data

    return question_data


@router.post("/api/learning/submit-answer")
@router.post("/learning/submit-answer")
async def submit_learning_answer(
    body: SubmitAnswerRequest = Body(...),
) -> dict[str, Any]:
    """Evaluate student answer and reasoning, update BKT mastery, and adjust cohort metrics."""
    # Lookup question
    question = _ACTIVE_QUESTIONS.get(body.question_id)
    if question is None:
        # Fallback question reconstruction from question_id prefix if missing from cache
        concept_id = "c_ohms_law"
        if body.question_id.startswith("q_c_"):
            parts = body.question_id[2:].split("_")
            if len(parts) >= 2:
                concept_id = f"c_{parts[1]}"
        question = {
            "concept_id": concept_id,
            "prompt": "Explain your step-by-step reasoning.",
            "expected_answer": "Remains constant according to Ohm's Law.",
        }

    concept_id = question.get("concept_id", "c_ohms_law")
    prompt = question.get("prompt", "")
    expected_answer = question.get("expected_answer", "")

    # 1. Analyze reasoning and misconceptions
    analysis = analyze_reasoning_and_misconceptions(
        concept_id=concept_id,
        question=prompt,
        expected_answer=expected_answer,
        student_answer=body.answer,
        student_reasoning=body.reasoning,
    )

    # Sound answer requires both final answer correctness and valid reasoning
    is_sound = analysis.is_correct and analysis.reasoning_valid

    # 2. Update BKT mastery
    cohort_service = get_cohort_service()
    student = cohort_service.get_or_create_student(body.student_id)
    prev_mastery = student.get("mastery_levels", {}).get(concept_id, 0.20)

    new_bkt = update_bkt(p_l_prev=prev_mastery, is_correct=is_sound)

    # 3. Schedule spaced review
    scheduler = SpacedRepetitionScheduler()
    state = scheduler.get_initial_state(KnowledgeType.CONCEPT)
    evidence = LearningEvidence(
        knowledge_point_id=concept_id,
        result="correct" if is_sound else "incorrect",
        quality=1.0 if is_sound else 0.0,
    )
    review_state = scheduler.schedule_exam_paced_review(
        state=state,
        knowledge_type=KnowledgeType.CONCEPT,
        evidence=evidence,
    )

    # 4. Update cohort service
    cohort_service.record_student_attempt(
        student_id=body.student_id,
        concept_id=concept_id,
        bkt_mastery=new_bkt,
        cohort_id="class-10-a",
        misconception_id=analysis.misconception_id,
    )

    return {
        "is_correct": analysis.is_correct,
        "reasoning_valid": analysis.reasoning_valid,
        "misconception_detected": analysis.misconception_id is not None,
        "misconception_id": analysis.misconception_id,
        "remedial_feedback": analysis.remedial_feedback,
        "bkt_mastery": round(float(new_bkt), 4),
        "next_review_at": review_state.next_review_at,
    }
