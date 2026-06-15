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

    def test_ratio_percent_represented_by_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| current assets | $ 28.1 |\n"
                    "| --- | --- |\n"
                    "| ipr&d | 190.0 |\n"
                    "| total cash purchase price net of cash acquired | $ 320.1 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of the total cash purchase price net of cash acquired was represented by ipr&d?",
            graph,
        )

        self.assertEqual(answer.text, "59.4%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_allocated_to_year_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2011 | 2010 |\n"
                    "| --- | --- | --- |\n"
                    "| money market funds | $ 17187 | $ 1840 |\n"
                    "| mutual funds | 9223 | 6850 |\n"
                    "| total deferred compensation plan investments | $ 26410 | $ 8690 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what portion of the total investment is allocated to mutual funds in 2011?",
            graph,
        )

        self.assertEqual(answer.text, "34.9%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_due_after_total(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | ( in thousands ) |\n"
                    "| --- | --- |\n"
                    "| 2010 | $ 6951 |\n"
                    "| thereafter | 25048 |\n"
                    "| total | $ 44572 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of total purchase commitments are due after 2014?",
            graph,
        )

        self.assertEqual(answer.text, "56.2%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_due_to_row_for_year(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| in millions | 2008 | 2009 | thereafter |\n"
                    "| --- | --- | --- | --- |\n"
                    "| lease obligations | $ 136 | $ 116 | $ 92 |\n"
                    "| purchase obligations ( a ) | 1953 | 294 | 1480 |\n"
                    "| total | $ 2089 | $ 410 | $ 1572 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of december 31 , 2007 , total future minimum commitments under existing non-cancelable operating leases and purchase obligations were due to purchase obligations for the year of 2008?",
            graph,
        )

        self.assertEqual(answer.text, "93.5%")
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

    def test_change_from_year_columns(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2013 | 2012 | 2011 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| weighted average common shares outstanding for basic computations | 320.9 | 323.7 | 335.9 |\n"
                    "| weighted average common shares outstanding for diluted computations | 326.5 | 328.4 | 339.9 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the change in the weighted average common shares outstanding for diluted computations from 2012 to 2013 , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "-1.9")
        self.assertIn("row_year_difference", answer.calculations[0])

    def test_average_amount_uses_selected_row_values(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| december 31, | 2016 | 2015 | 2014 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| balance at january 1 | $ 373 | $ 394 | $ 392 |\n"
                    "| settlements | -13 ( 13 ) | -19 ( 19 ) | -2 ( 2 ) |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "for the period ending in 2016 , what was the average amount of settlements , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "11.3")
        self.assertIn("row_values_average", answer.calculations[0])

    def test_repeated_increase_projection(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( in millions ) | 2007 | 2006 | 2005 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| development costs incurred during the period | 1654 | 1251 | 1030 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "if current development costs increased in 2008 as much as in 2007 , what would the 2008 total be , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "2057")
        self.assertIn("repeated_increase_projection", answer.calculations[0])

    def test_pretax_aftertax_difference(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "these unrealized losses related to reclassifications totaled $ 303 million , "
                    "or $ 189 million after-tax , as of december 31 , 2011."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2011 what was the amount of tax related to the unrealized losses reclassifications totaled $ 303 million , or $ 189 million after-tax,",
            graph,
        )

        self.assertEqual(answer.text, "114")
        self.assertIn("pretax_aftertax_difference", answer.calculations[0])

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
