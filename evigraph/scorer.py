from __future__ import annotations

import math
import re
from typing import Any

from evigraph.clients import LLMClient, make_llm_client
from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import EvidenceNode, EvidenceScore


def _clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[A-Za-z0-9.]+", text.lower()) if len(token) > 1}


class RuleBasedUtilityRiskScorer:
    def score_all(self, query: str, graph: EvidenceGraph) -> dict[str, EvidenceScore]:
        scores = {}
        for node in graph.nodes.values():
            score = self.score_node(query, node, graph)
            node.scores = score.to_dict()
            scores[node.node_id] = score
        return scores

    def score_node(self, query: str, node: EvidenceNode, graph: EvidenceGraph) -> EvidenceScore:
        query_tokens = _tokens(query)
        node_tokens = _tokens(node.text())
        overlap = len(query_tokens & node_tokens) / max(1, len(query_tokens))
        entity_alignment = self._entity_alignment(query, node)
        modality_bonus = 0.25 if self._modality_matches(query, node) else 0.0
        relevance = _clip(0.35 + overlap + modality_bonus + entity_alignment)

        has_numbers = bool(re.search(r"\d", node.text()))
        text_lower = node.text().lower()
        source_lower = str(node.source_doc or "").lower()
        reliable_content = any(marker in text_lower for marker in ["official", "audited", "final", "supersedes"])
        unreliable_source = any(marker in source_lower for marker in ["draft", "forecast", "press", "excerpt"])
        is_oracle_source = node.metadata.get("loader") == "source_doc_oracle"
        unreliable_content = (
            any(
                marker in text_lower
                for marker in ["preliminary forecast", "draft forecast", "press excerpt", "early draft", "expected"]
            )
            and not reliable_content
            and not is_oracle_source
        )
        utility = _clip(0.25 + 0.45 * relevance + (0.25 if has_numbers else 0.0) + modality_bonus)
        grounding = _clip(0.2 + (0.35 if has_numbers else 0.0) + (0.25 if node.source_doc else 0.0) + modality_bonus)
        uncertainty = _clip(1.0 - node.confidence + (0.2 if unreliable_source or unreliable_content else 0.0))
        misleading_risk = _clip(
            (0.75 if node.metadata.get("is_misleading") else 0.0)
            + (0.25 if node.metadata.get("source_quality") in {"draft", "third_party"} else 0.0)
            + (0.65 if unreliable_source or unreliable_content else 0.0)
        )
        contradiction_risk = _clip(
            (0.8 if node.metadata.get("is_conflicting") else 0.0)
            + (0.65 if ("press" in source_lower or "press excerpt" in text_lower) and not reliable_content else 0.0)
        )
        source_reliability = self._source_reliability(node)
        cost = self._normalized_cost(node)
        retrieval_prior = self._retrieval_prior(node)
        final_score = (
            1.0 * relevance
            + 1.5 * utility
            + 1.2 * grounding
            + 0.6 * source_reliability
            + 0.8 * retrieval_prior
            - 1.0 * misleading_risk
            - 1.0 * contradiction_risk
            - 0.7 * uncertainty
            - 0.4 * cost
        )
        return EvidenceScore(
            relevance=relevance,
            utility=utility,
            grounding=grounding,
            uncertainty=uncertainty,
            misleading_risk=misleading_risk,
            contradiction_risk=contradiction_risk,
            source_reliability=source_reliability,
            cost=cost,
            final_score=round(final_score, 4),
            reason=self._reason(node, misleading_risk, contradiction_risk, utility),
        )

    def _modality_matches(self, query: str, node: EvidenceNode) -> bool:
        query_lower = query.lower()
        if any(word in query_lower for word in ["chart", "plot", "trend"]):
            return node.modality == "chart"
        if any(word in query_lower for word in ["table", "cell", "row"]):
            return node.modality == "table"
        return node.modality == "text"

    def _entity_alignment(self, query: str, node: EvidenceNode) -> float:
        query_label = self._case_label(query)
        if not query_label:
            return 0.0
        node_label = self._case_label(f"{node.source_doc} {node.text()}")
        if not node_label:
            return -0.15
        return 0.35 if node_label == query_label else -0.45

    def _case_label(self, text: str) -> str | None:
        match = re.search(r"\bcase\s+([a-z]+)\b", text.lower())
        return match.group(1) if match else None

    def _source_reliability(self, node: EvidenceNode) -> float:
        quality = node.metadata.get("source_quality")
        if quality == "draft":
            return 0.35
        if quality == "third_party":
            return 0.45
        if node.source_doc and node.source_doc.endswith(".pdf"):
            return 0.85
        return 0.65

    def _normalized_cost(self, node: EvidenceNode) -> float:
        tokens = float(node.cost.get("tokens", len(node.text().split())))
        tool_calls = float(node.cost.get("tool_calls", 0))
        latency_ms = float(node.cost.get("latency_ms", 0))
        return _clip(math.log1p(tokens) / 6.0 + 0.12 * tool_calls + latency_ms / 3000.0)

    def _retrieval_prior(self, node: EvidenceNode) -> float:
        try:
            rank = int(node.metadata.get("retrieval_rank", 0))
        except (TypeError, ValueError):
            return 0.0
        if rank <= 0:
            return 0.0
        return _clip((9 - min(rank, 9)) / 8)

    def _reason(self, node: EvidenceNode, misleading: float, contradiction: float, utility: float) -> str:
        if misleading > 0.6:
            return "High misleading risk; likely not reliable evidence."
        if contradiction > 0.6:
            return "Conflicts with higher-grounding structured evidence."
        if utility > 0.7:
            return "Useful candidate with answer-bearing content."
        return "Low-to-medium utility candidate."


class LLMJudgeUtilityRiskScorer(RuleBasedUtilityRiskScorer):
    def __init__(self, llm_client: LLMClient | None = None, config: dict[str, Any] | None = None) -> None:
        self.llm_client = llm_client or make_llm_client(_llm_config(config or {}))

    def score_node(self, query: str, node: EvidenceNode, graph: EvidenceGraph) -> EvidenceScore:
        rule_score = super().score_node(query, node, graph)
        try:
            payload = self.llm_client.chat_json(self._messages(query, node))
            return self._score_from_payload(payload, rule_score)
        except Exception as exc:
            fallback = rule_score
            fallback.reason = f"LLM judge unavailable; rule fallback used. {exc}"
            return fallback

    def _messages(self, query: str, node: EvidenceNode) -> list[dict[str, str]]:
        content_summary = node.text()
        if len(content_summary) > 1800:
            content_summary = content_summary[:1800] + "..."
        return [
            {
                "role": "system",
                "content": (
                    "You are an evidence judge for a multimodal RAG system. "
                    "Score candidate evidence for utility-risk selection. Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Query: {query}\n"
                    f"Evidence id: {node.node_id}\n"
                    f"Evidence type: {node.node_type}\n"
                    f"Modality: {node.modality}\n"
                    f"Source: {node.source_doc}\n"
                    f"Evidence content: {content_summary}\n\n"
                    "Return JSON with numbers from 0 to 1:\n"
                    "{"
                    '"relevance": ..., "utility": ..., "grounding": ..., '
                    '"uncertainty": ..., "misleading_risk": ..., '
                    '"contradiction_risk": ..., "source_reliability": ..., '
                    '"reason": "..."'
                    "}"
                ),
            },
        ]

    def _score_from_payload(self, payload: dict[str, Any], fallback: EvidenceScore) -> EvidenceScore:
        relevance = _payload_float(payload, "relevance", fallback.relevance)
        utility = _payload_float(payload, "utility", fallback.utility)
        grounding = _payload_float(payload, "grounding", fallback.grounding)
        uncertainty = _payload_float(payload, "uncertainty", fallback.uncertainty)
        misleading_risk = _payload_float(payload, "misleading_risk", fallback.misleading_risk)
        contradiction_risk = _payload_float(payload, "contradiction_risk", fallback.contradiction_risk)
        source_reliability = _payload_float(payload, "source_reliability", fallback.source_reliability)
        cost = fallback.cost
        final_score = (
            1.0 * relevance
            + 1.5 * utility
            + 1.2 * grounding
            + 0.6 * source_reliability
            - 1.0 * misleading_risk
            - 1.0 * contradiction_risk
            - 0.7 * uncertainty
            - 0.4 * cost
        )
        return EvidenceScore(
            relevance=relevance,
            utility=utility,
            grounding=grounding,
            uncertainty=uncertainty,
            misleading_risk=misleading_risk,
            contradiction_risk=contradiction_risk,
            source_reliability=source_reliability,
            cost=cost,
            final_score=round(final_score, 4),
            reason=str(payload.get("reason") or "LLM judge score."),
        )


class HybridUtilityRiskScorer(RuleBasedUtilityRiskScorer):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.rule_scorer = RuleBasedUtilityRiskScorer()
        self.llm_scorer = LLMJudgeUtilityRiskScorer(config=config)
        self.llm_weight = float((config or {}).get("llm_weight", 0.5))

    def score_node(self, query: str, node: EvidenceNode, graph: EvidenceGraph) -> EvidenceScore:
        rule = self.rule_scorer.score_node(query, node, graph)
        llm = self.llm_scorer.score_node(query, node, graph)
        if llm.reason.startswith("LLM judge unavailable"):
            return llm
        weight = max(0.0, min(1.0, self.llm_weight))
        blended = {
            field: (1 - weight) * getattr(rule, field) + weight * getattr(llm, field)
            for field in [
                "relevance",
                "utility",
                "grounding",
                "uncertainty",
                "misleading_risk",
                "contradiction_risk",
                "source_reliability",
            ]
        }
        cost = rule.cost
        final_score = (
            1.0 * blended["relevance"]
            + 1.5 * blended["utility"]
            + 1.2 * blended["grounding"]
            + 0.6 * blended["source_reliability"]
            - 1.0 * blended["misleading_risk"]
            - 1.0 * blended["contradiction_risk"]
            - 0.7 * blended["uncertainty"]
            - 0.4 * cost
        )
        return EvidenceScore(
            **blended,
            cost=cost,
            final_score=round(final_score, 4),
            reason=f"Hybrid score. Rule: {rule.reason} LLM: {llm.reason}",
        )


def make_scorer(config: dict[str, Any] | None = None) -> RuleBasedUtilityRiskScorer:
    config = config or {}
    provider = str(config.get("provider", "rule")).lower()
    if provider in {"rule", "none", "null"}:
        return RuleBasedUtilityRiskScorer()
    if provider == "llm":
        return LLMJudgeUtilityRiskScorer(config=config)
    if provider == "hybrid":
        return HybridUtilityRiskScorer(config=config)
    raise ValueError(f"Unknown scoring provider: {provider}")


def _payload_float(payload: dict[str, Any], key: str, default: float) -> float:
    try:
        return _clip(float(payload.get(key, default)))
    except (TypeError, ValueError):
        return default


def _llm_config(config: dict[str, Any]) -> dict[str, Any]:
    nested = dict(config.get("llm", {}))
    if "llm_provider" in config:
        nested["provider"] = config["llm_provider"]
    if "llm_base_url" in config:
        nested["base_url"] = config["llm_base_url"]
    if "llm_api_key" in config:
        nested["api_key"] = config["llm_api_key"]
    if "llm_model" in config:
        nested["model"] = config["llm_model"]
    return nested
