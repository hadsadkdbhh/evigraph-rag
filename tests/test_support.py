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


if __name__ == "__main__":
    unittest.main()
