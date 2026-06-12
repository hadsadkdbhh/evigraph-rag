from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.indexing import LocalIndexBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local JSON index for MVP-1 retrieval.")
    parser.add_argument("--corpus", default=str(ROOT / "data" / "corpus"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "index" / "index.json"))
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    args = parser.parse_args()

    result = LocalIndexBuilder(args.chunk_size, args.chunk_overlap).build(args.corpus, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
