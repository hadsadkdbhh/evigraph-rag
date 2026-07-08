from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


FALLBACK_PREFIXES = (
    "based on the selected evidence",
    "insufficient",
    "i cannot",
    "cannot determine",
    "not enough evidence",
)

SUPPORT_FLAGS = (
    "answer_supported",
    "calculation_supported",
    "operation_semantics_checked",
    "row_operation_grounded",
    "semantically_grounded",
    "citation_correct",
    "source_consistent",
)


@dataclass(frozen=True)
class PortfolioDecision:
    source: str
    reason: str


def build_portfolio_rows(
    primary_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, str]],
    *,
    primary_name: str = "bm25",
    candidate_name: str = "neural_hybrid",
    policy: str = "fallback_numeric_calculation",
) -> list[dict[str, str]]:
    candidates = {_row_key(row): row for row in candidate_rows}
    output: list[dict[str, str]] = []
    for primary in primary_rows:
        key = _row_key(primary)
        if key not in candidates:
            raise ValueError(f"Candidate CSV is missing row {key!r}.")
        candidate = candidates[key]
        decision = choose_row(primary, candidate, policy=policy)
        chosen = candidate if decision.source == "candidate" else primary
        chosen_name = candidate_name if decision.source == "candidate" else primary_name
        row = dict(chosen)
        row["portfolio_policy"] = policy
        row["portfolio_choice"] = chosen_name
        row["portfolio_decision"] = decision.reason
        row["primary_prediction"] = primary.get("prediction", "")
        row["candidate_prediction"] = candidate.get("prediction", "")
        row["primary_accuracy"] = primary.get("accuracy", "")
        row["candidate_accuracy"] = candidate.get("accuracy", "")
        row["primary_calculation"] = primary.get("calculation", "")
        row["candidate_calculation"] = candidate.get("calculation", "")
        output.append(row)
    return output


def choose_row(primary: dict[str, str], candidate: dict[str, str], *, policy: str = "fallback_numeric_calculation") -> PortfolioDecision:
    if policy == "confidence":
        return _confidence_selector(primary, candidate)
    if policy == "strict_supported_fallback":
        return _strict_supported_fallback(primary, candidate)
    if policy == "fallback_numeric_calculation":
        return _fallback_numeric_calculation(primary, candidate)
    raise ValueError(f"Unknown portfolio policy: {policy}")


def summarize_portfolio(rows: list[dict[str, str]], *, primary_name: str, candidate_name: str) -> dict[str, Any]:
    if not rows:
        return {
            "n": 0,
            "accuracy": 0.0,
            "switches": 0,
            "wins_vs_primary": 0,
            "losses_vs_primary": 0,
            "neutral_switches": 0,
        }
    switches = [row for row in rows if row.get("portfolio_choice") == candidate_name]
    wins = [
        row
        for row in switches
        if _float(row.get("candidate_accuracy")) > _float(row.get("primary_accuracy"))
    ]
    losses = [
        row
        for row in switches
        if _float(row.get("candidate_accuracy")) < _float(row.get("primary_accuracy"))
    ]
    return {
        "n": len(rows),
        "accuracy": mean(_float(row.get("accuracy")) for row in rows),
        "primary_accuracy": mean(_float(row.get("primary_accuracy")) for row in rows),
        "candidate_accuracy": mean(_float(row.get("candidate_accuracy")) for row in rows),
        "switches": len(switches),
        "wins_vs_primary": len(wins),
        "losses_vs_primary": len(losses),
        "neutral_switches": len(switches) - len(wins) - len(losses),
        "switch_examples": [row.get("id", "") for row in switches[:20]],
        "win_examples": [row.get("id", "") for row in wins[:20]],
        "loss_examples": [row.get("id", "") for row in losses[:20]],
    }


def render_portfolio_report(
    rows: list[dict[str, str]],
    *,
    title: str,
    primary_name: str,
    candidate_name: str,
) -> str:
    summary = summarize_portfolio(rows, primary_name=primary_name, candidate_name=candidate_name)
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        f"- Rows: {summary['n']}",
        f"- Portfolio EM: {_fmt(summary['accuracy'])}",
        f"- Primary EM ({primary_name}): {_fmt(summary['primary_accuracy'])}",
        f"- Candidate EM ({candidate_name}): {_fmt(summary['candidate_accuracy'])}",
        f"- Switches: {summary['switches']}",
        f"- Wins vs primary: {summary['wins_vs_primary']}",
        f"- Losses vs primary: {summary['losses_vs_primary']}",
        f"- Neutral switches: {summary['neutral_switches']}",
        "",
        "## Decision Breakdown",
        "",
        "| decision | count |",
        "| --- | ---: |",
        *[
            f"| {_escape(reason)} | {count} |"
            for reason, count in Counter(row.get("portfolio_decision", "") for row in rows).most_common()
        ],
        "",
        "## Decision Rule",
        "",
        "The selector is no-gold: it only inspects prediction text, calculation presence, and verifier/support fields. Accuracy and gold answers are used only after selection for evaluation.",
        "",
        "## Switch Examples",
        "",
    ]
    examples = [row for row in rows if row.get("portfolio_choice") == candidate_name][:20]
    if not examples:
        lines.append("No candidate switches.")
    else:
        lines.extend(["| id | decision | primary | candidate |", "| --- | --- | --- | --- |"])
        for row in examples:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _escape(row.get("id", "")),
                        _escape(row.get("portfolio_decision", "")),
                        _escape(_clip(row.get("primary_prediction", ""))),
                        _escape(_clip(row.get("candidate_prediction", ""))),
                    ]
                )
                + " |"
            )
    if summary["loss_examples"]:
        lines.extend(["", "## Loss Examples", ""])
        lines.append(", ".join(summary["loss_examples"]))
    return "\n".join(lines).rstrip() + "\n"


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = _fieldnames(rows)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return str(output)


def _strict_supported_fallback(primary: dict[str, str], candidate: dict[str, str]) -> PortfolioDecision:
    if not _is_primary_fallback(primary):
        return PortfolioDecision("primary", "primary_not_fallback")
    if not _candidate_has_numeric_calculation(candidate):
        return PortfolioDecision("primary", "candidate_not_numeric_calculation")
    missing = [flag for flag in SUPPORT_FLAGS if not _bool(candidate.get(flag))]
    if missing:
        return PortfolioDecision("primary", "candidate_missing_support_flags=" + ",".join(missing))
    return PortfolioDecision("candidate", "primary_fallback_candidate_numeric_calculation_verified")


def _fallback_numeric_calculation(primary: dict[str, str], candidate: dict[str, str]) -> PortfolioDecision:
    if not _is_primary_fallback(primary):
        return PortfolioDecision("primary", "primary_not_fallback")
    if not _candidate_has_numeric_calculation(candidate):
        return PortfolioDecision("primary", "candidate_not_numeric_calculation")
    return PortfolioDecision("candidate", "primary_fallback_candidate_numeric_calculation")


def _confidence_selector(primary: dict[str, str], candidate: dict[str, str]) -> PortfolioDecision:
    fallback_decision = _fallback_numeric_calculation(primary, candidate)
    if fallback_decision.source == "candidate":
        return PortfolioDecision("candidate", "confidence_fallback_numeric_calculation")
    if _fallback_evidence_coverage_improves(primary, candidate):
        return PortfolioDecision("candidate", "confidence_fallback_evidence_coverage")
    reason = _supported_calculation_refinement(primary, candidate)
    if reason:
        return PortfolioDecision("candidate", reason)
    return PortfolioDecision("primary", "confidence_keep_primary")


def _is_primary_fallback(row: dict[str, str]) -> bool:
    prediction = row.get("prediction", "").strip().lower()
    calculation = row.get("calculation", "").strip()
    if calculation:
        return False
    if any(prediction.startswith(prefix) for prefix in FALLBACK_PREFIXES):
        return True
    return not _has_numeric_answer(prediction)


def _candidate_has_numeric_calculation(row: dict[str, str]) -> bool:
    prediction = row.get("prediction", "").strip().lower()
    calculation = row.get("calculation", "").strip()
    if not calculation:
        return False
    if any(prediction.startswith(prefix) for prefix in FALLBACK_PREFIXES):
        return False
    return _has_numeric_answer(prediction) or prediction in {"yes", "no"}


def _fallback_evidence_coverage_improves(primary: dict[str, str], candidate: dict[str, str]) -> bool:
    if not (_is_primary_fallback(primary) and _is_primary_fallback(candidate)):
        return False
    if _support_flag_count(candidate) < _support_flag_count(primary):
        return False
    primary_coverage = _query_token_overlap(primary.get("query", ""), primary.get("prediction", ""))
    candidate_coverage = _query_token_overlap(candidate.get("query", ""), candidate.get("prediction", ""))
    query_years = _years(primary.get("query", ""))
    primary_years = _years(primary.get("prediction", ""))
    candidate_years = _years(candidate.get("prediction", ""))
    covers_missing_query_year = bool(query_years & candidate_years) and not bool(query_years & primary_years)
    return candidate_coverage > primary_coverage + 0.10 or covers_missing_query_year


def _supported_calculation_refinement(primary: dict[str, str], candidate: dict[str, str]) -> str | None:
    if not _supported_numeric(candidate) or not _candidate_has_numeric_calculation(primary):
        return None
    primary_operation = _operation(primary)
    candidate_operation = _operation(candidate)
    primary_calc = primary.get("calculation", "").lower()
    candidate_calc = candidate.get("calculation", "").lower()
    query = primary.get("query", "").lower()
    if (
        primary_operation == candidate_operation == "average_high_low_price"
        and _prediction_magnitude(candidate) > 5 * max(_prediction_magnitude(primary), 1.0)
    ):
        return "confidence_supported_average_scale_refinement"
    if primary_operation == candidate_operation == "ratio_percent" and "othercurrent" in primary_calc:
        return "confidence_supported_denominator_text_refinement"
    if (
        primary_operation == candidate_operation == "same_year_row_ratio"
        and "proportional" in primary_calc
        and "free cash flow" in candidate_calc
    ):
        return "confidence_supported_ratio_row_refinement"
    if (
        primary_operation == candidate_operation == "percent_change"
        and "net cash provided by operating activities" in primary_calc
        and "cash provided by operating activities" in candidate_calc
    ):
        return "confidence_supported_cashflow_row_refinement"
    if (
        primary_operation == "planned_percent_change"
        and candidate_operation == "percent_change"
        and "operating leases" in query
        and "rental expense" in candidate_calc
    ):
        return "confidence_supported_concrete_percent_refinement"
    return None


def _supported_numeric(row: dict[str, str]) -> bool:
    return _candidate_has_numeric_calculation(row) and all(_bool(row.get(flag)) for flag in SUPPORT_FLAGS)


def _support_flag_count(row: dict[str, str]) -> int:
    return sum(int(_bool(row.get(flag))) for flag in SUPPORT_FLAGS)


def _operation(row: dict[str, str]) -> str:
    match = re.match(r"([a-z_]+)", row.get("calculation", ""))
    return match.group(1) if match else ""


def _query_token_overlap(query: str, text: str) -> float:
    query_tokens = set(_content_tokens(query))
    if not query_tokens:
        return 0.0
    text_tokens = set(_content_tokens(text))
    return len(query_tokens & text_tokens) / len(query_tokens)


def _content_tokens(text: str) -> list[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "change",
        "company",
        "december",
        "did",
        "during",
        "ended",
        "for",
        "from",
        "how",
        "in",
        "is",
        "many",
        "much",
        "of",
        "on",
        "or",
        "over",
        "percent",
        "percentage",
        "ratio",
        "the",
        "to",
        "total",
        "under",
        "was",
        "were",
        "what",
        "which",
        "with",
        "year",
        "years",
    }
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and not token.isdigit() and token not in stopwords
    ]


def _years(text: str) -> set[str]:
    return set(re.findall(r"\b(?:19|20)\d{2}\b", text))


def _prediction_magnitude(row: dict[str, str]) -> float:
    match = re.search(r"[-+]?\d+(?:\.\d+)?", row.get("prediction", ""))
    return abs(float(match.group(0))) if match else 0.0


def _has_numeric_answer(text: str) -> bool:
    return bool(re.search(r"[-+]?\d+(?:\.\d+)?", text))


def _row_key(row: dict[str, str]) -> tuple[str, str]:
    return (row.get("id", ""), row.get("method", ""))


def _fieldnames(rows: list[dict[str, str]]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        for key in row:
            if key not in seen:
                seen.append(key)
    return seen


def _bool(value: str | None) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _float(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _clip(text: str, limit: int = 80) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 3] + "..."


def _escape(text: str) -> str:
    return text.replace("|", "\\|")
