from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.dataset_inspector import BenchmarkGate, DatasetInspector


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect converted EviGraph question JSONL before benchmark runs.")
    parser.add_argument("--questions", required=True)
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--json-output", default=None)
    parser.add_argument("--md-output", default=None)
    parser.add_argument("--gate-output", default=None)
    parser.add_argument("--min-records", type=int, default=1)
    parser.add_argument("--min-source-doc-coverage", type=float, default=1.0)
    parser.add_argument("--allow-missing-source-doc", action="store_true")
    parser.add_argument("--fail-on-gate", action="store_true")
    args = parser.parse_args()

    inspector = DatasetInspector()
    report = inspector.inspect(args.questions, args.corpus, args.json_output)
    if args.md_output:
        inspector.write_markdown(report, args.md_output)
    gate = BenchmarkGate().evaluate(
        report,
        min_records=args.min_records,
        min_source_doc_coverage=args.min_source_doc_coverage,
        allow_missing_source_doc=args.allow_missing_source_doc,
    )
    if args.gate_output:
        gate_output = Path(args.gate_output)
        gate_output.parent.mkdir(parents=True, exist_ok=True)
        gate_output.write_text(BenchmarkGate().render_markdown(gate), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_gate and not gate["passed"]:
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
