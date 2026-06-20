from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.row_operation_diagnostics import RowOperationDiagnosticAnalyzer


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose wrong numeric operation/row failures in an experiment CSV.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--method", default="full_evigraph")
    parser.add_argument("--output", default=None)
    parser.add_argument("--json-output", default=None)
    args = parser.parse_args()

    analyzer = RowOperationDiagnosticAnalyzer()
    analysis = analyzer.analyze(args.csv, method=args.method)
    if args.output:
        analyzer.write(args.csv, args.output, method=args.method, json_output_path=args.json_output)
    elif args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
