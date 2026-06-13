from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.manifest import ManifestRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an experiment manifest end to end.")
    parser.add_argument("--manifest", default=str(ROOT / "configs" / "experiments.mock.json"))
    args = parser.parse_args()

    artifacts = ManifestRunner(args.manifest).run()
    print(json.dumps(artifacts, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
