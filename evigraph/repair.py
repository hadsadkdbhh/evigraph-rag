from __future__ import annotations

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
        if not self._should_repair(verification, answer):
            return answer, verification, None

        attempted = 0
        for support_graph in self._source_cluster_graphs(graph):
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
            if candidate_verification.get("answer_supported"):
                candidate_verification["repair_applied"] = True
                candidate_verification["repair_attempts"] = attempted
                return (
                    candidate,
                    candidate_verification,
                    Action(
                        "REPAIR_NUMERIC_ANSWER",
                        target_node_ids=list(candidate.citations),
                        params={"attempts": attempted},
                        estimated_cost={"tool_calls": 0, "latency_ms": 10 * attempted},
                        reason="Verifier rejected the initial row/operation grounding; accepted a source-local repaired answer.",
                    ),
                )

        repaired_verification = dict(verification)
        repaired_verification["repair_applied"] = False
        repaired_verification["repair_attempts"] = attempted
        return answer, repaired_verification, None

    def _should_repair(self, verification: dict, answer: Answer) -> bool:
        if verification.get("answer_supported"):
            return False
        if not answer.calculations:
            return False
        return verification.get("row_grounded") is False or verification.get("operation_semantics_checked") is False

    def _source_cluster_graphs(self, graph: EvidenceGraph) -> list[EvidenceGraph]:
        by_source: dict[str, list[EvidenceNode]] = {}
        for node in graph.nodes.values():
            if not node.source_doc:
                continue
            if self._is_risky(node):
                continue
            by_source.setdefault(str(node.source_doc), []).append(node)

        ranked_sources = sorted(
            by_source.items(),
            key=lambda item: self._source_rank_key(item[1]),
        )
        return [
            self._source_graph(graph, nodes)
            for _, nodes in ranked_sources[: self.max_source_clusters]
            if nodes and min(self._retrieval_rank(node) for node in nodes) <= self.max_repair_rank
        ]

    def _source_graph(self, graph: EvidenceGraph, nodes: list[EvidenceNode]) -> EvidenceGraph:
        support = EvidenceGraph()
        ordered_nodes = sorted(nodes, key=self._node_rank_key)[: self.max_nodes_per_source]
        ordered_ids = {node.node_id for node in ordered_nodes}
        for node in ordered_nodes:
            support.add_node(node)
        for edge in graph.edges:
            if edge.source in ordered_ids and edge.target in ordered_ids:
                support.edges.append(edge)
        return support

    def _source_rank_key(self, nodes: list[EvidenceNode]) -> tuple[int, float, str]:
        best_rank = min(self._retrieval_rank(node) for node in nodes)
        best_score = max(float(node.scores.get("final_score", 0.0)) for node in nodes)
        source = str(nodes[0].source_doc or "")
        return (best_rank, -best_score, source)

    def _node_rank_key(self, node: EvidenceNode) -> tuple[int, int, float, str]:
        return (
            1 if node.metadata.get("neighbor_context") else 0,
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
