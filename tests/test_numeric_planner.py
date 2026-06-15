from __future__ import annotations

import unittest

from evigraph.evidence_graph import EvidenceGraph
from evigraph.generator import SupportOnlyGenerator
from evigraph.numeric_planner import NumericPlannerFallback
from evigraph.schema import EvidenceNode


class FakePlanClient:
    def __init__(self, plan: dict) -> None:
        self.payload = plan

    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict:
        return self.payload


class FailingPlanClient:
    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict:
        raise RuntimeError("planner unavailable")


class NumericPlannerFallbackTest(unittest.TestCase):
    def test_executes_fake_llm_ratio_plan_against_context_numbers(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="evidence",
                node_type="text",
                content="The total purchase price was $320.1 million and IPR&D was $190.0 million.",
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "ratio",
                    "node_id": "evidence",
                    "target": {"label": "ipr&d", "value": 190.0},
                    "base": {"label": "total purchase price", "value": 320.1},
                    "scale": "percent",
                }
            )
        )

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "what percentage of the total purchase price was represented by ipr&d?",
            graph,
        )

        self.assertEqual(answer.text, "59.4%")
        self.assertIn("planned_ratio", answer.calculations[0])

    def test_rejects_plan_values_not_present_in_context(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="evidence",
                node_type="text",
                content="The total purchase price was $320.1 million and IPR&D was $190.0 million.",
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "ratio",
                    "node_id": "evidence",
                    "target": {"label": "ipr&d", "value": 191.0},
                    "base": {"label": "total purchase price", "value": 320.1},
                    "scale": "percent",
                }
            )
        )

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "what percentage of the total purchase price was represented by ipr&d?",
            graph,
        )

        self.assertNotIn("planned_ratio", answer.calculations)

    def test_strict_mode_raises_planner_errors(self) -> None:
        planner = NumericPlannerFallback(FailingPlanClient(), strict=True)

        with self.assertRaises(RuntimeError):
            planner.answer("query", [("node", "value 1")])


if __name__ == "__main__":
    unittest.main()
