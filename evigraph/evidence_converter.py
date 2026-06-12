from __future__ import annotations

from evigraph.schema import EvidenceNode


class EvidenceConverter:
    def to_evidence_nodes(self, candidates: list[EvidenceNode | dict]) -> list[EvidenceNode]:
        nodes: list[EvidenceNode] = []
        for index, candidate in enumerate(candidates):
            if isinstance(candidate, EvidenceNode):
                nodes.append(candidate)
            else:
                nodes.append(
                    EvidenceNode(
                        node_id=str(candidate.get("node_id", f"candidate_{index}")),
                        node_type=str(candidate.get("node_type", "text")),
                        content=candidate.get("content", ""),
                        source_doc=candidate.get("source_doc"),
                        page_number=candidate.get("page_number"),
                        bbox=candidate.get("bbox"),
                        modality=str(candidate.get("modality", "text")),
                        confidence=float(candidate.get("confidence", 1.0)),
                        metadata=dict(candidate.get("metadata", {})),
                    )
                )
        return nodes
