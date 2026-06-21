from __future__ import annotations

import unittest

from evigraph.table_executor import TableOperationExecutor


class TableOperationExecutorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = TableOperationExecutor()

    def test_sum(self) -> None:
        result = self.executor.sum([1.0, 2.0, 3.0])
        self.assertIsNotNone(result)
        self.assertEqual(result.value, 6.0)

    def test_product(self) -> None:
        result = self.executor.product([2.5, 4.0, 365.0])
        self.assertIsNotNone(result)
        self.assertEqual(result.value, 3650.0)

    def test_select_rows(self) -> None:
        rows = [
            ["net sales", "100", "90"],
            ["operating income", "20", "15"],
            ["total assets", "300", "280"],
        ]
        selected = self.executor.select_rows(["metric", "2023", "2022"], rows, ["operating", "income"])
        self.assertEqual(selected, [["operating income", "20", "15"]])

    def test_select_column(self) -> None:
        rows = [
            ["net sales", "100", "90"],
            ["operating income", "20", "15"],
        ]
        selected = self.executor.select_column(["metric", "2023", "2022"], rows, ["2023"])
        self.assertEqual(selected, ["100", "20"])

    def test_resolve_value_from_markdown_table_selector(self) -> None:
        context = """
| metric | 2023 | 2022 |
| --- | ---: | ---: |
| net sales | 100 | 90 |
| operating income | 20 | 15 |
"""

        value = self.executor.resolve_value({"label": "operating income", "year": "2023"}, context)

        self.assertIsNotNone(value)
        self.assertEqual(value.value, 20.0)
        self.assertEqual(value.row_label, "operating income")
        self.assertEqual(value.column_label, "2023")

    def test_resolve_value_accepts_row_and_column_terms(self) -> None:
        context = """
| metric | current year | prior year |
| --- | ---: | ---: |
| weighted average shares | 1,250 | 1,000 |
"""

        value = self.executor.resolve_value(
            {"row_terms": ["average", "shares"], "column_terms": ["current"]},
            context,
        )

        self.assertIsNotNone(value)
        self.assertEqual(value.value, 1250.0)
        self.assertEqual(value.column_label, "current year")

    def test_resolve_explicit_value_can_be_supported_by_question_text(self) -> None:
        value = self.executor.resolve_value(
            {"label": "days in year", "value": 365},
            "The table reports daily average volume.",
            support_text="What is the annualized amount using 365 days?",
        )

        self.assertIsNotNone(value)
        self.assertEqual(value.value, 365.0)

    def test_resolve_value_disambiguates_period_in_column_header(self) -> None:
        context = """
| metric | three months ended 2023 | twelve months ended 2023 |
| --- | ---: | ---: |
| revenue | 30 | 120 |
"""

        value = self.executor.resolve_value(
            {"label": "revenue", "year": "2023", "period": "three months ended"},
            context,
        )

        self.assertIsNotNone(value)
        self.assertEqual(value.value, 30.0)
        self.assertEqual(value.column_label, "three months ended 2023")
        self.assertEqual(value.period_label, "three months ended")

    def test_resolve_value_disambiguates_period_in_row_label(self) -> None:
        context = """
| metric | amount |
| --- | ---: |
| revenue three months ended | 30 |
| revenue twelve months ended | 120 |
"""

        value = self.executor.resolve_value(
            {"label": "revenue", "column": "amount", "period": "twelve months ended"},
            context,
        )

        self.assertIsNotNone(value)
        self.assertEqual(value.value, 120.0)
        self.assertEqual(value.row_label, "revenue twelve months ended")

    def test_resolve_value_uses_year_in_row_label_for_single_value_waterfall(self) -> None:
        context = """
| metric | amount |
| --- | ---: |
| 2007 net revenue | 231.0 |
| rider revenue | 3.9 |
| 2008 net revenue | 252.7 |
"""

        value = self.executor.resolve_value({"row_terms": ["net", "revenue"], "year": "2008"}, context)

        self.assertIsNotNone(value)
        self.assertEqual(value.value, 252.7)
        self.assertEqual(value.row_label, "2008 net revenue")
        self.assertEqual(value.column_label, "amount")

    def test_difference(self) -> None:
        result = self.executor.difference(173.2, 171.5)
        self.assertAlmostEqual(result.value, 1.7)

    def test_ratio(self) -> None:
        result = self.executor.ratio(637, 5)
        self.assertIsNotNone(result)
        self.assertEqual(result.value, 127.4)

    def test_ratio_rejects_zero_denominator(self) -> None:
        self.assertIsNone(self.executor.ratio(1, 0))

    def test_percent_change(self) -> None:
        result = self.executor.percent_change(766451, 204079)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.value, 275.6, places=1)

    def test_average(self) -> None:
        result = self.executor.average([45, 45, 45, 45, 44])
        self.assertIsNotNone(result)
        self.assertEqual(result.value, 44.8)


if __name__ == "__main__":
    unittest.main()
