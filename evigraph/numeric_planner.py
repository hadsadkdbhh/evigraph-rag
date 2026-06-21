from __future__ import annotations

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
                    "\"operation\": \"difference|ratio|percent_change|percent_of_increase|average|sum|product\", "
                    "\"node_id\": \"context id\", "
                    "\"target\": {\"label\": \"row label or phrase\", \"year\": \"optional column/year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"base\": {\"label\": \"row label or phrase\", \"year\": \"optional column/year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"numerator_target\": {\"label\": \"row label\", \"year\": \"target year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"numerator_base\": {\"label\": \"row label\", \"year\": \"base year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"denominator_target\": {\"label\": \"row label\", \"year\": \"target year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"denominator_base\": {\"label\": \"row label\", \"year\": \"base year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"values\": [{\"label\": \"row label or phrase\", \"year\": \"optional column/year\", \"period\": \"optional duration\", \"value\": number}], "
                    "\"scale\": \"number|percent\", "
                    "\"rationale\": \"short\""
                    "}\n"
                    "Use target/base for difference, ratio, and percent_change. "
                    "Use numerator_target/base and denominator_target/base for percent_of_increase. "
                    "Use values for sum, average, and product. Values must appear in the context or question. "
                    "If the context is a table, you may omit value when label plus year/column identifies a cell; "
                    "the executor will read that cell locally. When multiple columns share a year, set period to "
                    "phrases such as three months ended, six months ended, nine months ended, or twelve months ended."
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

        if operation in {"multiply", "multiplication"}:
            operation = "product"

        if operation in {"difference", "ratio", "percent_change"}:
            target = self.executor.resolve_value(plan.get("target"), context_text, support_text=query)
            base = self.executor.resolve_value(plan.get("base"), context_text, support_text=query)
            if target is None or base is None:
                return None
            if operation == "difference":
                result = self.executor.difference(target.value, base.value)
                return PlannedNumericAnswer(
                    text=f"{result.value:g}",
                    calculation=self._calculation(
                        "planned_difference",
                        result.expression,
                        target,
                        base,
                    ),
                )
            if operation == "ratio":
                result = self.executor.ratio(target.value, base.value)
                if result is None:
                    return None
                value = result.value * 100.0 if str(plan.get("scale")) == "percent" else result.value
                suffix = "%" if str(plan.get("scale")) == "percent" else ""
                return PlannedNumericAnswer(
                    text=self._format_number(value, suffix),
                    calculation=self._calculation(
                        "planned_ratio",
                        f"{target.value:g} / {base.value:g}{' * 100' if suffix else ''} = {value:.1f}{suffix}",
                        target,
                        base,
                    ),
                )
            result = self.executor.percent_change(target.value, base.value)
            if result is None:
                return None
            return PlannedNumericAnswer(
                text=f"{result.value:.1f}%",
                calculation=self._calculation(
                    "planned_percent_change",
                    result.expression,
                    target,
                    base,
                ),
            )

        if operation == "percent_of_increase":
            numerator_target = self.executor.resolve_value(plan.get("numerator_target"), context_text, support_text=query)
            numerator_base = self.executor.resolve_value(plan.get("numerator_base"), context_text, support_text=query)
            denominator_target = self.executor.resolve_value(
                plan.get("denominator_target"),
                context_text,
                support_text=query,
            )
            denominator_base = self.executor.resolve_value(plan.get("denominator_base"), context_text, support_text=query)
            operands = [numerator_target, numerator_base, denominator_target, denominator_base]
            if any(value is None for value in operands):
                return None
            numerator_delta = self.executor.difference(numerator_target.value, numerator_base.value)
            denominator_delta = self.executor.difference(denominator_target.value, denominator_base.value)
            ratio = self.executor.ratio(numerator_delta.value, denominator_delta.value)
            if ratio is None:
                return None
            percent = ratio.value * 100.0
            calculation = (
                "planned_percent_of_increase "
                f"numerator={self._value_ref(numerator_target)}-{self._value_ref(numerator_base)} "
                f"denominator={self._value_ref(denominator_target)}-{self._value_ref(denominator_base)}: "
                f"({numerator_target.value:g} - {numerator_base.value:g}) / "
                f"({denominator_target.value:g} - {denominator_base.value:g}) * 100 = {percent:.1f}%"
            )
            return PlannedNumericAnswer(text=self._format_number(percent, "%"), calculation=calculation)

        if operation in {"sum", "average", "product"}:
            resolved_values = [
                value
                for item in plan.get("values", [])
                if (value := self.executor.resolve_value(item, context_text, support_text=query)) is not None
            ]
            values = [
                value.value
                for value in resolved_values
            ]
            if not values:
                return None
            if operation == "sum":
                result = self.executor.sum(values)
            elif operation == "average":
                result = self.executor.average(values)
            else:
                result = self.executor.product(values)
            if result is None:
                return None
            return PlannedNumericAnswer(
                text=f"{result.value:g}",
                calculation=f"planned_{operation} values={self._value_refs(resolved_values)}: {result.expression}",
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

    def _format_number(self, value: float, suffix: str = "") -> str:
        if abs(value - round(value)) < 0.05:
            return f"{round(value):.0f}{suffix}"
        return f"{value:.1f}{suffix}"

    def _calculation(self, operation: str, expression: str, target: Any, base: Any) -> str:
        target_ref = self._value_ref(target)
        base_ref = self._value_ref(base)
        return f"{operation} target={target_ref} base={base_ref}: {expression}"

    def _value_ref(self, value: Any) -> str:
        row = getattr(value, "row_label", "") or "value"
        column = getattr(value, "column_label", "")
        period = getattr(value, "period_label", "")
        if column and period:
            return f"{row}/{period}/{column}"
        if column:
            return f"{row}/{column}"
        return str(row)

    def _value_refs(self, values: list[Any]) -> str:
        return ", ".join(self._value_ref(value) for value in values)


class NumericPlannerFallback:
    def __init__(self, plan_client: NumericPlanClient, strict: bool = False, log_errors: bool = False) -> None:
        self.plan_client = plan_client
        self.executor = NumericPlanExecutor()
        self.strict = strict
        self.log_errors = log_errors

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
        return cls(
            LLMNumericPlanClient(make_llm_client(llm_config)),
            strict=bool(config.get("strict", False)),
            log_errors=bool(config.get("log_errors", False)),
        )

    def answer(self, query: str, contexts: list[tuple[str, str]]) -> PlannedNumericAnswer | None:
        try:
            plan = self.plan_client.plan(query, contexts)
        except Exception as exc:
            if self.log_errors:
                print(f"[numeric_planner] planner request failed: {exc}", flush=True)
            if self.strict:
                raise
            return None
        answer = self.executor.execute(query, contexts, plan)
        if answer is None and self.log_errors:
            print(f"[numeric_planner] planner returned unverifiable plan: {plan}", flush=True)
        if answer is None and self.strict:
            raise RuntimeError(f"Numeric planner returned unverifiable plan: {plan}")
        return answer
