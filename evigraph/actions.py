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
        selected = list(selected)

        selected.extend(self._expand_source_context(selected, graph, actions))
        parsed_nodes = self._parse_structured_nodes(selected, graph, actions)
        selected.extend(parsed_nodes)

        calculation_pair = self._calculation_pair(query_lower)
        calculation_inputs = self._calculation_inputs(selected)
        if calculation_pair and self._requires_calculation(query_lower) and calculation_inputs:
            action = Action(
                action_type="RUN_CALCULATION",
                target_node_ids=[node.node_id for node in calculation_inputs],
                params={"target_year": calculation_pair[0], "base_year": calculation_pair[1]},
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

        actions.append(Action(action_type="STOP", target_node_ids=[], reason="Selected evidence is sufficient."))
        return selected, graph, actions

    def _expand_source_context(
        self,
        selected: list[EvidenceNode],
        graph: EvidenceGraph,
        actions: list[Action],
    ) -> list[EvidenceNode]:
        selected_ids = {node.node_id for node in selected}
        selected_sources = {node.source_doc for node in selected if node.source_doc}
        expanded = []
        for node in graph.nodes.values():
            if node.node_id in selected_ids:
                continue
            if node.source_doc not in selected_sources:
                continue
            if node.metadata.get("loader") != "source_doc_oracle":
                continue
            node.metadata["selection_status"] = "selected"
            expanded.append(node)
        if expanded:
            actions.append(
                Action(
                    action_type="EXPAND_SOURCE_CONTEXT",
                    target_node_ids=[node.node_id for node in expanded],
                    estimated_cost={"tool_calls": 0, "latency_ms": 5},
                    reason="Oracle source_doc evaluation includes the full source context for numerical evidence.",
                )
            )
        return expanded

    def _requires_calculation(self, query_lower: str) -> bool:
        if "percent" in query_lower or "percentage" in query_lower or "growth rate" in query_lower:
            return False
        return any(phrase in query_lower for phrase in ["how much higher", "difference", "increase", "decrease"])

    def _calculation_pair(self, query_lower: str) -> tuple[str, str] | None:
        import re

        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        if " from " in query_lower and " to " in query_lower:
            return years[1], years[0]
        return years[0], years[1]

    def _has_numeric_evidence(self, selected: list[EvidenceNode]) -> bool:
        return any(node.modality in {"chart", "table"} for node in selected)

    def _parse_structured_nodes(
        self,
        selected: list[EvidenceNode],
        graph: EvidenceGraph,
        actions: list[Action],
    ) -> list[EvidenceNode]:
        parsed_nodes: list[EvidenceNode] = []
        table_targets = [node for node in selected if node.node_type == "table" and self._extract_values(node)]
        if table_targets:
            actions.append(
                Action(
                    action_type="PARSE_TABLE",
                    target_node_ids=[node.node_id for node in table_targets],
                    estimated_cost={"tool_calls": 1, "latency_ms": 30},
                    reason="Structured table evidence is needed for grounded calculation.",
                )
            )

        for node in table_targets:
            parsed_id = f"parsed_{node.node_id}"
            if parsed_id in graph.nodes:
                parsed_nodes.append(graph.nodes[parsed_id])
                continue
            parsed_node = EvidenceNode(
                node_id=parsed_id,
                node_type="table",
                content=node.content,
                source_doc=node.source_doc,
                page_number=node.page_number,
                bbox=node.bbox,
                modality="table",
                confidence=node.confidence,
                scores=dict(node.scores),
                cost={"tokens": 8, "tool_calls": 1, "latency_ms": 30},
                metadata={"selection_status": "selected", "parser": "table_passthrough"},
            )
            graph.add_node(parsed_node)
            graph.add_edge(parsed_node.node_id, node.node_id, "derived_from", 1.0)
            parsed_nodes.append(parsed_node)
        return parsed_nodes

    def _calculation_inputs(self, selected: list[EvidenceNode]) -> list[EvidenceNode]:
        parsed = [node for node in selected if node.node_id.startswith("parsed_") and self._extract_values(node)]
        if parsed:
            chart_nodes = [node for node in selected if node.modality == "chart" and self._extract_values(node)]
            return chart_nodes + parsed
        return [node for node in selected if node.modality in {"chart", "table"} and self._extract_values(node)]

    def _run_mock_calculation(self, action: Action, graph: EvidenceGraph) -> EvidenceNode | None:
        target_year = str(action.params.get("target_year", "2023"))
        base_year = str(action.params.get("base_year", "2022"))
        for target_id in action.target_node_ids:
            node = graph.nodes[target_id]
            values = self._extract_values(node)
            if values and base_year in values and target_year in values:
                diff = float(values[target_year]) - float(values[base_year])
                calc_node = EvidenceNode(
                    node_id=f"calc_{target_year}_minus_{base_year}",
                    node_type="calculation",
                    content={
                        "expression": f"{target_year} - {base_year}",
                        "target_year": target_year,
                        "base_year": base_year,
                        "target_value": float(values[target_year]),
                        "base_value": float(values[base_year]),
                        "result": diff,
                    },
                    source_doc=node.source_doc,
                    modality="calculation",
                    cost={"tokens": 8, "tool_calls": 1, "latency_ms": 20},
                    metadata={"selection_status": "selected"},
                )
                graph.add_node(calc_node)
                graph.add_edge(calc_node.node_id, node.node_id, "computed_from", 1.0)
                return calc_node
        return None

    def _extract_values(self, node: EvidenceNode) -> dict[str, float]:
        content = node.content
        if not isinstance(content, dict):
            return {}
        if "values" in content and isinstance(content["values"], dict):
            return {str(key): float(value) for key, value in content["values"].items()}
        if "rows" in content:
            values = {}
            for row in content["rows"]:
                if len(row) >= 2:
                    try:
                        values[str(row[0])] = float(row[1])
                    except (TypeError, ValueError):
                        continue
            return values
        return {}
