from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.dataset_inspector import DatasetInspector


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect converted EviGraph question JSONL before benchmark runs.")
    parser.add_argument("--questions", required=True)
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--json-output", default=None)
    parser.add_argument("--md-output", default=None)
    args = parser.parse_args()

    inspector = DatasetInspector()
    report = inspector.inspect(args.questions, args.corpus, args.json_output)
    if args.md_output:
        inspector.write_markdown(report, args.md_output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
