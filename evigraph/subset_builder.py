from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from evigraph.dataset_adapter import DatasetAdapter
from evigraph.dataset_inspector import DatasetInspector


class BenchmarkSubsetBuilder:
    def build(
        self,
        input_path: str | Path,
        output_path: str | Path,
        field_map: dict[str, str] | None = None,
        corpus_path: str | Path | None = None,
        sample_size: int | None = None,
        seed: int = 13,
        require_source_doc: bool = True,
    ) -> dict[str, Any]:
        input_file = Path(input_path)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        adapter = DatasetAdapter()
        inspector = DatasetInspector()
        records = adapter._read_records(input_file)
        field_map = field_map or {}
        corpus_sources = inspector._corpus_sources(Path(corpus_path) if corpus_path else None)

        eligible = []
        skipped_missing_source = 0
        skipped_unmatched_source = 0
        for record in records:
            source_doc = self._source_doc(record, field_map)
            if require_source_doc and not source_doc:
                skipped_missing_source += 1
                continue
            if require_source_doc and not inspector._source_matches(str(source_doc), corpus_sources):
                skipped_unmatched_source += 1
                continue
            eligible.append(record)

        sampled = list(eligible)
        random.Random(seed).shuffle(sampled)
        if sample_size is not None:
            sampled = sampled[:sample_size]

        with output_file.open("w", encoding="utf-8", newline="\n") as handle:
            for record in sampled:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        return {
            "input": str(input_file),
            "output": str(output_file),
            "total_records": len(records),
            "eligible_records": len(eligible),
            "sampled_records": len(sampled),
            "sample_size": sample_size,
            "seed": seed,
            "require_source_doc": require_source_doc,
            "skipped_missing_source_doc": skipped_missing_source,
            "skipped_unmatched_source_doc": skipped_unmatched_source,
        }

    def _source_doc(self, record: dict[str, Any], field_map: dict[str, str]) -> Any:
        return DatasetAdapter()._value(record, "source_doc", field_map)
