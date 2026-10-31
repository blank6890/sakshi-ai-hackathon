"""Reasoning-based misconception detection and cognitive diagnosis for physics concepts."""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from deeptutor.learning.grading import grade_answer


class MisconceptionAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    is_correct: bool
    reasoning_valid: bool
    misconception_id: str | None = None
    misconception_name: str = ""
    remedial_feedback: str = ""
    explanation: str = ""

    @model_validator(mode="after")
    def _sync_fields(self) -> MisconceptionAnalysis:
        if not self.explanation and self.remedial_feedback:
            self.explanation = self.remedial_feedback
        elif not self.remedial_feedback and self.explanation:
            self.remedial_feedback = self.explanation
        return self


PHYSICS_MISCONCEPTIONS: dict[str, dict[str, Any]] = {
    "ohm_r_depends_on_v": {
        "id": "ohm_r_depends_on_v",
        "name": "Resistance Depends on Voltage or Current",
        "concept_ids": ["c_ohms_law", "c_resistance", "c_factors_affecting_resistance"],
        "description": "Believing resistance R depends causally on V or I rather than material, length, area, temperature.",
        "remedial_feedback": (
            "Resistance R is an intrinsic property determined by the conductor's material and dimensions "
            "(length, cross-sectional area) and temperature (R = rho * L / A), not by the applied voltage V or current I. "
            "In an ohmic conductor, when V changes, current I changes proportionally while R remains constant."
        ),
        "flawed_patterns": [
            r"\b(r|resistance)\s+(is\s+)?(directly\s+)?proportional\s+to\s+(v|voltage)\b",
            r"\b(r|resistance)\s+doubles\b",
            r"\b(r|resistance)\s+(increases|decreases|changes)\s+when\s+(v|i|voltage|current)\b",
            r"\b(v|voltage)\s+cancels\s+(out\s+)?current\b",
            r"\bcancels\s+out\s+current\b",
            r"\bcancels\s+current\b",
            r"\br\s*=\s*v\s*/\s*i\s*,?\s*so\s+(r|resistance)\s+doubles\b",
            r"\bdepends\s+on\s+(the\s+)?(voltage|v|current|i)\b",
        ],
        "sound_patterns": [
            r"material\s+and\s+dimensions",
            r"resistivity",
            r"cross-sectional\s+area",
            r"independent\s+of\s+(v|voltage|i|current)",
            r"(does\s+not|not)\s+depend\s+on\s+(v|voltage|i|current)",
            r"intrinsic\s+property",
            r"remains\s+constant",
        ],
    },
    "series_current_consumed": {
        "id": "series_current_consumed",
        "name": "Current Consumed in Series Resistors",
        "concept_ids": ["c_series_circuits", "c_resistors_in_series"],
        "description": "Believing current decreases as it passes through successive series resistors ('current gets used up').",
        "remedial_feedback": (
            "By conservation of charge, electric current is identical at every point in a series circuit; "
            "resistors do not consume or use up current, but cause a potential difference (voltage drop)."
        ),
        "flawed_patterns": [
            r"\bcurrent\s+(decreases|drops|falls|is\s+consumed|gets\s+used\s+up|gets\s+less|diminishes)\b",
            r"\bresistors?\s+(consume|consumes|use\s+up|uses\s+up)\s+current\b",
            r"\bless\s+current\s+(reaches|flows|exits|passes)\b",
            r"\bcurrent\s+gets\s+(used|consumed|smaller)\s+(as|after)\b",
        ],
        "sound_patterns": [
            r"conservation\s+of\s+charge",
            r"current\s+is\s+(the\s+)?same\s+(everywhere|throughout|in\s+series)",
            r"identical\s+at\s+every\s+point",
            r"does\s+not\s+(get\s+used\s+up|consume)",
        ],
    },
    "parallel_resistor_additive": {
        "id": "parallel_resistor_additive",
        "name": "Parallel Resistor Resistance Additive",
        "concept_ids": ["c_parallel_circuits", "c_resistors_in_parallel"],
        "description": "Believing adding parallel resistors increases total equivalent resistance.",
        "remedial_feedback": (
            "Adding resistors in parallel provides additional pathways for charge flow, thereby decreasing "
            "total equivalent resistance (1/Req = 1/R1 + 1/R2 + ...), not increasing it."
        ),
        "flawed_patterns": [
            r"\b(adding|more)\s+(parallel\s+)?resistors\s+increases\s+(total\s+|equivalent\s+)?resistance\b",
            r"\bparallel\s+resistors?\s+add(s)?\s+up\b",
            r"\btotal\s+resistance\s+increases\s+(in|with)\s+parallel\b",
            r"\br_?eq\s*=\s*r1\s*\+\s*r2\s+in\s+parallel\b",
        ],
        "sound_patterns": [
            r"additional\s+pathways?",
            r"decreases\s+(total\s+|equivalent\s+)?resistance",
            r"1/r_?eq",
            r"reciprocal",
        ],
    },
    "mirror_lens_formula_confusion": {
        "id": "mirror_lens_formula_confusion",
        "name": "Mirror and Lens Formula Confusion",
        "concept_ids": ["c_spherical_mirrors", "c_refraction_lenses", "c_lens_formula"],
        "description": "Using +1/v for lenses or -1/v for mirrors.",
        "remedial_feedback": (
            "The mirror formula has a plus sign (1/f = 1/v + 1/u) whereas the lens formula has a minus sign "
            "(1/f = 1/v - 1/u). Confusing the sign produces incorrect focal lengths and image distances."
        ),
        "flawed_patterns": [
            r"\b1/f\s*=\s*1/v\s*\+\s*1/u\s+(for\s+lens|for\s+lenses|in\s+lens)\b",
            r"\b1/f\s*=\s*1/v\s*-\s*1/u\s+(for\s+mirror|for\s+mirrors|in\s+mirror)\b",
            r"\b\+1/v\s+for\s+lens(es)?\b",
            r"\b-1/v\s+for\s+mirror(s)?\b",
            r"\blens\s+formula\s+has\s+(a\s+)?plus\b",
            r"\bmirror\s+formula\s+has\s+(a\s+)?minus\b",
            r"\blens\s+formula\s+(is|uses)\s+1/v\s*\+\s*1/u\b",
            r"\bmirror\s+formula\s+(is|uses)\s+1/v\s*-\s*1/u\b",
        ],
        "sound_patterns": [
            r"mirror\s+formula\s+(is|has)\s+(1/f\s*=\s*)?1/v\s*\+\s*1/u",
            r"lens\s+formula\s+(is|has)\s+(1/f\s*=\s*)?1/v\s*-\s*1/u",
        ],
    },
    "refraction_density_speed": {
        "id": "refraction_density_speed",
        "name": "Light Speed in Optically Denser Medium",
        "concept_ids": ["c_refraction", "c_refractive_index", "c_snells_law"],
        "description": "Believing light travels faster in optically denser medium.",
        "remedial_feedback": (
            "Light travels slower in an optically denser medium with higher refractive index (v = c / n), "
            "bending towards the normal."
        ),
        "flawed_patterns": [
            r"\blight\s+travels\s+faster\s+in\s+(optically\s+)?denser\b",
            r"\bspeed\s+(of\s+light\s+)?increases\s+in\s+(optically\s+)?denser\b",
            r"\bhigher\s+refractive\s+index\s+means\s+faster\b",
            r"\bdenser\s+medium\s+(makes\s+light\s+faster|increases\s+speed)\b",
        ],
        "sound_patterns": [
            r"travels\s+slower\s+in\s+(optically\s+)?denser",
            r"v\s*=\s*c\s*/\s*n",
            r"speed\s+decreases\s+in\s+(optically\s+)?denser",
        ],
    },
    "magnetic_monopole": {
        "id": "magnetic_monopole",
        "name": "Existence of Isolated Magnetic Monopoles",
        "concept_ids": ["c_magnetic_field_lines", "c_bar_magnet"],
        "description": "Believing cutting a magnet creates isolated north and south poles.",
        "remedial_feedback": (
            "Cutting a magnet produces two smaller bipolar magnets, each with its own north and south poles; "
            "isolated magnetic monopoles do not exist in classical electromagnetism."
        ),
        "flawed_patterns": [
            r"\bcreates?\s+(an\s+)?isolated\s+(north|south)\b",
            r"\b(creates?|produces?|results?\s+in)\s+(a\s+)?single\s+pole\b",
            r"\bseparates?\s+(the\s+)?north\s+and\s+south\s+poles?\b",
            r"\bonly\s+(a\s+)?(north|south)\s+pole\s+remains\b",
            r"\bisolated\s+magnetic\s+monopole\b",
        ],
        "sound_patterns": [
            r"two\s+(smaller\s+)?(bipolar\s+)?magnets",
            r"each\s+(half\s+)?has\s+both\s+north\s+and\s+south",
            r"monopoles\s+do\s+not\s+exist",
        ],
    },
    "electromagnet_charge_flow": {
        "id": "electromagnet_charge_flow",
        "name": "Magnetic Field Lines Confused with Charge Flow",
        "concept_ids": ["c_magnetic_effects", "c_electromagnet", "c_solenoid"],
        "description": "Confusing magnetic field lines with electric current discharge or static charge flow.",
        "remedial_feedback": (
            "Magnetic field lines represent the direction and strength of the magnetic force exerted on "
            "moving charges or magnetic dipoles; they are not a flow of electric charge or current discharge."
        ),
        "flawed_patterns": [
            r"\b(field\s+lines\s+are|represent)\s+(electric\s+)?(charge\s+flow|current\s+discharge)\b",
            r"\bcharges?\s+flow(ing)?\s+along\s+(the\s+)?magnetic\s+field\s+lines\b",
            r"\bcurrent\s+discharge\s+along\s+field\s+lines\b",
            r"\bmagnetic\s+field\s+lines\s+are\s+electric\s+current\b",
        ],
        "sound_patterns": [
            r"represent\s+the\s+direction\s+(and\s+strength\s+)?of\s+(the\s+)?magnetic\s+force",
            r"not\s+(a\s+)?flow\s+of\s+(electric\s+)?charge",
        ],
    },
}


_OPPOSITE_PAIRS = [
    (r"\bincreas(e|es|ed|ing)\b", r"\bdecreas(e|es|ed|ing)\b"),
    (r"\bfaster\b", r"\bslower\b"),
    (r"\bmore\b", r"\bless\b"),
    (r"\bgreater\b", r"\b(smaller|less)\b"),
    (r"\bconstant\b", r"\b(changes?|doubles?|halves?|increases?|decreases?)\b"),
    (r"\+", r"-"),
    (r"\btrue\b", r"\bfalse\b"),
    (r"\byes\b", r"\bno\b"),
]


def _check_answer_correct(student_answer: str, expected_answer: str) -> bool:
    sa = student_answer.strip().lower()
    ea = expected_answer.strip().lower()
    if not sa or not ea:
        return False
    if sa == ea:
        return True

    # Check for direct contradictions (antonyms, opposing signs)
    for p1, p2 in _OPPOSITE_PAIRS:
        has_p1_sa = bool(re.search(p1, sa))
        has_p2_sa = bool(re.search(p2, sa))
        has_p1_ea = bool(re.search(p1, ea))
        has_p2_ea = bool(re.search(p2, ea))
        if has_p1_sa and has_p2_ea and not has_p1_ea:
            return False
        if has_p2_sa and has_p1_ea and not has_p2_ea:
            return False

    if ea in sa or sa in ea:
        return True

    # Check key scientific phrases
    for phrase in [
        "remains constant",
        "remains the same",
        "constant",
        "same everywhere",
        "closed continuous loops",
        "slower",
        "1/v - 1/u",
        "1/v + 1/u",
    ]:
        if phrase in sa and phrase in ea:
            return True

    return grade_answer(student_answer, expected_answer, "short") or grade_answer(
        student_answer, expected_answer, "choice"
    ) or grade_answer(student_answer, expected_answer, "open")


def _evaluate_with_llm(
    concept_id: str,
    question: str,
    expected_answer: str,
    student_answer: str,
    student_reasoning: str,
    llm_config: Any,
) -> MisconceptionAnalysis | None:
    if llm_config is None:
        return None
    try:
        from deeptutor.services.llm.factory import complete_with_config

        async def _call():
            prompt = (
                f"You are evaluating a student's answer and reasoning on Class 10 Physics concept '{concept_id}'.\n"
                f"Question: {question}\n"
                f"Expected Answer: {expected_answer}\n"
                f"Student Answer: {student_answer}\n"
                f"Student Reasoning: {student_reasoning}\n\n"
                "Evaluate whether the answer is correct, whether the reasoning is scientifically sound, "
                "and whether any common misconception was exhibited (e.g. ohm_r_depends_on_v, series_current_consumed, "
                "parallel_resistor_additive, mirror_lens_formula_confusion, refraction_density_speed, "
                "magnetic_monopole, electromagnet_charge_flow).\n"
                "Return JSON only: {\"is_correct\": bool, \"reasoning_valid\": bool, "
                "\"misconception_id\": string|null, \"misconception_name\": string, \"remedial_feedback\": string}"
            )
            return await complete_with_config(config=llm_config, prompt=prompt, max_tokens=500)

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            raw = pool.submit(lambda: asyncio.run(_call())).result(timeout=10)

        data = json.loads(raw)
        return MisconceptionAnalysis(
            is_correct=data.get("is_correct", False),
            reasoning_valid=data.get("reasoning_valid", False),
            misconception_id=data.get("misconception_id"),
            misconception_name=data.get("misconception_name", ""),
            remedial_feedback=data.get("remedial_feedback", ""),
        )
    except Exception:
        return None


def analyze_reasoning_and_misconceptions(
    concept_id: str,
    question: str,
    expected_answer: str,
    student_answer: str,
    student_reasoning: str,
    llm_config: Any = None,
) -> MisconceptionAnalysis:
    """Analyze student answer correctness, reasoning validity, and diagnose misconceptions.

    Detects lucky guesses where is_correct is True but reasoning_valid is False and
    an active misconception was used in the rationale.
    """
    is_correct = _check_answer_correct(student_answer, expected_answer)
    combined_reasoning = f"{student_answer} {student_reasoning}".strip().lower()

    # Priority 1: Rule-based check against cataloged misconceptions
    detected_id: str | None = None
    detected_meta: dict[str, Any] | None = None

    # Check concept-relevant misconceptions first, then remaining
    ordered_items = sorted(
        PHYSICS_MISCONCEPTIONS.values(),
        key=lambda item: 0 if concept_id in item.get("concept_ids", []) or item["id"] in concept_id else 1,
    )

    for item in ordered_items:
        # Check if student explicitly exhibits a flawed pattern
        for pat in item.get("flawed_patterns", []):
            if re.search(pat, combined_reasoning, re.IGNORECASE):
                # Verify that sound patterns do not override this
                sound_matched = any(
                    re.search(sp, student_reasoning.lower(), re.IGNORECASE)
                    for sp in item.get("sound_patterns", [])
                )
                if not sound_matched:
                    detected_id = item["id"]
                    detected_meta = item
                    break
        if detected_id:
            break

    if detected_id and detected_meta:
        return MisconceptionAnalysis(
            is_correct=is_correct,
            reasoning_valid=False,
            misconception_id=detected_id,
            misconception_name=detected_meta["name"],
            remedial_feedback=detected_meta["remedial_feedback"],
        )

    # Priority 2: Optional LLM completion fallback for open-ended queries
    if llm_config is not None:
        llm_result = _evaluate_with_llm(
            concept_id, question, expected_answer, student_answer, student_reasoning, llm_config
        )
        if llm_result is not None:
            return llm_result

    # Priority 3: Fallback heuristic for sound reasoning vs uncataloged error
    if is_correct:
        # Student answered correctly and didn't exhibit any cataloged misconception
        return MisconceptionAnalysis(
            is_correct=True,
            reasoning_valid=True,
            misconception_id=None,
            misconception_name="",
            remedial_feedback="",
        )

    # Incorrect answer with no cataloged misconception
    return MisconceptionAnalysis(
        is_correct=False,
        reasoning_valid=False,
        misconception_id=None,
        misconception_name="",
        remedial_feedback=(
            f"The answer '{student_answer}' is incorrect. The expected answer is '{expected_answer}'."
        ),
    )


__all__ = [
    "MisconceptionAnalysis",
    "PHYSICS_MISCONCEPTIONS",
    "analyze_reasoning_and_misconceptions",
]
