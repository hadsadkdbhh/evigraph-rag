from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from evigraph.schema import EvidenceEdge, EvidenceNode


@dataclass
class EvidenceGraph:
    nodes: dict[str, EvidenceNode] = field(default_factory=dict)
    edges: list[EvidenceEdge] = field(default_factory=list)

    def add_node(self, node: EvidenceNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0, **metadata: Any) -> None:
        if source in self.nodes and target in self.nodes:
            self.edges.append(EvidenceEdge(source, target, edge_type, weight, metadata))

    def outgoing(self, node_id: str, edge_type: str | None = None) -> list[EvidenceEdge]:
        return [
            edge
            for edge in self.edges
            if edge.source == node_id and (edge_type is None or edge.edge_type == edge_type)
        ]

    def incoming(self, node_id: str, edge_type: str | None = None) -> list[EvidenceEdge]:
        return [
            edge
            for edge in self.edges
            if edge.target == node_id and (edge_type is None or edge.edge_type == edge_type)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }


class EvidenceGraphBuilder:
    def build(self, query: str, nodes: list[EvidenceNode]) -> EvidenceGraph:
        graph = EvidenceGraph()
        for node in nodes:
            graph.add_node(node)

        by_source: dict[str, list[EvidenceNode]] = defaultdict(list)
        for node in nodes:
            if node.source_doc:
                by_source[node.source_doc].append(node)

        for source_nodes in by_source.values():
            for left in source_nodes:
                for right in source_nodes:
                    if left.node_id != right.node_id:
                        graph.add_edge(left.node_id, right.node_id, "source", 0.5)

        for node in nodes:
            if node.metadata.get("is_conflicting"):
                for other in nodes:
                    if other.node_id != node.node_id and other.modality in {"chart", "table"}:
                        graph.add_edge(node.node_id, other.node_id, "contradiction", 0.8)
            if node.modality in {"chart", "table"}:
                for other in nodes:
                    if other.node_id != node.node_id and other.source_doc == node.source_doc:
                        graph.add_edge(node.node_id, other.node_id, "support", 0.6)
        return graph
