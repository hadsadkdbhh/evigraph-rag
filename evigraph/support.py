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
                if edge.edge_type in {"source", "support"} and self._is_support_neighbor(
                    graph.nodes.get(edge.target),
                    graph.nodes.get(edge.source),
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

    def _is_support_neighbor(self, node: EvidenceNode | None, source_node: EvidenceNode | None) -> bool:
        if node is None:
            return False
        source_node_id = source_node.node_id if source_node else ""
        source_chunk_id = str(source_node.metadata.get("chunk_id", "")) if source_node else ""
        if (
            node.metadata.get("neighbor_context")
            and (
                node.metadata.get("expanded_from") == source_node_id
                or (
                    source_chunk_id
                    and node.metadata.get("expanded_from_chunk_id") == source_chunk_id
                )
            )
            and node.scores.get("misleading_risk", 0.0) < 0.65
            and node.scores.get("contradiction_risk", 0.0) < 0.65
        ):
            return True
        try:
            rank = int(node.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            return False
        if rank > 4:
            return False
        return node.scores.get("misleading_risk", 0.0) < 0.65 and node.scores.get("contradiction_risk", 0.0) < 0.65
