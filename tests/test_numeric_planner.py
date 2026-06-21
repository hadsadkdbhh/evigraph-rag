from __future__ import annotations

import unittest

from evigraph.evidence_graph import EvidenceGraph
from evigraph.generator import SupportOnlyGenerator
from evigraph.numeric_planner import HeuristicNumericPlanClient, NumericPlannerFallback
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

    def test_falls_back_to_heuristic_after_planner_error(self) -> None:
        context = (
            "| metric | three months ended 2023 | three months ended 2022 |\n"
            "| --- | ---: | ---: |\n"
            "| revenue | 30 | 20 |\n"
        )
        planner = NumericPlannerFallback(
            FailingPlanClient(),
            strict=False,
            fallback_client=HeuristicNumericPlanClient(),
            disable_primary_after_error=True,
        )

        answer = planner.answer(
            "what was the percentage increase in revenue for the three months ended 2023 compared with 2022?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "50.0%")
        self.assertTrue(planner.primary_disabled)

    def test_heuristic_plans_ratio_percent_with_numerator_and_denominator_rows(self) -> None:
        context = (
            "| asset class | 2011 |\n"
            "| --- | ---: |\n"
            "| mutual funds | 17187 |\n"
            "| total investment | 26410 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "what percentage of total investment was represented by mutual funds in 2011?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "65.1%")
        self.assertIn("planned_ratio", answer.calculation)

    def test_heuristic_plans_percent_of_base_that_was_target_as_ratio(self) -> None:
        context = (
            "| millions of dollars | dec . 31 2008 | dec . 31 2007 |\n"
            "| --- | ---: | ---: |\n"
            "| accrued wages and vacation | 367 | 394 |\n"
            "| total accounts payable and other current liabilities | 2560 | 2902 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "as of december 31 , 2008 what was the percent of the total accounts payable and other liabilities that was accrued wages and vacation",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "14.3%")
        self.assertIn("planned_ratio", answer.calculation)
        self.assertIn("accrued wages and vacation/dec . 31 2008", answer.calculation)

    def test_percent_question_rejects_sum_plan(self) -> None:
        context = (
            "| millions of dollars | dec . 31 2008 | dec . 31 2007 |\n"
            "| --- | ---: | ---: |\n"
            "| accrued wages and vacation | 367 | 394 |\n"
            "| total accounts payable and other current liabilities | 2560 | 2902 |\n"
        )
        planner = NumericPlannerFallback(
            FakePlanClient(
                {
                    "operation": "sum",
                    "node_id": "table",
                    "values": [{"label": "accrued wages and vacation", "year": "2008"}],
                }
            )
        )

        answer = planner.answer(
            "as of december 31 , 2008 what was the percent of the total accounts payable and other liabilities that was accrued wages and vacation",
            [("table", context)],
        )

        self.assertIsNone(answer)

    def test_heuristic_plans_average_over_year_range(self) -> None:
        context = (
            "| metric | 2008 | 2009 | 2010 |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| stock based compensation expense | 180 | 210 | 264 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "what was the average stock based compensation expense from 2008 to 2010?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "218")
        self.assertIn("planned_average", answer.calculation)

    def test_heuristic_plans_sum_over_listed_years(self) -> None:
        context = (
            "| metric | 2004 | 2005 | 2006 |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| matching buy sell volumes | 10 | 20 | 30 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "what was the total matching buy sell volumes in 2006, 2005 and 2004?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "60")
        self.assertIn("planned_sum", answer.calculation)

    def test_heuristic_complement_percent(self) -> None:
        context = (
            "| metric | percent |\n"
            "| --- | ---: |\n"
            "| leased | 35 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "what percentage of stores were not leased?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "65%")
        self.assertIn("planned_complement_percent", answer.calculation)

    def test_local_planner_config_does_not_require_llm_environment(self) -> None:
        planner = NumericPlannerFallback.from_config(
            {
                "enabled": True,
                "llm_provider": "heuristic",
                "strict": False,
            }
        )

        self.assertIsNotNone(planner)
        self.assertIsInstance(planner.plan_client, HeuristicNumericPlanClient)

    def test_heuristic_due_after_uses_thereafter_over_total_columns(self) -> None:
        context = (
            "| commitment | 2021 | thereafter | total |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| long-term debt | 71 | 631 | 710 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "what percentage of long-term debt is due after 2021?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "88.9%")
        self.assertIn("planned_ratio", answer.calculation)
        self.assertIn("thereafter", answer.calculation)

    def test_heuristic_ratio_compared_to_uses_distinct_operands(self) -> None:
        context = (
            "| metric | 2018 | 2017 | 2016 |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| htm investment securities period-end | 31434 | 47733 | 50168 |\n"
            "| investment securities portfolio period-end | 260115 | 247980 | 286838 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "in 2017 what was the ratio of the htm investment securities period-end compared to investment securities portfolio period-end",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "0.2")
        self.assertIn("htm investment securities period-end/2017", answer.calculation)
        self.assertIn("investment securities portfolio period-end/2017", answer.calculation)

    def test_heuristic_total_amount_without_year_list_is_lookup_not_sum(self) -> None:
        context = (
            "| item | value |\n"
            "| --- | ---: |\n"
            "| net tangible assets obtained through the acquisition | 62154 |\n"
            "| customer-related intangible assets | 42721 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "what are the total amount of net tangible assets obtained through the acquisition?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "62154")
        self.assertIn("planned_lookup", answer.calculation)

    def test_heuristic_total_sum_drops_total_as_row_term(self) -> None:
        context = (
            "| metric | 2004 | 2005 | 2006 |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| matching buy sell volumes | 50 | 59 | 63 |\n"
            "| total shipments | 1400 | 1455 | 1425 |\n"
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = planner.answer(
            "in tpd , what were total matching buy/sell volumes in 2006 , 2005 and 2004?",
            [("table", context)],
        )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.text, "172")
        self.assertIn("matching buy sell volumes/2006", answer.calculation)


if __name__ == "__main__":
    unittest.main()
