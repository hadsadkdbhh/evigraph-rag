from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class TatqaQuestion:
    doc_index: int
    question_index: int
    doc_uid: str
    source_doc: str
    qid: str
    query: str
    answer: str
    task_type: str
    record: dict[str, Any]


def build_subset(
    input_path: str | Path,
    raw_output: str | Path,
    corpus_output: str | Path,
    sample_size: int = 20,
    seed: int = 13,
    answer_types: tuple[str, ...] = ("arithmetic",),
) -> dict[str, Any]:
    input_file = Path(input_path)
    raw_output_file = Path(raw_output)
    corpus_output_dir = Path(corpus_output)
    payload = json.loads(input_file.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("TAT-QA input must be a JSON list of document records.")

    candidates: list[TatqaQuestion] = []
    for doc_index, doc in enumerate(payload, start=1):
        doc_uid = str(doc.get("table", {}).get("uid") or f"doc_{doc_index:04d}")
        source_doc = _source_filename(doc_index, doc_uid)
        for question_index, question in enumerate(doc.get("questions", []), start=1):
            if str(question.get("answer_type", "")).lower() not in answer_types:
                continue
            answer = _normalize_answer(question.get("answer"), question.get("scale"))
            if not answer or not _has_number(answer):
                continue
            qid = str(question.get("uid") or f"{doc_uid}_{question_index:03d}")
            candidates.append(
                TatqaQuestion(
                    doc_index=doc_index,
                    question_index=question_index,
                    doc_uid=doc_uid,
                    source_doc=source_doc,
                    qid=qid,
                    query=str(question.get("question", "")).strip(),
                    answer=answer,
                    task_type=f"tatqa_{question.get('answer_type', 'unknown')}_{question.get('answer_from', 'unknown')}",
                    record=doc,
                )
            )

    if sample_size > len(candidates):
        raise ValueError(f"Requested {sample_size} examples, but only {len(candidates)} eligible examples exist.")

    rng = random.Random(seed)
    shuffled = list(candidates)
    rng.shuffle(shuffled)
    selected = sorted(shuffled[:sample_size], key=lambda item: (item.doc_index, item.question_index, item.qid))

    if corpus_output_dir.exists():
        shutil.rmtree(corpus_output_dir)
    corpus_output_dir.mkdir(parents=True, exist_ok=True)
    raw_output_file.parent.mkdir(parents=True, exist_ok=True)

    used_docs: dict[str, TatqaQuestion] = {}
    with raw_output_file.open("w", encoding="utf-8", newline="\n") as handle:
        for item in selected:
            used_docs.setdefault(item.source_doc, item)
            handle.write(
                json.dumps(
                    {
                        "id": item.qid,
                        "query": item.query,
                        "answer": item.answer,
                        "source_doc": item.source_doc,
                        "task_type": item.task_type,
                        "dataset": "tatqa",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    for source_doc, item in sorted(used_docs.items()):
        (corpus_output_dir / source_doc).write_text(_document_markdown(item.record, item.doc_uid), encoding="utf-8")

    return {
        "input": str(input_file),
        "raw_output": str(raw_output_file),
        "corpus_output": str(corpus_output_dir),
        "eligible_questions": len(candidates),
        "sampled_questions": len(selected),
        "corpus_documents": len(used_docs),
        "seed": seed,
        "answer_types": list(answer_types),
    }


def _source_filename(doc_index: int, doc_uid: str) -> str:
    safe_uid = re.sub(r"[^A-Za-z0-9_-]+", "_", doc_uid).strip("_")[:16] or f"doc_{doc_index:04d}"
    return f"tatqa_{doc_index:04d}_{safe_uid}.md"


def _normalize_answer(answer: Any, scale: Any) -> str:
    if isinstance(answer, list):
        if len(answer) != 1:
            return ""
        answer = answer[0]
    text = str(answer).strip()
    if not text:
        return ""
    scale_text = str(scale or "").strip().lower()
    if scale_text == "percent" and "%" not in text:
        return f"{text}%"
    if scale_text:
        return f"{text} {scale_text}"
    return text


def _has_number(text: str) -> bool:
    return bool(re.search(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?", text))


def _document_markdown(doc: dict[str, Any], doc_uid: str) -> str:
    lines = [
        f"# TAT-QA Document {doc_uid}",
        "",
        "## Table",
        "",
        _table_markdown(doc.get("table", {}).get("table", [])),
        "",
        "## Paragraphs",
        "",
    ]
    paragraphs = sorted(doc.get("paragraphs", []), key=lambda item: item.get("order", 0))
    for paragraph in paragraphs:
        text = str(paragraph.get("text", "")).strip()
        if text:
            lines.append(text)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _table_markdown(rows: list[list[Any]]) -> str:
    normalized_rows = [[_cell(cell) for cell in row] for row in rows if row]
    if not normalized_rows:
        return "No table text available."
    width = max(len(row) for row in normalized_rows)
    padded = [row + [""] * (width - len(row)) for row in normalized_rows]
    header = padded[0]
    body = padded[1:] or [[""] * width]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _cell(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).replace("|", "/").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a small reproducible TAT-QA subset for EviGraph manifests.")
    parser.add_argument("--input", required=True, help="Path to tatqa_dataset_dev.json.")
    parser.add_argument("--raw-output", required=True, help="Output questions JSONL path.")
    parser.add_argument("--corpus-output", required=True, help="Output corpus directory.")
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--answer-types", default="arithmetic", help="Comma-separated TAT-QA answer types.")
    args = parser.parse_args()

    answer_types = tuple(part.strip().lower() for part in args.answer_types.split(",") if part.strip())
    result = build_subset(
        args.input,
        args.raw_output,
        args.corpus_output,
        sample_size=args.sample_size,
        seed=args.seed,
        answer_types=answer_types,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
