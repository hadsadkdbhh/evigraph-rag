from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol

from evigraph.clients import LLMClient, make_llm_client
from evigraph.table_executor import TableOperationExecutor


@dataclass
class PlannedNumericAnswer:
    text: str
    calculation: str


class NumericPlanClient(Protocol):
    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict[str, Any]:
        ...


class LLMNumericPlanClient:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict[str, Any]:
        return self.llm_client.chat_json(self._messages(query, contexts))

    def _messages(self, query: str, contexts: list[tuple[str, str]]) -> list[dict[str, str]]:
        compact_context = "\n\n".join(
            f"[{node_id}]\n{text[:2200]}" for node_id, text in contexts[:4]
        )
        return [
            {
                "role": "system",
                "content": (
                    "You are a numeric QA planner. Return JSON only. "
                    "Do not compute the final answer in prose. Produce a verifiable plan over cited context."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {query}\n\n"
                    f"Context:\n{compact_context}\n\n"
                    "Return a JSON object with this schema:\n"
                    "{"
                    "\"operation\": \"difference|ratio|percent_change|average|sum\", "
                    "\"node_id\": \"context id\", "
                    "\"target\": {\"label\": \"row or phrase\", \"year\": \"optional\", \"value\": number}, "
                    "\"base\": {\"label\": \"row or phrase\", \"year\": \"optional\", \"value\": number}, "
                    "\"values\": [{\"label\": \"row or phrase\", \"year\": \"optional\", \"value\": number}], "
                    "\"scale\": \"number|percent\", "
                    "\"rationale\": \"short\""
                    "}\n"
                    "Use target/base for difference, ratio, and percent_change. "
                    "Use values for sum and average. Values must appear in the context."
                ),
            },
        ]


class NumericPlanExecutor:
    def __init__(self) -> None:
        self.executor = TableOperationExecutor()

    def execute(self, query: str, contexts: list[tuple[str, str]], plan: dict[str, Any]) -> PlannedNumericAnswer | None:
        operation = str(plan.get("operation", "")).lower()
        node_id = str(plan.get("node_id") or "")
        context_text = self._context_text(node_id, contexts)
        if context_text is None:
            return None

        if operation in {"difference", "ratio", "percent_change"}:
            target = self._planned_value(plan.get("target"), context_text)
            base = self._planned_value(plan.get("base"), context_text)
            if target is None or base is None:
                return None
            if operation == "difference":
                result = self.executor.difference(target, base)
                return PlannedNumericAnswer(
                    text=f"{result.value:g}",
                    calculation=f"planned_difference: {result.expression}",
                )
            if operation == "ratio":
                result = self.executor.ratio(target, base)
                if result is None:
                    return None
                value = result.value * 100.0 if str(plan.get("scale")) == "percent" else result.value
                suffix = "%" if str(plan.get("scale")) == "percent" else ""
                return PlannedNumericAnswer(
                    text=self._format_number(value, suffix),
                    calculation=f"planned_ratio: {target:g} / {base:g}{' * 100' if suffix else ''} = {value:.1f}{suffix}",
                )
            result = self.executor.percent_change(target, base)
            if result is None:
                return None
            return PlannedNumericAnswer(
                text=f"{result.value:.1f}%",
                calculation=f"planned_percent_change: {result.expression}",
            )

        if operation in {"sum", "average"}:
            values = [
                value
                for item in plan.get("values", [])
                if (value := self._planned_value(item, context_text)) is not None
            ]
            if not values:
                return None
            result = self.executor.sum(values) if operation == "sum" else self.executor.average(values)
            if result is None:
                return None
            return PlannedNumericAnswer(
                text=f"{result.value:g}",
                calculation=f"planned_{operation}: {result.expression}",
            )
        return None

    def _context_text(self, node_id: str, contexts: list[tuple[str, str]]) -> str | None:
        if node_id:
            for candidate_id, text in contexts:
                if candidate_id == node_id:
                    return text
        if len(contexts) == 1:
            return contexts[0][1]
        return None

    def _planned_value(self, item: Any, context_text: str) -> float | None:
        if not isinstance(item, dict) or "value" not in item:
            return None
        try:
            value = float(item["value"])
        except (TypeError, ValueError):
            return None
        if self._value_supported(value, context_text):
            return value
        return None

    def _value_supported(self, value: float, context_text: str) -> bool:
        for number in re.findall(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?", context_text):
            try:
                if abs(float(number.replace(",", "")) - value) < 0.05:
                    return True
            except ValueError:
                continue
        return False

    def _format_number(self, value: float, suffix: str = "") -> str:
        if abs(value - round(value)) < 0.05:
            return f"{round(value):.0f}{suffix}"
        return f"{value:.1f}{suffix}"


class NumericPlannerFallback:
    def __init__(self, plan_client: NumericPlanClient) -> None:
        self.plan_client = plan_client
        self.executor = NumericPlanExecutor()

    @classmethod
    def from_config(cls, config: dict[str, Any] | None = None) -> NumericPlannerFallback | None:
        config = config or {}
        if not config.get("enabled", False):
            return None
        llm_config = dict(config.get("llm", {}))
        for source_key, target_key in [
            ("llm_provider", "provider"),
            ("llm_base_url", "base_url"),
            ("llm_api_key", "api_key"),
            ("llm_model", "model"),
            ("llm_timeout", "timeout"),
        ]:
            if source_key in config:
                llm_config[target_key] = config[source_key]
        return cls(LLMNumericPlanClient(make_llm_client(llm_config)))

    def answer(self, query: str, contexts: list[tuple[str, str]]) -> PlannedNumericAnswer | None:
        try:
            plan = self.plan_client.plan(query, contexts)
        except Exception:
            return None
        return self.executor.execute(query, contexts, plan)
