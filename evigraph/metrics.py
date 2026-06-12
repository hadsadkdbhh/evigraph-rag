from __future__ import annotations

import re
from typing import Any


def numeric_exact_match(prediction: str, gold: str | None) -> float:
    if not gold:
        return 0.0
    predicted_numbers = _numbers(prediction)
    gold_numbers = _numbers(gold)
    if not predicted_numbers or not gold_numbers:
        return float(prediction.strip().lower() == gold.strip().lower())
    return float(any(abs(pred - gold_value) < 1e-6 for pred in predicted_numbers for gold_value in gold_numbers))


def misleading_acceptance(selected_ids: list[str]) -> float:
    risky_markers = ("misleading", "conflicting", "forecast")
    return float(any(any(marker in node_id.lower() for marker in risky_markers) for node_id in selected_ids))


def summarize_result(result: dict[str, Any], gold: str | None = None) -> dict[str, Any]:
    selected_ids = list(result.get("selected_ids", []))
    cost = result.get("cost", {})
    prediction = result.get("answer", {}).get("text", "")
    return {
        "accuracy": numeric_exact_match(prediction, gold),
        "answer_supported": bool(result.get("verification", {}).get("answer_supported", False)),
        "citation_correct": bool(result.get("verification", {}).get("citation_correct", False)),
        "misleading_acceptance": misleading_acceptance(selected_ids),
        "input_tokens": cost.get("selected_tokens", 0.0),
        "tool_calls": cost.get("tool_calls", 0.0),
        "latency_ms": cost.get("latency_ms", 0.0),
    }


def _numbers(text: str) -> list[float]:
    return [float(match) for match in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]
