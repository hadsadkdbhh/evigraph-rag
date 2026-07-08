from __future__ import annotations

import re
from typing import Protocol

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Action, Answer, EvidenceNode


class AnswerGenerator(Protocol):
    def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
        ...


class AnswerVerifier(Protocol):
    def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
        ...


class VerifierGuidedRepairer:
    """Search source-local candidate repairs and accept only verifier-supported answers."""

    def __init__(self, max_source_clusters: int = 8, max_nodes_per_source: int = 6, max_repair_rank: int = 2) -> None:
        self.max_source_clusters = max_source_clusters
        self.max_nodes_per_source = max_nodes_per_source
        self.max_repair_rank = max_repair_rank

    def repair(
        self,
        query: str,
        answer: Answer,
        verification: dict,
        graph: EvidenceGraph,
        generator: AnswerGenerator,
        verifier: AnswerVerifier,
    ) -> tuple[Answer, dict, Action | None]:
        if not self._should_repair(query, verification, answer):
            return answer, verification, None

        issues = self._repair_issues(verification)
        attempted = 0
        for support_graph in self._source_cluster_graphs(graph, query, answer):
            attempted += 1
            planner_first = getattr(generator, "generate_planner_first", None)
            candidate = (
                planner_first(query, support_graph)
                if callable(planner_first)
                else generator.generate(query, support_graph)
            )
            if self._same_answer(candidate, answer):
                continue
            candidate_verification = verifier.verify(query, candidate, support_graph)
            if candidate_verification.get("answer_supported") and self._candidate_improves(
                query,
                candidate,
                candidate_verification,
                answer,
                verification,
            ):
                candidate_verification["repair_applied"] = True
                candidate_verification["repair_attempts"] = attempted
                return (
                    candidate,
                    candidate_verification,
                    Action(
                        "REPAIR_NUMERIC_ANSWER",
                        target_node_ids=list(candidate.citations),
                        params={"attempts": attempted, "issues": issues},
                        estimated_cost={"tool_calls": 0, "latency_ms": 10 * attempted},
                        reason="Verifier-guided operand repair accepted a better source-local numeric answer.",
                    ),
                )

        if verification.get("answer_supported"):
            return answer, verification, None
        repaired_verification = dict(verification)
        repaired_verification["repair_applied"] = False
        repaired_verification["repair_attempts"] = attempted
        return answer, repaired_verification, None

    def _should_repair(self, query: str, verification: dict, answer: Answer) -> bool:
        if not answer.calculations:
            return False
        issues = self._repair_issues(verification)
        if issues == ["source_consistency"]:
            return bool(verification.get("answer_supported") and self._answer_reasonableness_score(query, answer) < 0)
        if issues:
            return True
        return bool(verification.get("answer_supported"))

    def _repair_issues(self, verification: dict) -> list[str]:
        issues = []
        if verification.get("row_grounded") is False:
            issues.append("row_grounding")
        if verification.get("period_grounded") is False:
            issues.append("period_grounding")
        if verification.get("operation_semantics_checked") is False:
            issues.append("operation_type")
        if verification.get("source_consistent") is False:
            issues.append("source_consistency")
        if verification.get("arithmetically_supported") is False or verification.get("calculation_supported") is False:
            issues.append("operand_support")
        if not issues and verification.get("answer_supported") is False:
            issues.append("answer_support")
        if not issues and verification.get("answer_supported"):
            issues.append("supported_operand_rescore")
        return issues

    def _candidate_improves(
        self,
        query: str,
        candidate: Answer,
        candidate_verification: dict,
        current: Answer,
        current_verification: dict,
    ) -> bool:
        if not current_verification.get("answer_supported"):
            return True
        return self._answer_score(query, candidate, candidate_verification) > self._answer_score(
            query,
            current,
            current_verification,
        )

    def _answer_score(self, query: str, answer: Answer, verification: dict) -> float:
        score = 0.0
        score += 50.0 if verification.get("answer_supported") else 0.0
        score += 8.0 if verification.get("calculation_supported") else 0.0
        score += 8.0 if verification.get("arithmetically_supported") else 0.0
        score += 8.0 if verification.get("row_grounded") else 0.0
        score += 6.0 if verification.get("period_grounded", True) else 0.0
        score += 6.0 if verification.get("operation_semantics_checked") else 0.0
        score += 4.0 if verification.get("semantically_grounded") else 0.0
        score += float(verification.get("confidence", 0.0))
        score += self._answer_reasonableness_score(query, answer)
        return score

    def _answer_reasonableness_score(self, query: str, answer: Answer) -> float:
        query_lower = query.lower()
        numbers = self._numbers(answer.text)
        if not numbers:
            return 0.0
        if any(term in query_lower for term in ["percent", "percentage", "portion", "share", "ratio"]):
            score = 0.0
            for value in numbers:
                magnitude = abs(value)
                if magnitude <= 200:
                    score += 3.0
                elif magnitude >= 1000:
                    score -= 20.0
                elif magnitude >= 500:
                    score -= 10.0
                elif magnitude >= 300:
                    score -= 5.0
            return score
        return 0.0

    def _source_cluster_graphs(self, graph: EvidenceGraph, query: str = "", answer: Answer | None = None) -> list[EvidenceGraph]:
        by_source: dict[str, list[EvidenceNode]] = {}
        for node in graph.nodes.values():
            if not node.source_doc:
                continue
            if self._is_risky(node):
                continue
            by_source.setdefault(str(node.source_doc), []).append(node)

        ranked_sources = sorted(
            by_source.items(),
            key=lambda item: self._source_rank_key(item[1], query, answer),
        )
        return [
            self._source_graph(graph, nodes, query, answer)
            for _, nodes in ranked_sources[: self.max_source_clusters]
            if nodes and min(self._retrieval_rank(node) for node in nodes) <= self.max_repair_rank
        ]

    def _source_graph(
        self,
        graph: EvidenceGraph,
        nodes: list[EvidenceNode],
        query: str = "",
        answer: Answer | None = None,
    ) -> EvidenceGraph:
        support = EvidenceGraph()
        ordered_nodes = sorted(nodes, key=lambda node: self._node_rank_key(node, query, answer))[: self.max_nodes_per_source]
        ordered_ids = {node.node_id for node in ordered_nodes}
        for node in ordered_nodes:
            support.add_node(node)
        for edge in graph.edges:
            if edge.source in ordered_ids and edge.target in ordered_ids:
                support.edges.append(edge)
        return support

    def _source_rank_key(self, nodes: list[EvidenceNode], query: str = "", answer: Answer | None = None) -> tuple[int, int, int, int, float, str]:
        best_rank = min(self._retrieval_rank(node) for node in nodes)
        best_score = max(float(node.scores.get("final_score", 0.0)) for node in nodes)
        source = str(nodes[0].source_doc or "")
        query_terms = self._query_terms(query)
        query_years = self._query_years(query)
        operands = self._calculation_operands(answer)
        text = "\n".join(node.text().lower() for node in nodes)
        return (
            best_rank,
            -self._term_overlap(query_terms, text),
            -self._year_overlap(query_years, text),
            -self._operand_overlap(operands, text),
            -best_score,
            source,
        )

    def _node_rank_key(self, node: EvidenceNode, query: str = "", answer: Answer | None = None) -> tuple[int, int, int, int, int, float, str]:
        text = node.text().lower()
        query_terms = self._query_terms(query)
        query_years = self._query_years(query)
        operands = self._calculation_operands(answer)
        return (
            -self._term_overlap(query_terms, text),
            -self._year_overlap(query_years, text),
            -self._operand_overlap(operands, text),
            0 if node.metadata.get("neighbor_context") else 1,
            self._retrieval_rank(node),
            -float(node.scores.get("final_score", 0.0)),
            node.node_id,
        )

    def _retrieval_rank(self, node: EvidenceNode) -> int:
        try:
            return int(node.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            return 999

    def _is_risky(self, node: EvidenceNode) -> bool:
        return node.scores.get("misleading_risk", 0.0) >= 0.65 or node.scores.get("contradiction_risk", 0.0) >= 0.65

    def _same_answer(self, candidate: Answer, answer: Answer) -> bool:
        return candidate.text == answer.text and candidate.calculations == answer.calculations

    def _query_terms(self, query: str) -> set[str]:
        stop = {
            "what",
            "was",
            "were",
            "the",
            "and",
            "for",
            "from",
            "with",
            "that",
            "this",
            "how",
            "much",
            "many",
            "percent",
            "percentage",
            "change",
            "increase",
            "decrease",
            "total",
            "year",
            "years",
        }
        return {
            token
            for token in re.findall(r"[a-z][a-z0-9]+", query.lower())
            if token not in stop and len(token) > 2 and not token.isdigit()
        }

    def _query_years(self, query: str) -> set[str]:
        return set(re.findall(r"\b(?:19|20)\d{2}\b", query))

    def _calculation_operands(self, answer: Answer | None) -> list[float]:
        if answer is None:
            return []
        operands: list[float] = []
        for calculation in answer.calculations:
            if not calculation:
                continue
            expression = calculation.rsplit("=", 1)[0]
            if ":" in expression:
                expression = expression.split(":", 1)[1]
            numbers = self._numbers(expression)
            if len(numbers) > 1:
                operands.extend(numbers[:-1])
            else:
                operands.extend(numbers)
        return operands

    def _term_overlap(self, terms: set[str], text: str) -> int:
        if not terms:
            return 0
        text_terms = set(re.findall(r"[a-z][a-z0-9]+", text.lower()))
        return len(terms & text_terms)

    def _year_overlap(self, years: set[str], text: str) -> int:
        if not years:
            return 0
        return sum(1 for year in years if year in text)

    def _operand_overlap(self, operands: list[float], text: str) -> int:
        if not operands:
            return 0
        numbers = self._numbers(text)
        return sum(1 for operand in operands if any(self._close(operand, number) for number in numbers))

    def _numbers(self, text: str) -> list[float]:
        return [float(match.replace(",", "")) for match in re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text)]

    def _close(self, left: float, right: float) -> bool:
        return abs(left - right) <= max(0.1, abs(right) * 0.001)
