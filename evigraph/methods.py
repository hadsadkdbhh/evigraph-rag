from __future__ import annotations

from typing import Any

from evigraph.actions import EvidenceActionController
from evigraph.evidence_converter import EvidenceConverter
from evigraph.evidence_graph import EvidenceGraph, EvidenceGraphBuilder
from evigraph.generator import LLMDirectRAGGenerator, SupportOnlyGenerator
from evigraph.logging_utils import RunLogger
from evigraph.numeric_planner import NumericPlannerFallback
from evigraph.repair import VerifierGuidedRepairer
from evigraph.retrieval import CorpusRetriever
from evigraph.schema import Action, Answer, EvidenceNode, EvidenceScore
from evigraph.scorer import make_scorer
from evigraph.selector import EvidenceSetSelector
from evigraph.support import SupportSubgraphExtractor
from evigraph.verifier import ClaimVerifier


METHODS = [
    "llm_direct_rag",
    "direct_rag",
    "topk",
    "retrieve_then_program",
    "full_context",
    "utility_only",
    "evigraph_wo_risk",
    "evigraph_wo_operation_planner",
    "evigraph_wo_verifier_grounded_rejection",
    "evigraph_wo_verifier",
    "evigraph_wo_support",
    "full_evigraph",
]


class MethodRunner:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        self.config = config
        selection_config = config.get("selection", {})
        self.max_nodes = int(selection_config.get("max_nodes", 4))
        self.risk_threshold = float(selection_config.get("risk_threshold", 0.65))
        self.output_dir = str(config.get("run", {}).get("output_dir", "outputs/runs"))
        self.retriever = CorpusRetriever()
        self.converter = EvidenceConverter()
        self.graph_builder = EvidenceGraphBuilder()
        self.scorer = make_scorer(config.get("scoring", {}))
        self.actions = EvidenceActionController()
        self.support_extractor = SupportSubgraphExtractor()
        self.generator = SupportOnlyGenerator(
            planner_fallback=NumericPlannerFallback.from_config(config.get("numeric_planner", {}))
        )
        self.generator_without_planner = SupportOnlyGenerator(planner_fallback=None)
        self.llm_direct_generator: LLMDirectRAGGenerator | None = None
        self.verifier = ClaimVerifier()
        self.repairer = VerifierGuidedRepairer()

    def run(
        self,
        query: str,
        method: str = "full_evigraph",
        corpus_path: str | None = None,
        source_doc: str | None = None,
        retrieval_mode: str = "oracle_doc",
        top_k: int = 8,
        log_run: bool = True,
    ) -> dict[str, Any]:
        if method not in METHODS:
            raise ValueError(f"Unknown method {method!r}. Expected one of: {', '.join(METHODS)}")

        logger = RunLogger(self.output_dir, run_name=method) if log_run else None
        candidates = self.retriever.retrieve(
            query,
            corpus_path,
            top_k=top_k,
            source_doc=source_doc,
            retrieval_mode=retrieval_mode,
        )
        self._trace(logger, "retrieve", {"method": method, "candidate_ids": [node.node_id for node in candidates]})

        nodes = self.converter.to_evidence_nodes(candidates)
        graph = self.graph_builder.build(query, nodes)
        scores = self.scorer.score_all(query, graph)
        self._trace(logger, "score", {"scores": {node_id: score.to_dict() for node_id, score in scores.items()}})

        selected, actions, support_graph, verification = self._run_method(query, method, nodes, graph, scores)
        if method == "llm_direct_rag":
            generator = self._llm_direct_generator()
        elif method in {"direct_rag", "evigraph_wo_operation_planner"}:
            generator = self.generator_without_planner
        else:
            generator = self.generator
        answer = generator.generate(query, support_graph)
        if method == "evigraph_wo_verifier":
            verification = self._skipped_verification(answer)
        else:
            verification = self.verifier.verify(query, answer, support_graph)
            if method == "full_evigraph" and retrieval_mode in {"oracle_doc", "source_rerank"}:
                answer, verification, repair_action = self.repairer.repair(
                    query,
                    answer,
                    verification,
                    graph,
                    generator,
                    self.verifier,
                )
                if repair_action is not None:
                    actions.append(repair_action)
            verifier_grounded_rejection_enabled = method not in {
                "llm_direct_rag",
                "direct_rag",
                "evigraph_wo_verifier_grounded_rejection",
            }
            if verifier_grounded_rejection_enabled and verification.get("row_grounded") is False:
                answer = Answer(
                    text="Insufficient evidence to answer.",
                    citations=[],
                    calculations=answer.calculations,
                )
                verification = self.verifier.verify(query, answer, support_graph)
                verification["missing_evidence"].append("Rejected numeric answer because calculation row did not match query.")
            verify_action = Action(
                "VERIFY_CLAIM",
                target_node_ids=list(answer.citations),
                estimated_cost={"tool_calls": 1, "latency_ms": 20},
                reason="Check answer claims against the minimal support subgraph.",
            )
            actions.append(verify_action)
            self._add_verifier_judgment_node(support_graph, verification)

        cost = self._cost(selected, actions)
        self._trace(logger, "select", {"selected_ids": [node.node_id for node in selected]})
        self._trace(logger, "actions", {"actions": [action.to_dict() for action in actions]})
        self._trace(logger, "verify", verification)

        artifacts = {}
        if logger:
            artifacts = logger.save(query, graph, support_graph, selected, actions, answer, verification)

        return {
            "method": method,
            "answer": answer.to_dict(),
            "selected_ids": [node.node_id for node in selected],
            "actions": [action.to_dict() for action in actions],
            "verification": verification,
            "cost": cost,
            "artifacts": artifacts,
        }

    def _run_method(
        self,
        query: str,
        method: str,
        nodes: list[EvidenceNode],
        graph: EvidenceGraph,
        scores: dict[str, EvidenceScore],
    ) -> tuple[list[EvidenceNode], list[Action], EvidenceGraph, dict[str, Any]]:
        actions: list[Action] = []
        verification: dict[str, Any] = {}

        if method == "direct_rag":
            selected = nodes[: self.max_nodes]
            support_graph = self._selected_graph(graph, selected)
            actions = [Action("STOP", [], reason="Direct RAG baseline uses retrieval-order context without operation planner.")]
            return selected, actions, support_graph, verification

        if method == "llm_direct_rag":
            selected = nodes[: self.max_nodes]
            support_graph = self._selected_graph(graph, selected)
            actions = [Action("STOP", [], reason="LLM Direct RAG baseline sends retrieval-order context directly to an external LLM.")]
            return selected, actions, support_graph, verification

        if method == "topk":
            selected = nodes[: self.max_nodes]
            support_graph = self._selected_graph(graph, selected)
            actions = [Action("STOP", [], reason="Top-k baseline uses retrieval order only.")]
            return selected, actions, support_graph, verification

        if method == "retrieve_then_program":
            selected = nodes[: self.max_nodes]
            support_graph = self._selected_graph(graph, selected)
            actions = [Action("STOP", [], reason="Retrieve-then-program baseline uses retrieval-order context and local planner.")]
            return selected, actions, support_graph, verification

        if method == "full_context":
            selected = nodes
            actions = [Action("STOP", [], reason="Full-context baseline passes all candidates.")]
            return selected, actions, graph, verification

        if method == "utility_only":
            selected = sorted(nodes, key=lambda node: node.scores.get("utility", 0.0), reverse=True)[: self.max_nodes]
            support_graph = self._selected_graph(graph, selected)
            actions = [Action("STOP", [], reason="Utility-only baseline ignores risk signals.")]
            return selected, actions, support_graph, verification

        risk_threshold = 2.0 if method == "evigraph_wo_risk" else self.risk_threshold
        selected = EvidenceSetSelector(max_nodes=self.max_nodes, risk_threshold=risk_threshold).select(query, graph, scores)
        selected, graph, actions = self.actions.maybe_refine(query, selected, graph)

        if method == "evigraph_wo_support":
            support_graph = self._selected_graph(graph, selected)
        else:
            support_graph = self.support_extractor.extract(query, graph, selected)
        return selected, actions, support_graph, verification

    def _selected_graph(self, graph: EvidenceGraph, selected: list[EvidenceNode]) -> EvidenceGraph:
        selected_ids = {node.node_id for node in selected}
        support_graph = EvidenceGraph()
        for node in selected:
            support_graph.add_node(node)
        for edge in graph.edges:
            if edge.source in selected_ids and edge.target in selected_ids:
                support_graph.edges.append(edge)
        return support_graph

    def _llm_direct_generator(self) -> LLMDirectRAGGenerator:
        if self.llm_direct_generator is None:
            self.llm_direct_generator = LLMDirectRAGGenerator(self.config.get("llm_direct_rag", {}))
        return self.llm_direct_generator

    def _cost(self, selected: list[EvidenceNode], actions: list[Action]) -> dict[str, float]:
        return {
            "selected_tokens": sum(float(node.cost.get("tokens", 0)) for node in selected),
            "tool_calls": sum(float(node.cost.get("tool_calls", 0)) for node in selected)
            + sum(float(action.estimated_cost.get("tool_calls", 0)) for action in actions),
            "latency_ms": sum(float(node.cost.get("latency_ms", 0)) for node in selected)
            + sum(float(action.estimated_cost.get("latency_ms", 0)) for action in actions),
        }

    def _skipped_verification(self, answer: Any) -> dict[str, Any]:
        return {
            "answer_supported": False,
            "unsupported_claims": [],
            "contradictions": [],
            "missing_evidence": ["Verifier disabled by ablation."],
            "citation_correct": False,
            "confidence": 0.0,
            "context_utilization": "not_checked",
            "arithmetically_supported": False,
            "calculation_supported": False,
            "period_grounded": False,
            "operation_semantics_checked": False,
            "row_operation_grounded": False,
            "semantically_grounded": False,
            "row_grounded": False,
        }

    def _trace(self, logger: RunLogger | None, step: str, payload: dict[str, Any]) -> None:
        if logger:
            logger.trace(step, payload)

    def _add_verifier_judgment_node(self, support_graph: EvidenceGraph, verification: dict[str, Any]) -> None:
        judgment = EvidenceNode(
            node_id="verifier_judgment",
            node_type="verifier_judgment",
            content=verification,
            modality="text",
            confidence=float(verification.get("confidence", 0.0)),
            cost={"tokens": 20, "tool_calls": 1, "latency_ms": 20},
            metadata={"selection_status": "selected"},
        )
        support_graph.add_node(judgment)
        for citation in verification.get("checked_citations", []):
            support_graph.add_edge(judgment.node_id, citation, "support", 1.0)
