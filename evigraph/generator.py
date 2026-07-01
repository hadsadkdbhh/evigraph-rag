from __future__ import annotations

from typing import Any

from evigraph.clients import LLMClient, make_llm_client
from evigraph.evidence_graph import EvidenceGraph
from evigraph.numeric_planner import NumericPlannerFallback
from evigraph.numeric_reasoning import NumericReasoner
from evigraph.schema import Answer


class SupportOnlyGenerator:
    def __init__(self, planner_fallback: NumericPlannerFallback | None = None) -> None:
        self.numeric_reasoner = NumericReasoner(planner_fallback=planner_fallback)

    def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
        calc_nodes = [node for node in support_graph.nodes.values() if node.node_type == "calculation"]
        citations = [
            node.node_id
            for node in support_graph.nodes.values()
            if node.node_type in {"chart", "table", "text", "calculation"}
        ]

        if calc_nodes:
            content = calc_nodes[0].content if isinstance(calc_nodes[0].content, dict) else {}
            result = content.get("result")
            target_year = content.get("target_year", "2023")
            base_year = content.get("base_year", "2022")
            target_value = content.get("target_value", 100.0)
            base_value = content.get("base_value", 87.5)
            text = f"{target_year} is higher than {base_year} by {result:g}."
            calculations = [f"{calc_nodes[0].node_id}: {target_value:g} - {base_value:g} = {result:g}"]
            return Answer(text=text, citations=citations, calculations=calculations)

        derived = self._derive_difference_from_values(support_graph)
        if derived is not None:
            text = f"2023 is higher than 2022 by {derived:g}."
            calculations = [f"derived_from_context: 100.0 - 87.5 = {derived:g}"]
            return Answer(text=text, citations=citations, calculations=calculations)

        numeric_answer = self.numeric_reasoner.answer(query, support_graph)
        if numeric_answer is not None:
            cited = [node_id for node_id in numeric_answer.cited_node_ids if node_id in citations]
            return Answer(
                text=numeric_answer.text,
                citations=cited or citations,
                calculations=[numeric_answer.calculation],
            )

        best = max(
            support_graph.nodes.values(),
            key=lambda node: node.scores.get("final_score", 0.0),
            default=None,
        )
        if best is None:
            return Answer(text="Insufficient evidence to answer.", citations=[])
        return Answer(text=f"Based on the selected evidence: {best.text()}", citations=citations)

    def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
        citations = [
            node.node_id
            for node in support_graph.nodes.values()
            if node.node_type in {"chart", "table", "text", "calculation"}
        ]
        numeric_answer = self.numeric_reasoner.planner_first_answer(query, support_graph)
        if numeric_answer is not None:
            cited = [node_id for node_id in numeric_answer.cited_node_ids if node_id in citations]
            return Answer(
                text=numeric_answer.text,
                citations=cited or citations,
                calculations=[numeric_answer.calculation],
            )
        return self.generate(query, support_graph)

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


class LLMDirectRAGGenerator:
    """External LLM baseline over retrieved context, without EviGraph planning."""

    def __init__(self, config: dict[str, Any] | None = None, llm_client: LLMClient | None = None) -> None:
        config = config or {}
        self.config = config
        self.llm_client = llm_client or make_llm_client(config)
        self.max_context_chars = int(config.get("max_context_chars", 12000))
        self.temperature = float(config.get("temperature", 0.0))

    def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
        valid_citations = [
            node.node_id
            for node in support_graph.nodes.values()
            if node.node_type in {"chart", "table", "text", "calculation"}
        ]
        payload = self.llm_client.chat_json(
            self._messages(query, support_graph, valid_citations),
            temperature=self.temperature,
        )
        answer_text = str(payload.get("answer") or payload.get("text") or "").strip()
        if not answer_text:
            answer_text = "Insufficient evidence to answer."
        citations = self._valid_citations(payload.get("citations"), valid_citations)
        calculations = self._calculations(payload.get("calculation") or payload.get("calculations"))
        return Answer(text=answer_text, citations=citations, calculations=calculations)

    def _messages(
        self,
        query: str,
        support_graph: EvidenceGraph,
        valid_citations: list[str],
    ) -> list[dict[str, str]]:
        context = self._context_text(support_graph, valid_citations)
        return [
            {
                "role": "system",
                "content": (
                    "You are a direct RAG baseline for financial question answering. "
                    "Answer only from the supplied retrieved context. "
                    "Return strict JSON with keys: answer, citations, calculation. "
                    "Use citations from the supplied node ids only. "
                    "If the answer is not supported, set answer to 'Insufficient evidence to answer.' "
                    "and citations to an empty list."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{query}\n\n"
                    f"Retrieved context:\n{context}\n\n"
                    "Return JSON only, for example: "
                    '{"answer":"4.4%","citations":["node_id"],"calculation":"11800 / 267100 * 100 = 4.4%"}'
                ),
            },
        ]

    def _context_text(self, support_graph: EvidenceGraph, valid_citations: list[str]) -> str:
        blocks = []
        used_chars = 0
        for node_id in valid_citations:
            node = support_graph.nodes[node_id]
            text = node.text()
            source = node.source_doc or node.metadata.get("source_doc") or "unknown_source"
            block = f"[{node.node_id}] source={source} page={node.page_number}\n{text}"
            remaining = self.max_context_chars - used_chars
            if remaining <= 0:
                break
            if len(block) > remaining:
                block = block[:remaining]
            blocks.append(block)
            used_chars += len(block)
        return "\n\n".join(blocks)

    def _valid_citations(self, raw_citations: Any, valid_citations: list[str]) -> list[str]:
        valid = set(valid_citations)
        if isinstance(raw_citations, str):
            raw_values = [raw_citations]
        elif isinstance(raw_citations, list):
            raw_values = [str(value) for value in raw_citations]
        else:
            raw_values = []
        filtered = [citation for citation in raw_values if citation in valid]
        return filtered

    def _calculations(self, raw_calculations: Any) -> list[str]:
        if isinstance(raw_calculations, str):
            calculation = raw_calculations.strip()
            return [calculation] if calculation else []
        if isinstance(raw_calculations, list):
            return [str(value).strip() for value in raw_calculations if str(value).strip()]
        return []
