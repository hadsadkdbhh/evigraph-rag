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
            "compute the acquisition allocation for ipr&d relative to total purchase price",
            graph,
        )

        self.assertEqual(answer.text, "59.4%")
        self.assertIn("planned_ratio", answer.calculations[0])

    def test_executes_selector_plan_against_markdown_table_cells(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="table",
                content=(
                    "| metric | 2023 | 2022 |\n"
                    "| --- | ---: | ---: |\n"
                    "| revenue | 125 | 100 |\n"
                    "| operating income | 30 | 20 |\n"
                ),
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "percent_change",
                    "node_id": "table",
                    "target": {"label": "revenue", "year": "2023"},
                    "base": {"label": "revenue", "year": "2022"},
                    "scale": "percent",
                }
            )
        )

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "compute the planned revenue movement from prior year to current year",
            graph,
        )

        self.assertEqual(answer.text, "25.0%")
        self.assertIn("planned_percent_change", answer.calculations[0])
        self.assertIn("revenue/2023", answer.calculations[0])

    def test_executes_product_plan_with_question_supported_constant(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="table",
                content=(
                    "| metric | amount |\n"
                    "| --- | ---: |\n"
                    "| average daily volume | 2.5 |\n"
                    "| average price | 4.0 |\n"
                ),
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "product",
                    "node_id": "table",
                    "values": [
                        {"label": "average daily volume", "column": "amount"},
                        {"label": "average price", "column": "amount"},
                        {"label": "days in year", "value": 365},
                    ],
                }
            )
        )

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "compute the annualized traded value using 365 days",
            graph,
        )

        self.assertEqual(answer.text, "3650")
        self.assertIn("planned_product", answer.calculations[0])
        self.assertIn("average daily volume/amount", answer.calculations[0])

    def test_executes_percent_of_increase_plan(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="table",
                content=(
                    "| metric | 2023 | 2022 |\n"
                    "| --- | ---: | ---: |\n"
                    "| product revenue | 160 | 100 |\n"
                    "| total revenue | 250 | 150 |\n"
                ),
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "percent_of_increase",
                    "node_id": "table",
                    "numerator_target": {"label": "product revenue", "year": "2023"},
                    "numerator_base": {"label": "product revenue", "year": "2022"},
                    "denominator_target": {"label": "total revenue", "year": "2023"},
                    "denominator_base": {"label": "total revenue", "year": "2022"},
                }
            )
        )

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "what percentage of the increase in total revenue came from product revenue?",
            graph,
        )

        self.assertEqual(answer.text, "60%")
        self.assertIn("planned_percent_of_increase", answer.calculations[0])
        self.assertIn("product revenue/2023-product revenue/2022", answer.calculations[0])

    def test_executes_period_disambiguated_percent_change_plan(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="table",
                content=(
                    "| metric | three months ended 2023 | three months ended 2022 | twelve months ended 2023 | twelve months ended 2022 |\n"
                    "| --- | ---: | ---: | ---: | ---: |\n"
                    "| revenue | 30 | 20 | 120 | 80 |\n"
                ),
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "percent_change",
                    "node_id": "table",
                    "target": {"label": "revenue", "year": "2023", "period": "three months ended"},
                    "base": {"label": "revenue", "year": "2022", "period": "three months ended"},
                }
            )
        )

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "compute the planned revenue movement for the three months ended 2023 compared with 2022",
            graph,
        )

        self.assertEqual(answer.text, "50.0%")
        self.assertIn("three months ended", answer.calculations[0])

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
            "compute the acquisition allocation for ipr&d relative to total purchase price",
            graph,
        )

        self.assertNotIn("planned_ratio", answer.calculations)

    def test_strict_mode_raises_planner_errors(self) -> None:
        planner = NumericPlannerFallback(FailingPlanClient(), strict=True)

        with self.assertRaises(RuntimeError):
            planner.answer("query", [("node", "value 1")])


if __name__ == "__main__":
    unittest.main()
