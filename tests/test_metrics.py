from __future__ import annotations

import unittest

from evigraph.metrics import summarize_result


class MetricsTest(unittest.TestCase):
    def test_supported_accuracy_requires_exact_match_and_verifier_support(self) -> None:
        result = {
            "answer": {"text": "42"},
            "selected_ids": [],
            "verification": {
                "answer_supported": True,
                "arithmetically_supported": True,
                "calculation_supported": True,
                "operation_semantics_checked": True,
                "row_operation_grounded": True,
                "semantically_grounded": True,
                "citation_correct": True,
            },
            "cost": {},
        }

        metrics = summarize_result(result, "42")

        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertTrue(metrics["supported_accuracy"])
        self.assertFalse(metrics["unsupported_correct"])
        self.assertFalse(metrics["supported_wrong"])
        self.assertEqual(metrics["answer_support_gap"], 0.0)

    def test_supported_wrong_flags_grounded_but_wrong_predictions(self) -> None:
        result = {
            "answer": {"text": "12"},
            "selected_ids": [],
            "verification": {
                "answer_supported": True,
                "arithmetically_supported": True,
                "calculation_supported": True,
                "operation_semantics_checked": True,
                "row_operation_grounded": True,
                "semantically_grounded": True,
                "citation_correct": True,
            },
            "cost": {},
        }

        metrics = summarize_result(result, "42")

        self.assertEqual(metrics["accuracy"], 0.0)
        self.assertFalse(metrics["supported_accuracy"])
        self.assertFalse(metrics["unsupported_correct"])
        self.assertTrue(metrics["supported_wrong"])
        self.assertEqual(metrics["answer_support_gap"], -1.0)


if __name__ == "__main__":
    unittest.main()
