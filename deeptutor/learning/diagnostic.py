"""Adaptive Diagnostic Test Engine for initial learner calibration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import uuid
from typing import Any

from deeptutor.learning.bkt import BKTParameters, update_bkt
from deeptutor.learning.curriculum import CurriculumGraph


CLASS10_PHYSICS_MILESTONES: list[dict[str, Any]] = [
    {
        "question_id": "diag_q1_reflection",
        "concept_id": "c_reflection_refraction",
        "chapter": "Light - Reflection and Refraction",
        "prompt": "According to the laws of reflection, what is the angle of reflection if the angle of incidence is 45 degrees?",
        "expected_answer": "45 degrees",
    },
    {
        "question_id": "diag_q2_electric_current",
        "concept_id": "c_electric_current",
        "chapter": "Electricity",
        "prompt": "What is the electric current flowing when 1 Coulomb of charge passes through a cross-section per second?",
        "expected_answer": "1 A",
    },
    {
        "question_id": "diag_q3_ohms_law",
        "concept_id": "c_ohms_law",
        "chapter": "Electricity",
        "prompt": "According to Ohm's Law at constant temperature, what is the mathematical formula relating potential difference V, current I, and resistance R?",
        "expected_answer": "V = IR",
    },
    {
        "question_id": "diag_q4_lens_power",
        "concept_id": "c_lens_formula",
        "chapter": "Light - Reflection and Refraction",
        "prompt": "What is the SI unit of power of a lens having focal length expressed in meters?",
        "expected_answer": "Dioptre",
    },
    {
        "question_id": "diag_q5_magnetic_field",
        "concept_id": "c_magnetic_fields",
        "chapter": "Magnetic Effects of Electric Current",
        "prompt": "What is the conventional direction of magnetic field lines outside a bar magnet?",
        "expected_answer": "North to South",
    },
    {
        "question_id": "diag_q6_flemings_rules",
        "concept_id": "c_flemings_rules",
        "chapter": "Magnetic Effects of Electric Current",
        "prompt": "In Fleming's Left-Hand Rule, which finger represents the direction of the magnetic field?",
        "expected_answer": "Forefinger",
    },
]


@dataclass
class DiagnosticSession:
    """State tracking for a diagnostic assessment session."""

    session_id: str
    syllabus: str = "class10_physics"
    status: str = "in_progress"  # "in_progress" | "completed"
    questions: list[dict[str, Any]] = field(default_factory=list)
    answers: dict[str, dict[str, str]] = field(default_factory=dict)
    score: float = 0.0
    concept_mastery: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _check_answer(user_input: Any, expected: str) -> bool:
    if isinstance(user_input, dict):
        raw_ans = str(user_input.get("answer", ""))
    else:
        raw_ans = str(user_input)
    return raw_ans.strip().lower() == expected.strip().lower()


class DiagnosticEngine:
    """Orchestrates milestone diagnostic sessions and BKT prior propagation."""

    def __init__(self) -> None:
        self._sessions: dict[str, DiagnosticSession] = {}

    def create_session(self, syllabus: str = "class10_physics") -> DiagnosticSession:
        """Create a new diagnostic session with milestone questions from curriculum."""
        syllabus_name = syllabus or "class10_physics"
        # Select 6 milestone questions
        questions = [dict(q) for q in CLASS10_PHYSICS_MILESTONES]
        session_id = f"diag_{uuid.uuid4().hex[:12]}"
        session = DiagnosticSession(
            session_id=session_id,
            syllabus=syllabus_name,
            status="in_progress",
            questions=questions,
            answers={},
            score=0.0,
            concept_mastery={},
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> DiagnosticSession | None:
        return self._sessions.get(session_id)

    def submit_answers(
        self,
        session_id: str,
        answers: dict[str, dict[str, str]],
    ) -> dict[str, Any]:
        """Grade answers, apply BKT updates, propagate priors, and complete session."""
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Diagnostic session '{session_id}' not found")

        # Load curriculum graph
        graph = CurriculumGraph.load_default(session.syllabus)
        q_map = {q["question_id"]: q for q in session.questions}

        # Grade tested questions
        tested_results: dict[str, bool] = {}
        correct_count = 0
        total_questions = len(session.questions)

        for qid, q in q_map.items():
            user_entry = answers.get(qid, {})
            is_correct = _check_answer(user_entry, q["expected_answer"])
            tested_results[q["concept_id"]] = is_correct
            if is_correct:
                correct_count += 1

        score = float(correct_count / total_questions) if total_questions > 0 else 0.0

        # Compute BKT mastery vector with DAG prior propagation
        params = BKTParameters()
        p_l0 = params.p_l0  # 0.20
        concept_mastery: dict[str, float] = {}

        # Topological propagation ensures prerequisites are processed before dependent concepts
        topo_order = graph.topological_sort()
        for cid in topo_order:
            if cid in tested_results:
                # Direct BKT update on tested concepts
                is_correct = tested_results[cid]
                # BKT update on prior p_l0: correct -> ~0.601, incorrect -> ~0.176
                m = update_bkt(p_l_prev=p_l0, is_correct=is_correct, params=params)
                concept_mastery[cid] = round(m, 4)
            else:
                # Untested dependent concept: inherits propagated prior
                prereqs = graph.get_prerequisites(cid)
                if not prereqs:
                    concept_mastery[cid] = round(p_l0, 4)
                else:
                    # Weakest prerequisite acts as bottleneck
                    min_prereq = min(concept_mastery[p] for p in prereqs)
                    if min_prereq < p_l0:
                        # Dependent inherits low unmastered prior
                        concept_mastery[cid] = round(min_prereq, 4)
                    else:
                        # Scaled prior bounded below 0.25
                        propagated = min(0.24, p_l0 * (min_prereq / 0.60))
                        concept_mastery[cid] = round(propagated, 4)

        # Update session
        session.answers = answers
        session.status = "completed"
        session.score = score
        session.concept_mastery = concept_mastery
        self._latest_completed_session = session

        return {
            "status": "completed",
            "session_id": session_id,
            "score": score,
            "concept_mastery": concept_mastery,
        }

    def get_latest_completed_session(self) -> DiagnosticSession | None:
        """Return the most recently completed diagnostic assessment session."""
        return getattr(self, "_latest_completed_session", None)

    def get_report(self, session_id: str) -> dict[str, Any]:
        """Generate comprehensive diagnostic report with frontier recommendations."""
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Diagnostic session '{session_id}' not found")

        recommendations: list[dict[str, Any]] = []
        try:
            graph = CurriculumGraph.load_default(session.syllabus)
            mastered_ids = {
                cid for cid, m in session.concept_mastery.items() if m >= 0.5
            }
            frontier = sorted(graph.get_eligible_frontier(mastered_ids))
            for cid in frontier:
                concept = graph.get_concept(cid)
                recommendations.append({
                    "concept_id": cid,
                    "name": concept.get("name", cid),
                    "chapter": concept.get("chapter", ""),
                })
        except Exception:
            pass

        return {
            "session_id": session.session_id,
            "syllabus": session.syllabus,
            "status": session.status,
            "score": session.score,
            "concept_mastery": session.concept_mastery,
            "recommendations": recommendations,
            "answers": session.answers,
        }


# Global default engine instance
_diagnostic_engine = DiagnosticEngine()


def get_diagnostic_engine() -> DiagnosticEngine:
    """Return the global DiagnosticEngine instance."""
    return _diagnostic_engine


__all__ = [
    "CLASS10_PHYSICS_MILESTONES",
    "DiagnosticEngine",
    "DiagnosticSession",
    "get_diagnostic_engine",
]
