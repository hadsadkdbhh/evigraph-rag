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
