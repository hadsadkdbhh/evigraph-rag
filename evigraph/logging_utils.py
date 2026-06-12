from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Action, Answer, EvidenceNode


class RunLogger:
    def __init__(self, output_dir: str = "outputs/runs") -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = Path(output_dir) / timestamp
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.run_dir / "trace.jsonl"

    def trace(self, step: str, payload: dict[str, Any]) -> None:
        record = {"step": step, **payload}
        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def save(
        self,
        query: str,
        graph: EvidenceGraph,
        support_graph: EvidenceGraph,
        selected: list[EvidenceNode],
        actions: list[Action],
        answer: Answer,
        verification: dict[str, Any],
    ) -> dict[str, str]:
        self._write_json("graph.json", graph.to_dict())
        self._write_json("support_graph.json", support_graph.to_dict())
        self._write_json(
            "cost.json",
            {
                "selected_tokens": sum(float(node.cost.get("tokens", 0)) for node in selected),
                "tool_calls": sum(float(node.cost.get("tool_calls", 0)) for node in selected)
                + sum(float(action.estimated_cost.get("tool_calls", 0)) for action in actions),
                "actions": [action.to_dict() for action in actions],
            },
        )
        answer_md = [
            f"# Answer\n\n{answer.text}\n",
            "## Citations\n",
            *[f"- `{citation}`\n" for citation in answer.citations],
            "\n## Calculations\n",
            *[f"- {calculation}\n" for calculation in answer.calculations],
            "\n## Verification\n",
            f"```json\n{json.dumps(verification, ensure_ascii=False, indent=2)}\n```\n",
            "\n## Query\n",
            query,
            "\n",
        ]
        (self.run_dir / "answer.md").write_text("".join(answer_md), encoding="utf-8")
        return {
            "run_dir": str(self.run_dir),
            "trace": str(self.trace_path),
            "answer": str(self.run_dir / "answer.md"),
        }

    def _write_json(self, name: str, payload: dict[str, Any]) -> None:
        (self.run_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
