from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_FIELD_MAP = {
    "id": ["id", "qid", "question_id", "uid"],
    "query": ["query", "question", "prompt", "input"],
    "answer": ["answer", "gold", "gold_answer", "label", "target"],
    "source_doc": ["source_doc", "document", "doc_id", "image", "table_id"],
    "task_type": ["task_type", "type", "category", "dataset"],
}

FIELD_MAP_PROFILES = {
    "chartqa": {
        "id": "id",
        "query": "question",
        "answer": "answer",
        "source_doc": "image",
        "task_type": "type",
    },
    "stress": {
        "id": "qid",
        "query": "question",
        "answer": "gold_answer",
        "source_doc": "document",
        "task_type": "category",
    },
}


def field_map_for_profile(profile: str | None) -> dict[str, str]:
    if not profile:
        return {}
    key = profile.lower()
    if key not in FIELD_MAP_PROFILES:
        raise ValueError(f"Unknown dataset profile: {profile}")
    return dict(FIELD_MAP_PROFILES[key])


class DatasetAdapter:
    def convert(
        self,
        input_path: str | Path,
        output_path: str | Path,
        field_map: dict[str, str] | None = None,
        default_task_type: str | None = None,
        dataset_name: str | None = None,
    ) -> dict[str, Any]:
        input_file = Path(input_path)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        rows = self._read_records(input_file)
        mapping = field_map or {}
        converted = [
            self._convert_record(index, record, mapping, default_task_type, dataset_name)
            for index, record in enumerate(rows, start=1)
        ]
        with output_file.open("w", encoding="utf-8", newline="\n") as handle:
            for record in converted:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {
            "input": str(input_file),
            "output": str(output_file),
            "records": len(converted),
            "dataset": dataset_name,
        }

    def _convert_record(
        self,
        index: int,
        record: dict[str, Any],
        field_map: dict[str, str],
        default_task_type: str | None,
        dataset_name: str | None,
    ) -> dict[str, Any]:
        query = self._value(record, "query", field_map)
        answer = self._value(record, "answer", field_map)
        if query is None:
            raise ValueError(f"Record {index} has no query/question field.")
        if answer is None:
            raise ValueError(f"Record {index} has no answer/gold field.")

        sample = {
            "id": str(self._value(record, "id", field_map) or f"sample_{index:06d}"),
            "query": str(query),
            "answer": self._stringify(answer),
        }
        source_doc = self._value(record, "source_doc", field_map)
        task_type = self._value(record, "task_type", field_map) or default_task_type
        if source_doc is not None:
            sample["source_doc"] = str(source_doc)
        if task_type is not None:
            sample["task_type"] = str(task_type)
        if dataset_name:
            sample["dataset"] = dataset_name
        return sample

    def _value(self, record: dict[str, Any], target: str, field_map: dict[str, str]) -> Any:
        explicit_field = field_map.get(target)
        if explicit_field:
            return record.get(explicit_field)
        for candidate in DEFAULT_FIELD_MAP[target]:
            if candidate in record:
                return record[candidate]
        return None

    def _stringify(self, value: Any) -> str:
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _read_records(self, path: Path) -> list[dict[str, Any]]:
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                for key in ("data", "examples", "samples", "questions"):
                    if isinstance(payload.get(key), list):
                        return payload[key]
            raise ValueError(f"Unsupported JSON dataset shape: {path}")
        if suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                return list(csv.DictReader(handle))
        raise ValueError(f"Unsupported dataset format: {path.suffix}. Use .jsonl, .json, or .csv.")
