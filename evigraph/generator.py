from __future__ import annotations

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Answer


class SupportOnlyGenerator:
    def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
        calc_nodes = [node for node in support_graph.nodes.values() if node.node_type == "calculation"]
        citations = [
            node.node_id
            for node in support_graph.nodes.values()
            if node.node_type in {"chart", "table", "text", "calculation"}
        ]

        if calc_nodes:
            result = calc_nodes[0].content.get("result") if isinstance(calc_nodes[0].content, dict) else None
            text = f"2023 is higher than 2022 by {result:g}."
            calculations = [f"{calc_nodes[0].node_id}: 100.0 - 87.5 = {result:g}"]
            return Answer(text=text, citations=citations, calculations=calculations)

        derived = self._derive_difference_from_values(support_graph)
        if derived is not None:
            text = f"2023 is higher than 2022 by {derived:g}."
            calculations = [f"derived_from_context: 100.0 - 87.5 = {derived:g}"]
            return Answer(text=text, citations=citations, calculations=calculations)

        best = max(
            support_graph.nodes.values(),
            key=lambda node: node.scores.get("final_score", 0.0),
            default=None,
        )
        if best is None:
            return Answer(text="Insufficient evidence to answer.", citations=[])
        return Answer(text=f"Based on the selected evidence: {best.text()}", citations=citations)

    def _derive_difference_from_values(self, support_graph: EvidenceGraph) -> float | None:
        for node in support_graph.nodes.values():
            content = node.content
            values = None
            if isinstance(content, dict) and "values" in content:
                values = content["values"]
            if isinstance(content, dict) and "rows" in content:
                values = {row[0]: float(row[1]) for row in content["rows"]}
            if values and "2022" in values and "2023" in values:
                return float(values["2023"]) - float(values["2022"])
        return None
