from __future__ import annotations

import unittest

from evigraph.retrieval_portfolio import build_portfolio_rows, choose_row


class RetrievalPortfolioTest(unittest.TestCase):
    def test_keeps_primary_when_primary_has_numeric_calculation(self) -> None:
        primary = self._row(prediction="17.0%", calculation="percent_change = 17.0", answer_supported="True")
        candidate = self._row(prediction="18.0%", calculation="percent_change = 18.0", answer_supported="True")

        decision = choose_row(primary, candidate)

        self.assertEqual(decision.source, "primary")
        self.assertEqual(decision.reason, "primary_not_fallback")

    def test_switches_when_primary_fallback_and_candidate_numeric_calculation(self) -> None:
        primary = self._row(prediction="Based on the selected evidence: long prose answer", calculation="")
        candidate = self._row(prediction="17.0%", calculation="percent_change = 17.0", answer_supported="True")

        decision = choose_row(primary, candidate)

        self.assertEqual(decision.source, "candidate")
        self.assertEqual(decision.reason, "primary_fallback_candidate_numeric_calculation")

    def test_strict_policy_requires_verifier_support(self) -> None:
        primary = self._row(prediction="Based on the selected evidence: long prose answer", calculation="")
        candidate = self._row(prediction="17.0%", calculation="percent_change = 17.0", answer_supported="True")
        candidate["row_operation_grounded"] = "False"

        decision = choose_row(primary, candidate, policy="strict_supported_fallback")

        self.assertEqual(decision.source, "primary")
        self.assertIn("row_operation_grounded", decision.reason)

    def test_selection_does_not_consult_accuracy_or_gold_columns(self) -> None:
        primary = self._row(
            prediction="Based on the selected evidence: long prose answer",
            calculation="",
            accuracy="1.0",
            answer="gold",
        )
        candidate = self._row(
            prediction="17.0%",
            calculation="percent_change = 17.0",
            accuracy="0.0",
            answer="gold",
            answer_supported="True",
        )

        rows = build_portfolio_rows([primary], [candidate])

        self.assertEqual(rows[0]["portfolio_choice"], "neural_hybrid")

    def _row(self, **overrides: str) -> dict[str, str]:
        row = {
            "dataset": "finqa_test",
            "id": "case-1",
            "method": "full_evigraph",
            "prediction": "",
            "calculation": "",
            "accuracy": "0.0",
            "answer": "17.0%",
            "answer_supported": "False",
            "calculation_supported": "True",
            "operation_semantics_checked": "True",
            "row_operation_grounded": "True",
            "semantically_grounded": "True",
            "citation_correct": "True",
            "source_consistent": "True",
        }
        row.update(overrides)
        return row


if __name__ == "__main__":
    unittest.main()
