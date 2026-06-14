# Benchmark Protocol

This protocol defines how real benchmark subsets should enter the EviGraph
pipeline. It is intentionally strict: no benchmark result should be reported
unless it can be reproduced through a manifest in `configs/`.

## Required Inputs

Each benchmark subset should provide:

- A raw annotation file in `.jsonl`, `.json`, or `.csv`.
- A corpus directory containing the evidence available to retrieval.
- A manifest that records field mapping, corpus path, methods, budgets, and limitations.
- A generated experiment card from `scripts/run_manifest.py`.

## Internal Question Schema

Every raw example is converted to JSONL with these fields:

```json
{
  "id": "unique_example_id",
  "query": "question text",
  "answer": "gold answer",
  "source_doc": "optional evidence/document id",
  "task_type": "optional task category",
  "dataset": "benchmark name"
}
```

## Reporting Rules

- Report toy and synthetic stress results only as pipeline checks.
- Report public benchmark numbers only after the raw subset and manifest are documented.
- Keep synthetic distractors separate from benchmark corpora.
- Record all generated CSV summaries and experiment cards, but do not commit `outputs/`.
- When using a subset, report the subset size, filtering rules, and random seed or deterministic selection rule.

## Minimum Real-Benchmark Gate

Before a result is used in the paper, it should pass:

```powershell
python scripts/run_tests.py
python scripts/run_feasibility.py --corpus data/corpus --report outputs/eval/feasibility_report.json
python scripts/run_manifest.py --manifest configs/<benchmark>.json
```

The resulting `experiment_card.md` must include the benchmark limitations and
the exact manifest path.
