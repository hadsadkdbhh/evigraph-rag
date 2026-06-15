from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.methods import METHODS, MethodRunner


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        return {}
    text = config_path.read_text(encoding="utf-8")
    if config_path.suffix.lower() == ".json":
        return json.loads(text)
    return parse_simple_yaml(text)


def parse_simple_yaml(text: str) -> dict[str, Any]:
    config: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.strip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            key = line[:-1].strip()
            config[key] = {}
            current = config[key]
            continue
        if current is not None and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key.strip()] = parse_scalar(value.strip())
    return config


def parse_scalar(value: str) -> Any:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EviGraph-RAG MVP-0 on one query.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    parser.add_argument("--method", default="full_evigraph", choices=METHODS)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--source-doc", default=None)
    parser.add_argument("--retrieval-mode", default="oracle_doc", choices=["oracle_doc", "open", "source_rerank"])
    args = parser.parse_args()

    config = load_config(args.config)
    result = MethodRunner(config).run(
        args.query,
        args.method,
        corpus_path=args.corpus,
        source_doc=args.source_doc,
        retrieval_mode=args.retrieval_mode,
        top_k=args.top_k,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
