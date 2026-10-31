"""Curriculum prerequisite DAG and mastery frontier calculation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx


class CurriculumGraph:
    """Directed acyclic graph representing concept prerequisites."""

    def __init__(self, concepts: dict[str, dict[str, Any]]) -> None:
        self.concepts: dict[str, dict[str, Any]] = concepts
        self._graph = nx.DiGraph()
        for cid in self.concepts:
            self._graph.add_node(cid)
        for cid, data in self.concepts.items():
            for prereq in data.get("prerequisites", []):
                self._graph.add_edge(prereq, cid)
        self.validate_dag()

    @classmethod
    def from_dict(cls, data: dict[str, Any] | list[dict[str, Any]]) -> CurriculumGraph:
        """Create CurriculumGraph from dictionary or list of concepts."""
        raw_concepts = data if isinstance(data, list) else (data.get("concepts", []) if data else [])
        concepts = {c["id"]: c for c in raw_concepts}
        return cls(concepts)

    @classmethod
    def load_default(cls, name: str) -> CurriculumGraph:
        """Load default curriculum JSON by name from deeptutor/data/curriculum/{name}.json."""
        path = Path(__file__).resolve().parent.parent / "data" / "curriculum" / f"{name}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Curriculum data not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def validate_dag(self) -> None:
        """Verify graph is acyclic; raises ValueError if cycles exist."""
        if not nx.is_directed_acyclic_graph(self._graph):
            cycles = list(nx.simple_cycles(self._graph))
            raise ValueError(f"Prerequisite cycle detected: {cycles}")

    def get_concept(self, concept_id: str) -> dict[str, Any]:
        """Return concept dictionary by concept_id."""
        if concept_id not in self.concepts:
            raise KeyError(f"Concept '{concept_id}' not found in curriculum graph")
        return self.concepts[concept_id]

    def get_prerequisites(self, concept_id: str) -> list[str]:
        """Return prerequisite concept IDs for given concept_id."""
        concept = self.get_concept(concept_id)
        return list(concept.get("prerequisites", []))

    def get_eligible_frontier(self, mastered_ids: set[str]) -> set[str]:
        """Return concepts whose prerequisites are all in mastered_ids and are not yet mastered."""
        mastered = set(mastered_ids) if mastered_ids else set()
        frontier: set[str] = set()
        for cid, concept in self.concepts.items():
            if cid in mastered:
                continue
            prereqs = set(concept.get("prerequisites", []))
            if prereqs.issubset(mastered):
                frontier.add(cid)
        return frontier

    def topological_sort(self) -> list[str]:
        """Return concepts in topologically sorted order."""
        return list(nx.topological_sort(self._graph))
