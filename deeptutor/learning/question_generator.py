"""Targeted question generation and difficulty calibration based on Zone of Proximal Development (ZPD)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from deeptutor.learning.curriculum import CurriculumGraph


class DifficultyLevel(str, Enum):
    """Calibrated difficulty levels based on learner Bayesian Knowledge Tracing mastery."""

    CONCEPTUAL_LEVEL_1 = "conceptual_1"  # Qualitative intuition, definitions, core laws
    APPLICATION_LEVEL_2 = "application_2"  # Direct formula substitution, simple circuits/diagrams
    CALCULATION_LEVEL_3 = "calculation_3"  # Multi-step numericals, complex series/parallel, combination of lenses


@dataclass
class TargetedQuestionTarget:
    """Target concept and difficulty calibrated for the learner's ZPD."""

    concept_id: str
    concept_name: str
    difficulty: DifficultyLevel
    active_misconceptions: list[str] = field(default_factory=list)


@dataclass
class TargetedQuestion:
    """Calibrated targeted question ready for presentation to the learner."""

    concept_id: str
    concept_name: str
    difficulty: DifficultyLevel
    prompt: str
    expected_answer: str
    misconception_targets: list[str] = field(default_factory=list)
    question_type: str = "open"

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "concept_name": self.concept_name,
            "difficulty": self.difficulty.value,
            "difficulty_level": self.difficulty,
            "prompt": self.prompt,
            "expected_answer": self.expected_answer,
            "misconception_targets": list(self.misconception_targets),
            "question_type": self.question_type,
            "request_reasoning": True,
        }


# Calibrated exemplar question bank for physics curriculum
_QUESTION_BANK: dict[str, dict[DifficultyLevel, tuple[str, str]]] = {
    "c_ohms_law": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "State Ohm's Law and explain step-by-step why the resistance of a metallic conductor "
            "does not change when the applied voltage across it is doubled at constant temperature.",
            "Resistance is an intrinsic property determined by the conductor's material, length, "
            "cross-sectional area, and temperature (R = rho * L / A), not by applied voltage or current. "
            "By Ohm's Law (V = I * R), doubling the voltage doubles the current while resistance R remains constant.",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "A potential difference of 12 V is maintained across a conductor carrying a current of 2 A. "
            "Calculate the resistance of the conductor step-by-step using Ohm's Law.",
            "Using Ohm's Law V = I * R: R = V / I = 12 V / 2 A = 6 ohms.",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "A cylindrical wire of resistance R is stretched to double its original length without changing its volume. "
            "Calculate the new resistance step-by-step, explaining the changes in cross-sectional area and resistivity.",
            "Since volume V = A * L is constant, when length L' = 2L, cross-sectional area A' = A / 2. "
            "Resistivity rho is unchanged at constant temperature. "
            "New resistance R' = rho * L' / A' = rho * (2L) / (A / 2) = 4 * (rho * L / A) = 4R.",
        ),
    },
    "c_electric_current": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "Define electric current and explain step-by-step the difference between the direction of "
            "conventional current and the actual flow of electrons in a closed circuit.",
            "Electric current is the rate of flow of electric charges through a cross-section (I = Q / t). "
            "Conventional current flows from positive terminal to negative terminal, while negatively charged electrons "
            "drift from negative terminal to positive terminal.",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "A current of 0.5 A flows through a circuit for 10 minutes. Calculate the total charge "
            "transferred step-by-step.",
            "Time t = 10 min = 600 s. Charge Q = I * t = 0.5 A * 600 s = 300 C.",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "A total of 3.75 x 10^19 electrons flow past a point in a conductor of resistance 8 ohms in 3 seconds. "
            "Calculate the current and the potential difference across the conductor step-by-step "
            "(elementary charge e = 1.6 x 10^-19 C).",
            "Total charge Q = n * e = 3.75e19 * 1.6e-19 C = 6.0 C. "
            "Current I = Q / t = 6.0 C / 3.0 s = 2.0 A. "
            "Potential difference V = I * R = 2.0 A * 8 ohms = 16 V.",
        ),
    },
    "c_potential_difference": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "Define electric potential difference between two points and explain step-by-step what 1 Volt means "
            "in terms of work done and electric charge.",
            "Potential difference V = W / Q is the work done in moving a unit positive charge between two points. "
            "1 Volt is the potential difference when 1 Joule of work is done to move 1 Coulomb of charge.",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "How much work is done in moving a charge of 4 C across two points having a potential difference of 12 V? "
            "Show your step-by-step calculation.",
            "Work done W = V * Q = 12 V * 4 C = 48 Joules.",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "A battery delivers 720 J of energy to move 60 C of charge through a circuit in 15 seconds. "
            "Calculate the potential difference of the battery, the current flowing, and the electric power delivered step-by-step.",
            "Potential difference V = W / Q = 720 J / 60 C = 12 V. "
            "Current I = Q / t = 60 C / 15 s = 4 A. "
            "Power P = V * I = 12 V * 4 A = 48 W (or P = W / t = 720 J / 15 s = 48 W).",
        ),
    },
    "c_resistance_series_parallel": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "Explain step-by-step why the current remains constant through all resistors in series, and why "
            "connecting resistors in parallel reduces total equivalent resistance.",
            "In series, conservation of charge requires every charge to pass through all resistors sequentially, "
            "so current is identical. In parallel, each resistor adds an alternate branch for charge flow, "
            "increasing total conductance and reducing total equivalent resistance (1/Req = 1/R1 + 1/R2).",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "Two resistors of 6 ohms and 12 ohms are connected in parallel. "
            "Calculate the equivalent resistance step-by-step.",
            "1/Req = 1/6 + 1/12 = (2 + 1) / 12 = 3/12 = 1/4. Therefore, Req = 4 ohms.",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "Two resistors of 6 ohms and 12 ohms are connected in parallel, and this combination is connected "
            "in series with a 4 ohm resistor and a 16 V source. "
            "Calculate the total circuit resistance, main current, and current through the 6 ohm branch step-by-step.",
            "Parallel combination: 1/Rp = 1/6 + 1/12 = 3/12 => Rp = 4 ohms. "
            "Total circuit resistance: R_total = Rp + R_series = 4 + 4 = 8 ohms. "
            "Main current: I_total = V / R_total = 16 V / 8 ohms = 2 A. "
            "Voltage across parallel branch: Vp = I_total * Rp = 2 A * 4 ohms = 8 V. "
            "Current through 6 ohm resistor: I_6 = Vp / 6 = 8 V / 6 ohms = 1.33 A.",
        ),
    },
    "c_refraction_lenses": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "Explain step-by-step the sign conventions for a thin concave lens and state why its focal length "
            "is always considered negative in the lens formula.",
            "By Cartesian sign convention, distances opposite to incident light (left of optical centre) are negative. "
            "The principal focus of a concave lens is virtual and lies on the incident side, so focal length f is negative. "
            "The lens formula is 1/f = 1/v - 1/u.",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "A concave lens has a focal length of 15 cm. At what distance should an object be placed to form "
            "an image 10 cm from the lens? Solve step-by-step.",
            "Concave lens: f = -15 cm, virtual image v = -10 cm. "
            "Using lens formula 1/f = 1/v - 1/u: 1/u = 1/v - 1/f = 1/(-10) - 1/(-15) = -1/10 + 1/15 = -1/30. "
            "Therefore, object distance u = -30 cm (30 cm in front of the lens).",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "A convex lens of focal length 20 cm forms a real image three times the size of an object. "
            "Calculate the object distance, image distance, and optical power of the lens step-by-step.",
            "For a real image formed by a convex lens, magnification m = v / u = -3, so v = -3u. "
            "Using 1/f = 1/v - 1/u: 1/20 = 1/(-3u) - 1/u = -4 / (3u) => 3u = -80 => u = -80/3 cm = -26.67 cm. "
            "Image distance v = -3u = 80 cm. "
            "Power P = 1 / f(in meters) = 1 / 0.20 m = +5.0 Dioptres.",
        ),
    },
    "c_mirror_formula": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "State the mirror formula and explain step-by-step the Cartesian sign conventions applied "
            "to object distance, image distance, and focal length for a concave mirror.",
            "The mirror formula is 1/f = 1/v + 1/u. Distances measured against incident light (in front of mirror) "
            "are negative: object distance u is always negative, concave mirror focal length f is negative, "
            "and real inverted images have negative v while virtual upright images behind the mirror have positive v.",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "A convex mirror has a radius of curvature of 3.0 m. If an object is placed at 5.0 m from the mirror, "
            "find the position of the image step-by-step.",
            "Focal length f = R / 2 = +3.0 / 2 = +1.5 m. Object distance u = -5.0 m. "
            "Using 1/f = 1/v + 1/u: 1/v = 1/f - 1/u = 1/1.5 - 1/(-5.0) = 2/3 + 1/5 = 13/15. "
            "Therefore, v = +15/13 m = +1.15 m (virtual image behind the mirror).",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "An object 5.0 cm tall is placed 20.0 cm in front of a concave mirror of focal length 15.0 cm. "
            "Determine the position, size, and nature of the image step-by-step.",
            "Given u = -20.0 cm, f = -15.0 cm, h = 5.0 cm. "
            "1/v = 1/f - 1/u = 1/(-15) - 1/(-20) = -1/15 + 1/20 = -1/60 => v = -60.0 cm (real, in front). "
            "Magnification m = -v / u = -(-60) / (-20) = -3. "
            "Image height h' = m * h = -3 * 5.0 cm = -15.0 cm (real, inverted, magnified).",
        ),
    },
    "c_magnetic_fields": {
        DifficultyLevel.CONCEPTUAL_LEVEL_1: (
            "Explain step-by-step why magnetic field lines form continuous closed loops and why two magnetic field lines "
            "can never intersect each other.",
            "Magnetic field lines emerge from the North pole and enter the South pole outside a magnet, "
            "continuing from South to North inside, forming closed continuous loops because isolated magnetic monopoles do not exist. "
            "Two lines never intersect because the compass needle at the intersection would have to point in two different directions at once, which is physically impossible.",
        ),
        DifficultyLevel.APPLICATION_LEVEL_2: (
            "Explain step-by-step how to find the direction of magnetic field lines around a straight vertical wire "
            "carrying current upward using the Right-Hand Thumb Rule.",
            "Imagine holding the straight wire with the right hand so the thumb points upward in the direction of the current. "
            "The curled fingers encircle the wire in an anticlockwise direction (viewed from above), which is the direction of the magnetic field lines.",
        ),
        DifficultyLevel.CALCULATION_LEVEL_3: (
            "A proton enters a uniform magnetic field of 0.2 T perpendicularly at a speed of 4.0 x 10^6 m/s. "
            "Calculate the magnetic force acting on the proton step-by-step and determine the work done by this force "
            "(proton charge e = 1.6 x 10^-19 C).",
            "Magnetic force F = q * v * B * sin(theta). Since theta = 90 degrees, sin(90) = 1. "
            "F = 1.6e-19 C * 4.0e6 m/s * 0.2 T * 1 = 1.28 x 10^-13 N. "
            "The magnetic force acts perpendicular to the instantaneous velocity (direction of motion) at every instant. "
            "Therefore, work done W = F * d * cos(90) = 0 Joules.",
        ),
    },
}


class QuestionSelector:
    """Selects targeted concept and calibrates question difficulty within learner's ZPD."""

    def __init__(self, curriculum_graph: CurriculumGraph) -> None:
        self.curriculum_graph = curriculum_graph

    def calibrate_difficulty(self, mastery_p_l: float) -> DifficultyLevel:
        """Calibrate question difficulty according to mastery level P(L).

        - P(L) < 0.40 -> CONCEPTUAL_LEVEL_1
        - 0.40 <= P(L) < 0.70 -> APPLICATION_LEVEL_2
        - P(L) >= 0.70 -> CALCULATION_LEVEL_3
        """
        if mastery_p_l < 0.40:
            return DifficultyLevel.CONCEPTUAL_LEVEL_1
        if mastery_p_l < 0.70:
            return DifficultyLevel.APPLICATION_LEVEL_2
        return DifficultyLevel.CALCULATION_LEVEL_3

    def select_next_target(
        self,
        mastery_levels: dict[str, float],
        active_misconceptions: dict[str, list[str]] | None = None,
    ) -> TargetedQuestionTarget:
        """Select next learning target concept in the Zone of Proximal Development (ZPD).

        1. Identifies concepts with P(L) >= 0.70 as mastered prerequisites.
        2. Computes the eligible frontier DAG concepts whose prerequisites are satisfied.
        3. Prioritizes concepts with active detected misconceptions, then lowest P(L) (furthest from threshold).
        4. Calibrates difficulty level and returns TargetedQuestionTarget.
        """
        misconceptions_map = active_misconceptions or {}

        # 1. Mastered prerequisites: P(L) >= 0.70
        mastered_ids = {cid for cid, score in mastery_levels.items() if score >= 0.70}

        # 2. Eligible frontier from curriculum DAG
        frontier = self.curriculum_graph.get_eligible_frontier(mastered_ids)

        # 3. Restrict candidates to known frontier concepts
        # When mastery_levels is provided, candidates present in mastery_levels are prioritized
        candidates_in_mastery = [cid for cid in frontier if cid in mastery_levels]
        # Filter concepts where P(L) < 0.75
        weak_candidates = [cid for cid in candidates_in_mastery if mastery_levels[cid] < 0.75]

        if weak_candidates:
            pool = weak_candidates
        elif candidates_in_mastery:
            pool = candidates_in_mastery
        elif frontier:
            pool = list(frontier)
        else:
            # Fallback if whole frontier is empty: select from all graph concepts
            pool = list(self.curriculum_graph.concepts.keys())

        if not pool:
            raise ValueError("Curriculum graph has no concepts available for target selection")

        # Rank candidates:
        # Highest active misconception count first (-len), then lowest P(L) (highest 0.75 - p_l)
        def _rank_key(cid: str) -> tuple[int, float, str]:
            misc_count = len(misconceptions_map.get(cid, []))
            p_l = mastery_levels.get(cid, 0.0)
            return (-misc_count, p_l, cid)

        selected_id = min(pool, key=_rank_key)

        # Retrieve concept details
        concept_data = self.curriculum_graph.get_concept(selected_id)
        concept_name = concept_data.get("name", selected_id)

        p_l = mastery_levels.get(selected_id, 0.0)
        difficulty = self.calibrate_difficulty(p_l)
        concept_misconceptions = list(misconceptions_map.get(selected_id, []))

        return TargetedQuestionTarget(
            concept_id=selected_id,
            concept_name=concept_name,
            difficulty=difficulty,
            active_misconceptions=concept_misconceptions,
        )

    def generate_question(self, target: TargetedQuestionTarget) -> dict[str, Any]:
        """Generate or select a calibrated question targeting the concept and difficulty level.

        Always requests step-by-step reasoning from the student.
        """
        concept_id = target.concept_id
        difficulty = target.difficulty

        # Check exemplar question bank
        if concept_id in _QUESTION_BANK and difficulty in _QUESTION_BANK[concept_id]:
            prompt, expected_answer = _QUESTION_BANK[concept_id][difficulty]
        else:
            # Dynamic calibrated question generator for any curriculum concept
            name = target.concept_name
            if difficulty == DifficultyLevel.CONCEPTUAL_LEVEL_1:
                prompt = (
                    f"Explain the fundamental principles and definition of {name} step-by-step. "
                    "Provide qualitative reasoning explaining why these core laws hold."
                )
                expected_answer = (
                    f"Clear step-by-step qualitative explanation of {name}, defining key terms "
                    "and fundamental physical principles."
                )
            elif difficulty == DifficultyLevel.APPLICATION_LEVEL_2:
                prompt = (
                    f"State the governing formula for {name} and apply it step-by-step to calculate "
                    "the primary quantity for standard operating parameters. Show all intermediate substitution steps."
                )
                expected_answer = (
                    f"Step-by-step formula substitution and solution for {name} with correct units."
                )
            else:  # CALCULATION_LEVEL_3
                prompt = (
                    f"Solve a multi-step analytical problem on {name}. Show all intermediate derivations, "
                    "circuit/ray relationships, and complete step-by-step reasoning."
                )
                expected_answer = (
                    f"Complete multi-step calculation for {name} with rigorous intermediate steps and final result."
                )

        # If there are active misconceptions, supplement the prompt to diagnose/remediate them
        if target.active_misconceptions:
            prompt += (
                f"\nNote: Explain your step-by-step reasoning clearly, detailing how the underlying physical "
                f"laws apply rather than relying on intuitive shortcuts."
            )

        targeted_q = TargetedQuestion(
            concept_id=target.concept_id,
            concept_name=target.concept_name,
            difficulty=target.difficulty,
            prompt=prompt,
            expected_answer=expected_answer,
            misconception_targets=list(target.active_misconceptions),
            question_type="open",
        )
        return targeted_q.to_dict()


__all__ = [
    "DifficultyLevel",
    "TargetedQuestionTarget",
    "TargetedQuestion",
    "QuestionSelector",
]
