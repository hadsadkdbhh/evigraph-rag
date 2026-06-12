from __future__ import annotations

from evigraph.schema import EvidenceNode


class MockRetriever:
    """Deterministic candidates for MVP-0 smoke tests."""

    def retrieve(self, query: str, corpus_path: str | None = None, top_k: int = 8) -> list[EvidenceNode]:
        query_lower = query.lower()
        nodes = [
            EvidenceNode(
                node_id="chart_2022_2023",
                node_type="chart",
                content={
                    "title": "Revenue by year",
                    "values": {"2022": 87.5, "2023": 100.0},
                    "caption": "Annual revenue increased from 2022 to 2023.",
                },
                source_doc="mock_report.pdf",
                page_number=4,
                bbox=[120, 180, 520, 420],
                modality="chart",
                cost={"tokens": 60, "tool_calls": 1, "latency_ms": 200},
            ),
            EvidenceNode(
                node_id="text_summary",
                node_type="text",
                content="The report states that 2023 revenue was higher than 2022.",
                source_doc="mock_report.pdf",
                page_number=4,
                modality="text",
                cost={"tokens": 18, "tool_calls": 0, "latency_ms": 20},
            ),
            EvidenceNode(
                node_id="table_revenue",
                node_type="table",
                content={
                    "columns": ["year", "revenue"],
                    "rows": [["2022", "87.5"], ["2023", "100.0"]],
                },
                source_doc="mock_report.pdf",
                page_number=5,
                modality="table",
                cost={"tokens": 44, "tool_calls": 1, "latency_ms": 150},
            ),
            EvidenceNode(
                node_id="misleading_old_forecast",
                node_type="text",
                content="A preliminary forecast expected 2023 revenue to be 91.0.",
                source_doc="mock_draft.pdf",
                page_number=2,
                modality="text",
                confidence=0.55,
                cost={"tokens": 16, "tool_calls": 0, "latency_ms": 20},
                metadata={"is_misleading": True, "source_quality": "draft"},
            ),
            EvidenceNode(
                node_id="irrelevant_margin",
                node_type="text",
                content="Operating margin changed because of procurement expenses.",
                source_doc="mock_report.pdf",
                page_number=7,
                modality="text",
                cost={"tokens": 12, "tool_calls": 0, "latency_ms": 20},
            ),
            EvidenceNode(
                node_id="conflicting_press",
                node_type="text",
                content="A press excerpt claims 2023 revenue was only 95.0.",
                source_doc="mock_press_clip.txt",
                modality="text",
                confidence=0.6,
                cost={"tokens": 14, "tool_calls": 0, "latency_ms": 20},
                metadata={"is_conflicting": True, "source_quality": "third_party"},
            ),
        ]

        if "chart" not in query_lower and "higher" not in query_lower:
            nodes = list(reversed(nodes))
        return nodes[:top_k]
