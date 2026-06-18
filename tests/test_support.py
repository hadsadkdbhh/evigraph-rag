from __future__ import annotations

import unittest

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import EvidenceNode
from evigraph.support import SupportSubgraphExtractor


class SupportSubgraphExtractorTest(unittest.TestCase):
    def test_keeps_selected_node_even_at_risk_threshold(self) -> None:
        graph = EvidenceGraph()
        selected = EvidenceNode(
            node_id="selected_full_source",
            node_type="text",
            content="answer-bearing full source context",
            source_doc="report.md",
            scores={"misleading_risk": 0.65, "contradiction_risk": 0.0},
        )
        graph.add_node(selected)

        support = SupportSubgraphExtractor().extract("what percentage?", graph, [selected])

        self.assertIn("selected_full_source", support.nodes)

    def test_adds_top_retrieval_same_source_neighbor(self) -> None:
        graph = EvidenceGraph()
        selected = EvidenceNode(
            node_id="selected_chunk",
            node_type="text",
            content="selected table fragment",
            source_doc="report.md",
            scores={"misleading_risk": 0.0, "contradiction_risk": 0.0},
            metadata={"retrieval_rank": 1},
        )
        neighbor = EvidenceNode(
            node_id="neighbor_chunk",
            node_type="text",
            content="adjacent table fragment with missing row",
            source_doc="report.md",
            scores={"misleading_risk": 0.0, "contradiction_risk": 0.0},
            metadata={"retrieval_rank": 2},
        )
        graph.add_node(selected)
        graph.add_node(neighbor)
        graph.add_edge("selected_chunk", "neighbor_chunk", "source", 0.5)

        support = SupportSubgraphExtractor().extract("what percentage?", graph, [selected])

        self.assertIn("selected_chunk", support.nodes)
        self.assertIn("neighbor_chunk", support.nodes)

    def test_does_not_add_risky_retrieval_neighbor(self) -> None:
        graph = EvidenceGraph()
        selected = EvidenceNode(
            node_id="selected_chunk",
            node_type="text",
            content="selected table fragment",
            source_doc="report.md",
            scores={"misleading_risk": 0.0, "contradiction_risk": 0.0},
            metadata={"retrieval_rank": 1},
        )
        neighbor = EvidenceNode(
            node_id="forecast_chunk",
            node_type="text",
            content="draft forecast fragment",
            source_doc="report.md",
            scores={"misleading_risk": 0.7, "contradiction_risk": 0.0},
            metadata={"retrieval_rank": 2},
        )
        graph.add_node(selected)
        graph.add_node(neighbor)
        graph.add_edge("selected_chunk", "forecast_chunk", "source", 0.5)

        support = SupportSubgraphExtractor().extract("what percentage?", graph, [selected])

        self.assertIn("selected_chunk", support.nodes)
        self.assertNotIn("forecast_chunk", support.nodes)


if __name__ == "__main__":
    unittest.main()
