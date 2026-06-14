from __future__ import annotations

import argparse
import json
import random
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DATASET = "dreamerdeo/finqa"
CONFIG = "default"
API_BASE = "https://datasets-server.huggingface.co"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download a deterministic FinQA subset from Hugging Face.")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--pool-size", type=int, default=100)
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--raw-output", default="data/raw/finqa_subset.jsonl")
    parser.add_argument("--corpus-output", default="data/finqa_corpus")
    args = parser.parse_args()

    rows = fetch_rows(args.split, args.pool_size)
    if len(rows) < args.sample_size:
        raise ValueError(f"Requested {args.sample_size} samples but only fetched {len(rows)} rows.")

    sampled = list(rows)
    random.Random(args.seed).shuffle(sampled)
    sampled = sampled[: args.sample_size]

    raw_path = ROOT / args.raw_output
    corpus_path = ROOT / args.corpus_output
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.mkdir(parents=True, exist_ok=True)

    raw_records = []
    for index, payload in enumerate(sampled, start=1):
        record = payload["row"]
        source_doc = f"finqa_{index:03d}_{slugify(record['id'])}.md"
        write_corpus_file(corpus_path / source_doc, record, args.split)
        raw_records.append(
            {
                "id": str(record["id"]),
                "question": str(record["question"]),
                "answer": normalize_answer(record.get("answer")),
                "source_doc": source_doc,
                "task_type": "finqa_validation",
                "dataset": DATASET,
                "split": args.split,
                "row_idx": payload.get("row_idx"),
                "gold_evidence": record.get("gold_evidence", []),
            }
        )

    with raw_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in raw_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "dataset": DATASET,
                "config": CONFIG,
                "split": args.split,
                "pool_size": args.pool_size,
                "sample_size": args.sample_size,
                "seed": args.seed,
                "raw_output": str(raw_path),
                "corpus_output": str(corpus_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def fetch_rows(split: str, length: int) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "dataset": DATASET,
            "config": CONFIG,
            "split": split,
            "offset": 0,
            "length": length,
        }
    )
    url = f"{API_BASE}/rows?{query}"
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return list(payload["rows"])


def write_corpus_file(path: Path, record: dict[str, Any], split: str) -> None:
    lines = [
        f"# FinQA Evidence {record['id']}",
        "",
        f"- Source dataset: {DATASET}",
        f"- Split: {split}",
        "",
        "## Pre Text",
        "",
        *as_lines(record.get("pre_text")),
        "",
        "## Table",
        "",
        render_table(record.get("table")),
        "",
        "## Post Text",
        "",
        *as_lines(record.get("post_text")),
        "",
    ]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render_table(table: Any) -> str:
    if not isinstance(table, list) or not table:
        return ""
    rows = [[str(cell) for cell in row] for row in table if isinstance(row, list)]
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    padded = [row + [""] * (width - len(row)) for row in rows]
    header = padded[0]
    body = padded[1:]
    lines = [
        "| " + " | ".join(escape_cell(cell) for cell in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines.extend("| " + " | ".join(escape_cell(cell) for cell in row) + " |" for row in body)
    return "\n".join(lines)


def as_lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def normalize_answer(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value)


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug[:80] or "sample"


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
