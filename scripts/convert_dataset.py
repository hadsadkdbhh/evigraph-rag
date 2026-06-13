from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.dataset_adapter import DatasetAdapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert external benchmark records to EviGraph questions.jsonl.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-name", default=None)
    parser.add_argument("--default-task-type", default=None)
    parser.add_argument(
        "--field-map",
        default=None,
        help='Optional JSON object such as {"query":"question","answer":"gold_answer"}.',
    )
    args = parser.parse_args()

    field_map = json.loads(args.field_map) if args.field_map else None
    result = DatasetAdapter().convert(
        args.input,
        args.output,
        field_map=field_map,
        default_task_type=args.default_task_type,
        dataset_name=args.dataset_name,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
