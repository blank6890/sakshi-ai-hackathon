"""Cohort analytics and class gap aggregation service for teacher dashboards."""

from __future__ import annotations

from typing import Any

from deeptutor.learning.curriculum import CurriculumGraph
from deeptutor.learning.misconception import PHYSICS_MISCONCEPTIONS


STUDENT_NAMES_CLASS_10 = [
    "Aarav Sharma",
    "Ananya Patel",
    "Rohan Gupta",
    "Priya Singh",
    "Aditya Verma",
    "Sneha Rao",
    "Vikram Malhotra",
    "Kavya Iyer",
    "Rahul Nair",
    "Neha Joshi",
    "Arjun Reddy",
    "Pooja Das",
    "Devansh Mehta",
    "Tanvi Bhat",
    "Kabir Sen",
    "Isha Chopra",
    "Siddharth Jain",
    "Meera Pillai",
    "Rishi Agarwal",
    "Riya Mukherjee",
    "Karan Kapoor",
    "Anushka Saxena",
    "Manish Pandey",
    "Shruti Deshmukh",
    "Aryan Ghosh",
]

# Base difficulty profile for class 10 physics concepts: (target_class_avg, variance)
# Concepts with lower values represent class-wide knowledge gaps.
CONCEPT_PROFILE: dict[str, float] = {
    "c_reflection_refraction": 0.84,
    "c_spherical_mirrors": 0.72,
    "c_mirror_formula": 0.58,
    "c_refraction_lenses": 0.62,
    "c_lens_formula": 0.44,  # Major Gap
    "c_electric_charge": 0.88,
    "c_electric_current": 0.82,
    "c_potential_difference": 0.69,
    "c_ohms_law": 0.41,  # Major Gap
    "c_resistance_series_parallel": 0.38,  # Major Gap
    "c_joules_heating": 0.65,
    "c_electric_power": 0.52,  # Moderate Gap
    "c_magnetic_fields": 0.76,
    "c_solenoids": 0.49,  # Moderate Gap
    "c_flemings_rules": 0.55,
}

# Misconception assignment rules: which concepts trigger specific misconceptions
# when student mastery is below threshold.
MISCONCEPTION_RULES: list[tuple[str, str, float]] = [
    ("ohm_r_depends_on_v", "c_ohms_law", 0.60),
    ("series_current_consumed", "c_resistance_series_parallel", 0.55),
    ("parallel_resistor_additive", "c_resistance_series_parallel", 0.50),
    ("mirror_lens_formula_confusion", "c_lens_formula", 0.60),
    ("refraction_density_speed", "c_refraction_lenses", 0.55),
    ("electromagnet_charge_flow", "c_solenoids", 0.60),
    ("magnetic_monopole", "c_magnetic_fields", 0.50),
]


def _build_seeded_students() -> list[dict[str, Any]]:
    """Generate 25 deterministic student records with realistic BKT mastery profiles."""
    students: list[dict[str, Any]] = []

    # Student ability offsets: from high achievers (+0.18) to struggling learners (-0.22)
    ability_offsets = [
        0.18, 0.15, 0.14, 0.12, 0.10,
        0.08, 0.06, 0.04, 0.03, 0.01,
        0.00, -0.02, -0.04, -0.05, -0.07,
        -0.09, -0.11, -0.12, -0.14, -0.16,
        -0.18, -0.19, -0.20, -0.21, -0.22,
    ]

    for idx, (name, offset) in enumerate(zip(STUDENT_NAMES_CLASS_10, ability_offsets), start=1):
        student_id = f"stu_{idx:02d}"
        mastery_levels: dict[str, float] = {}

        for c_idx, (cid, base_avg) in enumerate(CONCEPT_PROFILE.items()):
            # Small cyclic variance for distinct individual student patterns
            perturbation = (((idx * 7 + c_idx * 11) % 19) - 9) * 0.012
            raw_val = base_avg + offset + perturbation
            clamped_val = max(0.12, min(0.98, raw_val))
            mastery_levels[cid] = round(clamped_val, 4)

        # Detect active misconceptions based on student's weak concepts
        active_misconceptions: list[str] = []
        for misc_id, trigger_concept, threshold in MISCONCEPTION_RULES:
            if mastery_levels.get(trigger_concept, 1.0) < threshold:
                active_misconceptions.append(misc_id)

        students.append({
            "student_id": student_id,
            "student_name": name,
            "mastery_levels": mastery_levels,
            "active_misconceptions": active_misconceptions,
        })

    return students


class CohortService:
    """Manages cohorts and aggregates concept gaps and student mastery heatmaps."""

    def __init__(self, cohorts: dict[str, dict[str, Any]] | None = None) -> None:
        if cohorts is not None:
            self._cohorts: dict[str, dict[str, Any]] = dict(cohorts)
        else:
            self._cohorts = self._build_default_cohorts()

    @staticmethod
    def _build_default_cohorts() -> dict[str, dict[str, Any]]:
        return {
            "class-10-a": {
                "cohort_id": "class-10-a",
                "cohort_name": "Class 10 - Section A (Physics)",
                "curriculum": "class10_physics",
                "students": _build_seeded_students(),
            },
            "empty-cohort": {
                "cohort_id": "empty-cohort",
                "cohort_name": "Empty Class (Demo)",
                "curriculum": "class10_physics",
                "students": [],
            },
        }

    def _get_concepts(self, curriculum_name: str) -> dict[str, dict[str, Any]]:
        """Retrieve concepts dictionary for the specified curriculum."""
        try:
            graph = CurriculumGraph.load_default(curriculum_name)
            return {
                cid: {
                    "name": data.get("name", cid),
                    "chapter": data.get("chapter", ""),
                }
                for cid, data in graph.concepts.items()
            }
        except Exception:
            # Fallback to predefined concept profile
            return {
                cid: {"name": cid.replace("c_", "").replace("_", " ").title(), "chapter": "Physics"}
                for cid in CONCEPT_PROFILE
            }

    def list_cohorts(self) -> list[dict[str, Any]]:
        """List all available cohorts."""
        return [
            {
                "cohort_id": c["cohort_id"],
                "cohort_name": c["cohort_name"],
                "total_students": len(c["students"]),
                "curriculum": c.get("curriculum", "class10_physics"),
            }
            for c in self._cohorts.values()
        ]

    def get_cohort(self, cohort_id: str) -> dict[str, Any]:
        """Fetch raw cohort record or raise KeyError."""
        if cohort_id not in self._cohorts:
            raise KeyError(f"Cohort '{cohort_id}' not found")
        return self._cohorts[cohort_id]

    def get_cohort_summary(self, cohort_id: str) -> dict[str, Any]:
        """Compute aggregated cohort metrics: average mastery, ranked top gaps, misconceptions."""
        cohort = self.get_cohort(cohort_id)
        students = cohort["students"]
        total_students = len(students)
        curriculum_name = cohort.get("curriculum", "class10_physics")
        concepts = self._get_concepts(curriculum_name)

        if total_students == 0:
            return {
                "cohort_id": cohort_id,
                "cohort_name": cohort["cohort_name"],
                "total_students": 0,
                "class_average_mastery": 0.0,
                "top_gaps": [],
                "frequent_misconceptions": [],
            }

        # Calculate concept gaps
        top_gaps: list[dict[str, Any]] = []
        total_mastery_sum = 0.0
        total_evaluations = 0

        for cid, c_info in concepts.items():
            mastery_vals = [s["mastery_levels"].get(cid, 0.0) for s in students]
            concept_sum = sum(mastery_vals)
            avg_mastery = round(concept_sum / total_students, 4)
            struggling_count = sum(1 for m in mastery_vals if m < 0.60)
            struggling_pct = round((struggling_count / total_students) * 100.0, 1)

            total_mastery_sum += concept_sum
            total_evaluations += total_students

            # Map misconceptions relevant to this concept held by cohort students
            concept_misconceptions: list[dict[str, Any]] = []
            for misc_id, meta in PHYSICS_MISCONCEPTIONS.items():
                if cid in meta.get("concept_ids", []):
                    affected_count = sum(
                        1 for s in students if misc_id in s.get("active_misconceptions", [])
                    )
                    if affected_count > 0:
                        concept_misconceptions.append({
                            "misconception_id": misc_id,
                            "name": meta.get("name", misc_id),
                            "count": affected_count,
                            "description": meta.get("description", ""),
                        })

            concept_misconceptions.sort(key=lambda m: m["count"], reverse=True)

            top_gaps.append({
                "concept_id": cid,
                "concept_name": c_info["name"],
                "chapter": c_info.get("chapter", ""),
                "average_mastery": avg_mastery,
                "struggling_student_count": struggling_count,
                "struggling_percentage": struggling_pct,
                "common_misconceptions": concept_misconceptions,
            })

        # Rank gaps ascending: lowest mastery (worst gap) first
        top_gaps.sort(key=lambda g: g["average_mastery"])

        class_avg_mastery = (
            round(total_mastery_sum / total_evaluations, 4) if total_evaluations > 0 else 0.0
        )

        # Aggregate frequent misconceptions across the cohort
        misc_counts: dict[str, list[str]] = {}
        for s in students:
            for misc_id in s.get("active_misconceptions", []):
                misc_counts.setdefault(misc_id, []).append(s["student_name"])

        frequent_misconceptions: list[dict[str, Any]] = []
        for misc_id, student_list in misc_counts.items():
            meta = PHYSICS_MISCONCEPTIONS.get(misc_id, {})
            frequent_misconceptions.append({
                "misconception_id": misc_id,
                "name": meta.get("name", misc_id),
                "description": meta.get("description", ""),
                "remedial_feedback": meta.get("remedial_feedback", ""),
                "concept_ids": meta.get("concept_ids", []),
                "count": len(student_list),
                "affected_students": student_list,
            })

        frequent_misconceptions.sort(key=lambda m: m["count"], reverse=True)

        return {
            "cohort_id": cohort_id,
            "cohort_name": cohort["cohort_name"],
            "total_students": total_students,
            "class_average_mastery": class_avg_mastery,
            "top_gaps": top_gaps,
            "frequent_misconceptions": frequent_misconceptions,
        }

    def get_cohort_heatmap(self, cohort_id: str) -> dict[str, Any]:
        """Return student x concept mastery matrix for heatmap visualization."""
        cohort = self.get_cohort(cohort_id)
        students_raw = cohort["students"]
        curriculum_name = cohort.get("curriculum", "class10_physics")
        concepts_raw = self._get_concepts(curriculum_name)

        concepts_list = [
            {
                "concept_id": cid,
                "concept_name": info["name"],
                "chapter": info.get("chapter", ""),
            }
            for cid, info in concepts_raw.items()
        ]

        if not students_raw:
            return {
                "cohort_id": cohort_id,
                "cohort_name": cohort["cohort_name"],
                "students": [],
                "concepts": concepts_list,
                "matrix": {},
            }

        students_list: list[dict[str, Any]] = []
        matrix: dict[str, dict[str, float]] = {}

        for s in students_raw:
            s_id = s["student_id"]
            m_levels = {
                cid: round(float(s["mastery_levels"].get(cid, 0.0)), 4)
                for cid in concepts_raw
            }
            overall = (
                round(sum(m_levels.values()) / len(m_levels), 4) if m_levels else 0.0
            )

            students_list.append({
                "student_id": s_id,
                "student_name": s["student_name"],
                "overall_mastery": overall,
            })
            matrix[s_id] = m_levels

        return {
            "cohort_id": cohort_id,
            "cohort_name": cohort["cohort_name"],
            "students": students_list,
            "concepts": concepts_list,
            "matrix": matrix,
        }

    def get_cohort_gaps(self, cohort_id: str) -> list[dict[str, Any]]:
        """Return ranked weak concepts for the cohort."""
        summary = self.get_cohort_summary(cohort_id)
        return summary["top_gaps"]


_default_cohort_service: CohortService | None = None


def get_cohort_service() -> CohortService:
    """Return singleton CohortService instance."""
    global _default_cohort_service
    if _default_cohort_service is None:
        _default_cohort_service = CohortService()
    return _default_cohort_service
