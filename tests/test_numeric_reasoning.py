from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evigraph.evidence_graph import EvidenceGraph
from evigraph.generator import SupportOnlyGenerator
from evigraph.metrics import numeric_exact_match
from evigraph.retrieval import CorpusRetriever
from evigraph.schema import EvidenceNode


class NumericReasoningTest(unittest.TestCase):
    def test_percent_change_from_year_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | amount ( in thousands ) |\n"
                    "| --- | --- |\n"
                    "| 2016 | $ 204079 |\n"
                    "| 2017 | $ 766451 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percent change in annual long-term debt maturities from 2016 to 2017?",
            graph,
        )

        self.assertEqual(answer.text, "275.6%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_ratio_percent_from_table_and_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="evidence",
                node_type="text",
                content=(
                    "foodservice net sales declined to $ 396 million in 2006.\n"
                    "|  | 2006 | 2005 |\n"
                    "| --- | --- | --- |\n"
                    "| sales | $ 2455 | $ 2245 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2006 what percentage of consumer packaging sales were represented by foodservice net sales?",
            graph,
        )

        self.assertEqual(answer.text, "16.1%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_row_average_from_entity_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| company | payments volume ( billions ) | total transactions ( billions ) |\n"
                    "| --- | --- | --- |\n"
                    "| american express | 637 | 5.0 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average payment volume per transaction for american express?",
            graph,
        )

        self.assertEqual(answer.text, "127.40")
        self.assertIn("row_average", answer.calculations[0])

    def test_year_range_average_from_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year | amortization amount ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| 2015 | $ 45 |\n"
                    "| 2016 | $ 45 |\n"
                    "| 2017 | $ 45 |\n"
                    "| 2018 | $ 45 |\n"
                    "| 2019 | $ 44 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average amortization amount , in millions , from 2015-2019?",
            graph,
        )

        self.assertEqual(answer.text, "44.8")
        self.assertIn("year_range_average", answer.calculations[0])

    def test_percentage_exact_match_allows_rounding(self) -> None:
        self.assertEqual(numeric_exact_match("86.8%", "87%"), 1.0)

    def test_source_doc_retrieval_adds_oracle_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "a.md").write_text("alpha table 2016 10\nmore alpha 2017 20", encoding="utf-8")
            (corpus / "b.md").write_text("beta unrelated 2016 100\nbeta unrelated 2017 200", encoding="utf-8")

            nodes = CorpusRetriever().retrieve("alpha 2017", corpus, source_doc="a.md")

        self.assertTrue(nodes)
        self.assertTrue(any(node.metadata.get("loader") == "source_doc_oracle" for node in nodes))
        self.assertTrue(all(Path(str(node.source_doc)).name == "a.md" for node in nodes))


if __name__ == "__main__":
    unittest.main()
