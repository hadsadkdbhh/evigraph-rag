from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evigraph.evidence_graph import EvidenceGraph
from evigraph.document_loader import DocumentChunk
from evigraph.retrieval import BM25Retriever, CorpusRetriever
from evigraph.schema import EvidenceNode, EvidenceScore
from evigraph.selector import EvidenceSetSelector


class RetrievalSelectionTest(unittest.TestCase):
    def test_bm25_records_retrieval_rank(self) -> None:
        chunks = [
            DocumentChunk("a", "alpha target value 10", "a.md"),
            DocumentChunk("b", "target value 20", "b.md"),
        ]

        nodes = BM25Retriever(chunks).retrieve("target value", top_k=2)

        self.assertEqual(nodes[0].metadata["retrieval_rank"], 1)
        self.assertEqual(nodes[1].metadata["retrieval_rank"], 2)

    def test_open_retrieval_adds_adjacent_chunk_context(self) -> None:
        chunks = [
            DocumentChunk("case_0_0", "fuel recovery query hit amount 98", "case.md", metadata={"char_start": 0}),
            DocumentChunk("case_0_1", "middle table row with deferred revisions 59.1", "case.md", metadata={"char_start": 900}),
            DocumentChunk("case_0_2", "unrelated trailing discussion", "case.md", metadata={"char_start": 1800}),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.json"
            index_path.write_text(
                json.dumps({"chunks": [chunk.to_dict() for chunk in chunks]}),
                encoding="utf-8",
            )

            nodes = CorpusRetriever().retrieve(
                "fuel recovery",
                str(index_path),
                top_k=1,
                retrieval_mode="open",
            )

        chunk_ids = [node.metadata.get("chunk_id") for node in nodes]
        self.assertEqual(chunk_ids[:2], ["case_0_0", "case_0_1"])
        self.assertTrue(nodes[1].metadata.get("neighbor_context"))
        self.assertEqual(nodes[1].metadata.get("retrieval_rank"), 1)

    def test_selector_keeps_same_source_distinct_chunks(self) -> None:
        graph = EvidenceGraph()
        first = EvidenceNode(
            node_id="chunk_1",
            node_type="text",
            content="table header year value revenue operating income",
            source_doc="report.md",
            modality="text",
        )
        second = EvidenceNode(
            node_id="chunk_2",
            node_type="text",
            content="continuation rows 2018 100 2017 95",
            source_doc="report.md",
            modality="text",
        )
        graph.add_node(first)
        graph.add_node(second)
        scores = {
            "chunk_1": self._score(2.0),
            "chunk_2": self._score(1.9),
        }

        selected = EvidenceSetSelector(max_nodes=2).select("revenue change", graph, scores)

        self.assertEqual([node.node_id for node in selected], ["chunk_1", "chunk_2"])

    def test_selector_keeps_safe_retrieval_rank_one_anchor(self) -> None:
        graph = EvidenceGraph()
        rank_one = EvidenceNode(
            node_id="rank_one",
            node_type="text",
            content="answer-bearing retrieval hit",
            source_doc="report.md",
            modality="text",
            metadata={"retrieval_rank": 1},
        )
        stronger = [
            EvidenceNode(
                node_id=f"stronger_{index}",
                node_type="text",
                content=f"higher scoring distractor {index}",
                source_doc=f"distractor_{index}.md",
                modality="text",
                metadata={"retrieval_rank": index + 2},
            )
            for index in range(4)
        ]
        for node in [rank_one, *stronger]:
            graph.add_node(node)
        scores = {"rank_one": self._score(1.0)}
        scores.update({node.node_id: self._score(2.0 + index) for index, node in enumerate(stronger)})

        selected = EvidenceSetSelector(max_nodes=4).select("what percentage?", graph, scores)

        self.assertEqual(selected[0].node_id, "rank_one")
        self.assertEqual(len(selected), 4)

    def test_selector_uses_neighbor_chunks_only_as_context_expansion(self) -> None:
        graph = EvidenceGraph()
        anchor = EvidenceNode(
            node_id="retrieved_1_case_0_0",
            node_type="text",
            content="answer-bearing retrieval hit",
            source_doc="report.md",
            modality="text",
            metadata={"retrieval_rank": 1},
        )
        neighbor = EvidenceNode(
            node_id="neighbor_1_case_0_1",
            node_type="text",
            content="adjacent context with very high utility",
            source_doc="report.md",
            modality="text",
            metadata={"retrieval_rank": 1, "neighbor_context": True},
        )
        distractor = EvidenceNode(
            node_id="retrieved_2_other_0_0",
            node_type="text",
            content="other selected evidence",
            source_doc="other.md",
            modality="text",
            metadata={"retrieval_rank": 2},
        )
        for node in [neighbor, anchor, distractor]:
            graph.add_node(node)
        scores = {
            neighbor.node_id: self._score(10.0),
            anchor.node_id: self._score(1.0),
            distractor.node_id: self._score(2.0),
        }

        selected = EvidenceSetSelector(max_nodes=2).select("what percentage?", graph, scores)

        self.assertEqual([node.node_id for node in selected], [anchor.node_id, distractor.node_id])
        self.assertEqual(neighbor.metadata.get("selection_status"), "context_expansion")

    def test_selector_does_not_keep_risky_retrieval_rank_one_anchor(self) -> None:
        graph = EvidenceGraph()
        rank_one = EvidenceNode(
            node_id="rank_one_risky",
            node_type="text",
            content="draft forecast",
            source_doc="report.md",
            modality="text",
            metadata={"retrieval_rank": 1},
        )
        safe = EvidenceNode(
            node_id="safe",
            node_type="text",
            content="safe evidence",
            source_doc="report.md",
            modality="text",
            metadata={"retrieval_rank": 2},
        )
        graph.add_node(rank_one)
        graph.add_node(safe)
        scores = {
            "rank_one_risky": self._score(3.0, misleading_risk=0.65),
            "safe": self._score(2.0),
        }

        selected = EvidenceSetSelector(max_nodes=2).select("what percentage?", graph, scores)

        self.assertEqual([node.node_id for node in selected], ["safe"])

    def _score(self, final_score: float, misleading_risk: float = 0.0) -> EvidenceScore:
        return EvidenceScore(
            relevance=1.0,
            utility=1.0,
            grounding=1.0,
            uncertainty=0.0,
            misleading_risk=misleading_risk,
            contradiction_risk=0.0,
            source_reliability=1.0,
            cost=0.0,
            final_score=final_score,
        )


if __name__ == "__main__":
    unittest.main()
