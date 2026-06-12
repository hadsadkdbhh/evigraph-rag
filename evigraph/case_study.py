from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CaseStudyExporter:
    def export(self, run_dir: str | Path, output_path: str | Path | None = None) -> str:
        run_path = Path(run_dir)
        if not run_path.exists():
            raise FileNotFoundError(f"Run directory does not exist: {run_path}")

        trace = self._read_trace(run_path / "trace.jsonl")
        graph = self._read_json(run_path / "graph.json")
        support_graph = self._read_json(run_path / "support_graph.json")
        cost = self._read_json(run_path / "cost.json")
        answer_md = (run_path / "answer.md").read_text(encoding="utf-8") if (run_path / "answer.md").exists() else ""

        markdown = self._render(run_path, trace, graph, support_graph, cost, answer_md)
        output = Path(output_path) if output_path else run_path / "case_study.md"
        output.write_text(markdown, encoding="utf-8")
        return str(output)

    def _render(
        self,
        run_path: Path,
        trace: list[dict[str, Any]],
        graph: dict[str, Any],
        support_graph: dict[str, Any],
        cost: dict[str, Any],
        answer_md: str,
    ) -> str:
        actions = cost.get("actions", [])
        selected_ids = self._trace_payload(trace, "select").get("selected_ids", [])
        scores = self._trace_payload(trace, "score").get("scores", {})
        verification = self._trace_payload(trace, "verify")
        support_nodes = {node["node_id"]: node for node in support_graph.get("nodes", [])}

        lines = [
            "# EviGraph Case Study",
            "",
            f"- Run: `{run_path}`",
            f"- Action trace: `{self._action_trace(actions)}`",
            f"- Selected evidence: {', '.join(f'`{node_id}`' for node_id in selected_ids) if selected_ids else 'n/a'}",
            f"- Cost: tokens={cost.get('selected_tokens', 0)}, tool_calls={cost.get('tool_calls', 0)}, latency_ms={cost.get('latency_ms', 0)}",
            "",
            "## Answer",
            "",
            self._answer_body(answer_md),
            "",
            "## Evidence Selection",
            "",
            self._selection_table(selected_ids, scores, support_nodes),
            "",
            "## Actions",
            "",
            self._actions_table(actions),
            "",
            "## Verification",
            "",
            "```json",
            json.dumps(verification, ensure_ascii=False, indent=2),
            "```",
            "",
            "## Support Graph",
            "",
            f"- Nodes: {len(support_graph.get('nodes', []))}",
            f"- Edges: {len(support_graph.get('edges', []))}",
            "",
            "## Full Candidate Graph",
            "",
            f"- Nodes: {len(graph.get('nodes', []))}",
            f"- Edges: {len(graph.get('edges', []))}",
            "",
        ]
        return "\n".join(lines)

    def _selection_table(
        self,
        selected_ids: list[str],
        scores: dict[str, dict[str, Any]],
        support_nodes: dict[str, dict[str, Any]],
    ) -> str:
        if not selected_ids:
            return "No selected evidence recorded."
        rows = ["| evidence | type | utility | grounding | risk | final | summary |", "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
        for node_id in selected_ids:
            node = support_nodes.get(node_id, {})
            score = scores.get(node_id, node.get("scores", {}))
            risk = max(float(score.get("misleading_risk", 0.0)), float(score.get("contradiction_risk", 0.0)))
            rows.append(
                "| "
                + " | ".join(
                    [
                        f"`{node_id}`",
                        str(node.get("node_type", "n/a")),
                        f"{float(score.get('utility', 0.0)):.2f}",
                        f"{float(score.get('grounding', 0.0)):.2f}",
                        f"{risk:.2f}",
                        f"{float(score.get('final_score', 0.0)):.2f}",
                        self._summary(node.get("content", "")),
                    ]
                )
                + " |"
            )
        return "\n".join(rows)

    def _actions_table(self, actions: list[dict[str, Any]]) -> str:
        if not actions:
            return "No actions recorded."
        rows = ["| step | action | targets | reason |", "| ---: | --- | --- | --- |"]
        for index, action in enumerate(actions, start=1):
            rows.append(
                f"| {index} | `{action.get('action_type')}` | "
                f"{', '.join(f'`{target}`' for target in action.get('target_node_ids', [])) or '-'} | "
                f"{action.get('reason', '')} |"
            )
        return "\n".join(rows)

    def _action_trace(self, actions: list[dict[str, Any]]) -> str:
        return " -> ".join(action.get("action_type", "?") for action in actions) or "n/a"

    def _trace_payload(self, trace: list[dict[str, Any]], step: str) -> dict[str, Any]:
        for record in reversed(trace):
            if record.get("step") == step:
                return record
        return {}

    def _read_trace(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _summary(self, content: Any) -> str:
        if isinstance(content, dict):
            text = json.dumps(content, ensure_ascii=False)
        else:
            text = str(content)
        text = text.replace("\n", " ").replace("|", "\\|")
        return text[:140] + ("..." if len(text) > 140 else "")

    def _answer_body(self, answer_md: str) -> str:
        lines = answer_md.strip().splitlines()
        if lines and lines[0].strip() == "# Answer":
            lines = lines[1:]
        body = "\n".join(lines).strip()
        return body or "No answer.md found."
