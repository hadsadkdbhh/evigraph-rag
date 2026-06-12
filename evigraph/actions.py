from __future__ import annotations

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Action, EvidenceNode


class EvidenceActionController:
    def maybe_refine(
        self,
        query: str,
        selected: list[EvidenceNode],
        graph: EvidenceGraph,
    ) -> tuple[list[EvidenceNode], EvidenceGraph, list[Action]]:
        actions: list[Action] = []
        query_lower = query.lower()

        if self._requires_calculation(query_lower) and self._has_numeric_evidence(selected):
            action = Action(
                action_type="RUN_CALCULATION",
                target_node_ids=[node.node_id for node in selected if node.modality in {"chart", "table"}],
                estimated_cost={"tool_calls": 1, "latency_ms": 20},
                reason="Query asks for a numerical comparison.",
            )
            calc_node = self._run_mock_calculation(action, graph)
            if calc_node:
                selected.append(calc_node)
            actions.append(action)

        risky_nodes = [
            node
            for node in graph.nodes.values()
            if node.scores.get("misleading_risk", 0.0) >= 0.65 or node.scores.get("contradiction_risk", 0.0) >= 0.65
        ]
        if risky_nodes:
            actions.append(
                Action(
                    action_type="DISCARD_NOISY_NODE",
                    target_node_ids=[node.node_id for node in risky_nodes],
                    reason="Risk-aware selector rejected misleading or contradictory candidates.",
                )
            )

        actions.append(Action(action_type="STOP", target_node_ids=[], reason="Selected evidence is sufficient for MVP-0."))
        return selected, graph, actions

    def _requires_calculation(self, query_lower: str) -> bool:
        return any(phrase in query_lower for phrase in ["how much higher", "difference", "increase", "decrease"])

    def _has_numeric_evidence(self, selected: list[EvidenceNode]) -> bool:
        return any(node.modality in {"chart", "table"} for node in selected)

    def _run_mock_calculation(self, action: Action, graph: EvidenceGraph) -> EvidenceNode | None:
        for target_id in action.target_node_ids:
            node = graph.nodes[target_id]
            content = node.content
            values = None
            if isinstance(content, dict) and "values" in content:
                values = content["values"]
            if isinstance(content, dict) and "rows" in content:
                values = {row[0]: float(row[1]) for row in content["rows"]}
            if values and "2022" in values and "2023" in values:
                diff = float(values["2023"]) - float(values["2022"])
                calc_node = EvidenceNode(
                    node_id="calc_2023_minus_2022",
                    node_type="calculation",
                    content={"expression": "2023 - 2022", "result": diff},
                    source_doc=node.source_doc,
                    modality="calculation",
                    cost={"tokens": 8, "tool_calls": 1, "latency_ms": 20},
                    metadata={"selection_status": "selected"},
                )
                graph.add_node(calc_node)
                graph.add_edge(calc_node.node_id, node.node_id, "computed_from", 1.0)
                return calc_node
        return None
