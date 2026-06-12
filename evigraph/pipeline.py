from __future__ import annotations

from typing import Any

from evigraph.actions import EvidenceActionController
from evigraph.evidence_converter import EvidenceConverter
from evigraph.evidence_graph import EvidenceGraphBuilder
from evigraph.generator import SupportOnlyGenerator
from evigraph.logging_utils import RunLogger
from evigraph.retrieval import MockRetriever
from evigraph.scorer import RuleBasedUtilityRiskScorer
from evigraph.selector import EvidenceSetSelector
from evigraph.support import SupportSubgraphExtractor
from evigraph.verifier import ClaimVerifier


class EviGraphPipeline:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        selection_config = config.get("selection", {})
        run_config = config.get("run", {})
        self.retriever = MockRetriever()
        self.converter = EvidenceConverter()
        self.graph_builder = EvidenceGraphBuilder()
        self.scorer = RuleBasedUtilityRiskScorer()
        self.selector = EvidenceSetSelector(
            max_nodes=int(selection_config.get("max_nodes", 4)),
            risk_threshold=float(selection_config.get("risk_threshold", 0.65)),
        )
        self.actions = EvidenceActionController()
        self.support_extractor = SupportSubgraphExtractor()
        self.generator = SupportOnlyGenerator()
        self.verifier = ClaimVerifier()
        self.logger = RunLogger(output_dir=str(run_config.get("output_dir", "outputs/runs")))

    def run(self, query: str, corpus_path: str | None = None, top_k: int = 8) -> dict[str, Any]:
        candidates = self.retriever.retrieve(query, corpus_path, top_k=top_k)
        self.logger.trace("retrieve", {"candidate_ids": [node.node_id for node in candidates]})

        nodes = self.converter.to_evidence_nodes(candidates)
        self.logger.trace("convert", {"node_count": len(nodes)})

        graph = self.graph_builder.build(query, nodes)
        self.logger.trace("build_graph", {"node_count": len(graph.nodes), "edge_count": len(graph.edges)})

        scores = self.scorer.score_all(query, graph)
        self.logger.trace("score", {"scores": {node_id: score.to_dict() for node_id, score in scores.items()}})

        selected = self.selector.select(query, graph, scores)
        self.logger.trace("select", {"selected_ids": [node.node_id for node in selected]})

        selected, graph, actions = self.actions.maybe_refine(query, selected, graph)
        self.logger.trace("actions", {"actions": [action.to_dict() for action in actions]})

        support_graph = self.support_extractor.extract(query, graph, selected)
        self.logger.trace("support_subgraph", {"node_ids": list(support_graph.nodes.keys())})

        answer = self.generator.generate(query, support_graph)
        verification = self.verifier.verify(query, answer, support_graph)
        self.logger.trace("verify", verification)

        artifacts = self.logger.save(query, graph, support_graph, selected, actions, answer, verification)
        return {
            "answer": answer.to_dict(),
            "selected_ids": [node.node_id for node in selected],
            "actions": [action.to_dict() for action in actions],
            "verification": verification,
            "artifacts": artifacts,
        }
