from __future__ import annotations

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import EvidenceNode


class SupportSubgraphExtractor:
    def extract(self, query: str, graph: EvidenceGraph, selected: list[EvidenceNode]) -> EvidenceGraph:
        support = EvidenceGraph()
        required_ids: list[str] = []
        seen_ids: set[str] = set()
        for node in selected:
            self._add_required(node.node_id, required_ids, seen_ids)
        selected_ids = set(seen_ids)

        for node in selected:
            for edge in graph.outgoing(node.node_id):
                if edge.edge_type in {"computed_from", "derived_from"}:
                    self._add_required(edge.target, required_ids, seen_ids)
                if edge.edge_type in {"source", "support"} and self._is_top_retrieval_neighbor(
                    graph.nodes.get(edge.target)
                ):
                    self._add_required(edge.target, required_ids, seen_ids)

        for node_id in required_ids:
            if node_id in graph.nodes:
                node = graph.nodes[node_id]
                if node_id in selected_ids or (
                    node.scores.get("misleading_risk", 0.0) < 0.65
                    and node.scores.get("contradiction_risk", 0.0) < 0.65
                ):
                    support.add_node(node)

        for edge in graph.edges:
            if edge.source in support.nodes and edge.target in support.nodes:
                support.edges.append(edge)
        return support

    def _add_required(self, node_id: str, required_ids: list[str], seen_ids: set[str]) -> None:
        if node_id in seen_ids:
            return
        required_ids.append(node_id)
        seen_ids.add(node_id)

    def _is_top_retrieval_neighbor(self, node: EvidenceNode | None) -> bool:
        if node is None:
            return False
        try:
            rank = int(node.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            return False
        if rank > 4:
            return False
        return node.scores.get("misleading_risk", 0.0) < 0.65 and node.scores.get("contradiction_risk", 0.0) < 0.65
