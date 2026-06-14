from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.dataset_adapter import field_map_for_profile
from evigraph.subset_builder import BenchmarkSubsetBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic raw benchmark subset.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--require-source-doc", action="store_true")
    parser.add_argument("--profile", default=None, help="Optional built-in field map profile such as chartqa or stress.")
    parser.add_argument(
        "--field-map",
        default=None,
        help='Optional JSON object such as {"source_doc":"image"}.',
    )
    args = parser.parse_args()

    field_map = field_map_for_profile(args.profile)
    if args.field_map:
        field_map.update(json.loads(args.field_map))
    result = BenchmarkSubsetBuilder().build(
        args.input,
        args.output,
        field_map=field_map or None,
        corpus_path=args.corpus,
        sample_size=args.sample_size,
        seed=args.seed,
        require_source_doc=args.require_source_doc,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
