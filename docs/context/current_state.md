# EviGraph-RAG Working Context

Last updated: 2026-06-24

This file is the durable context checkpoint for Codex. Read it before continuing
project work after chat compaction or a new session. Keep it short, factual,
and tied to checked artifacts or documented runs.

## Current Project Goal

Build EviGraph-RAG into a credible AAAI submission candidate. The near-term
engineering goal is to improve real FinQA numerical reasoning and open
retrieval performance without inflating claims beyond the evidence.

## Current Baseline

Use the 300-example FinQA validation subset as the current reality check.

- Dataset: `data/raw/finqa_300_subset.jsonl`
- Corpus: `data/finqa_300_corpus`
- Index: `outputs/index/finqa_300_subset.json`
- Local planner manifest: `configs/experiments.finqa_300.local_planner.json`
- Main results: `outputs/eval/finqa_300_local_planner/summary.md`
- One-command pipeline report: `outputs/pipeline/pipeline_report.md`
- Paper table artifacts: `paper/generated/finqa_300_local_planner/`
- Main diagnostics:
  - `outputs/eval/finqa_300_local_planner/finqa_300_subset_source_rerank_full_local_planner_failures.md`
  - `outputs/eval/finqa_300_local_planner/finqa_300_subset_source_rerank_full_local_planner_row_operation_diagnostics.md`

Latest documented FinQA-300 local planner exact match:

| Setting | Accuracy |
| --- | ---: |
| Oracle-doc full EviGraph | 0.367 |
| Open BM25 full EviGraph | 0.280 |
| BM25 + source-rerank full EviGraph | 0.340 |

Latest source-rerank diagnostic counts:

| Failure class | Count |
| --- | ---: |
| wrong_numeric_operation_or_row | 62 |
| no_numeric_answer_other | 38 |
| no_numeric_answer_percent | 37 |
| no_numeric_answer_additive_or_lookup | 32 |
| no_numeric_answer_ratio | 17 |
| unsupported_textual_prediction | 11 |

Latest row/operation diagnostic split for source-rerank:

| Label | Count |
| --- | ---: |
| ambiguous_supported_wrong_number | 31 |
| wrong_operation_type | 14 |
| wrong_row_label | 10 |
| wrong_year_or_period | 8 |
| wrong_denominator | 6 |
| wrong_numerator | 5 |

## Pipeline Closure

As of 2026-06-24, the FinQA-300 local-planner pipeline has a single entrypoint:

```powershell
python .\scripts\run_pipeline.py
```

This quick path runs all unit tests and rebuilds paper assets from the latest
checked evaluation outputs. To refresh the 300-example manifest first, run:

```powershell
python .\scripts\run_pipeline.py --refresh-results
```

The latest full refresh passed:

- Unit tests: `175 tests OK`
- Manifest: `configs/experiments.finqa_300.local_planner.json`
- Result directory: `outputs/eval/finqa_300_local_planner`
- Pipeline report: `outputs/pipeline/pipeline_report.md`
- Full-refresh report: `outputs/pipeline/pipeline_report_full_refresh.md`
- Quick report: `outputs/pipeline/pipeline_report_quick.md`
- Paper summary: `paper/generated/finqa_300_local_planner/finqa_results_summary.md`
- LaTeX tables: `paper/generated/finqa_300_local_planner/finqa_results_tables.tex`

Use `scripts/run_pipeline.py --refresh-results` as the default reproducibility
gate before reporting new FinQA-300 numbers.

## What Has Already Been Tried

- FinQA-300 subset expansion with fixed seed and source-document metadata.
- Local program planner path to avoid API quota dependency.
- Row/column selection, ratio, ratio percent, difference, sum, average,
  product, percent change, percent-of-increase, same-row due-after ratio,
  complement percent, and waterfall contribution handling.
- Period disambiguation for repeated year columns.
- Adjacent chunk expansion for truncated ratio evidence.
- Failure-driven row/operation diagnostics.
- Several narrow semantic repairs for percent-change direction, respectively
  prose evidence, cash-paid acquisition ratios, compact year ranges, and
  interest-income decrease phrasing.
- Token-bound row matching in `TableOperationExecutor.select_best_row`, which
  prevents `tangible` from matching inside `intangible` while preserving basic
  plural matches such as `liability`/`liabilities`. This fixed the GPN net
  tangible assets lookup in oracle-doc and source-rerank.
- Entity-to-entity absolute difference planning for questions shaped like
  `difference in METRIC between ENTITY_A and ENTITY_B`. This fixed the ETR
  payments example by computing `abs(2 - 6) = 4` instead of subtracting the
  same row from itself, and moved open BM25 to 0.273.
- Year-anchored row selection and total-column exclusion inside
  `NumericReasoner._row_values_average`. `_keywords` strips 20XX tokens, so
  two rows differing only by year (for example `liability at december 31 2006`
  vs `... 2008`) used to tie and the earlier row won. When the query pins a
  year, the row whose label carries that year is now preferred, and a `total`
  summary column is excluded from the average. This fixed the IPG 2008
  restructuring-liability average (`(1.2 + 5.7 + 5.9) / 3 = 4.3` instead of
  `519.4`), moving FinQA-300 to 0.363 oracle-doc, 0.277 open BM25, and 0.337
  source-rerank.
- Period-end row preference for change queries inside
  `NumericReasoner._change_period_preference`, gated on non-zero lexical
  coverage in `_best_query_row`. A change query (`change`/`increased`/
  `decreased`/`growth`) over a table that carries both a period-beginning and a
  period-end row for the same metric used to tie on score and the earlier
  (beginning) row won. The period-end row (`at december 31`, `ending balance`)
  is now preferred and the period-beginning row penalized, but only as a
  tiebreaker between rows that already lexically match the query. The coverage
  gate matters: without it the preference promoted an unrelated row (for example
  `net mw in operation` for an earnings query) and forced the planner away from
  the correct prose answer. This fixed the JPM 2007 MSR fair-value change
  (`(8632 - 7546) / 7546 = 14.4%` instead of `12.9%`) and the APD 2018
  operating-expenses change, moving FinQA-300 to 0.367 oracle-doc, 0.280 open
  BM25, and 0.340 source-rerank.

Do not repeat these as broad rewrites. Build only from failure reports and add
small verified fixes.

## Current Engineering Rule

Do not blindly add generic numeric rules. For each change:

1. Pick one failure cluster from the diagnostic reports.
2. Inspect concrete examples first.
3. Add the smallest planner/executor/diagnostic change that explains the
   cluster.
4. Add or update focused tests.
5. Rerun the relevant unit tests.
6. Rerun the FinQA-300 local planner manifest when the change is measurable.
7. Update this file only after a real result changes.

## Highest-Yield Next Work

Priority order:

1. `ambiguous_supported_wrong_number`: operand selection inside supported
   ratio and percent-change evidence, especially wrong denominator, wrong row
   label, and wrong year/period cases.
2. `no_numeric_answer_percent`: percent operations that currently fall back to
   textual answers, but only after inspecting examples.
3. Open retrieval quality: improve source-rerank and open BM25 evidence
   selection after numeric executor gains stop moving oracle-doc.

Avoid spending quota on LLM planner runs until the local program planner and
failure diagnostics stop yielding obvious gains.

## Standard Commands

Run all tests:

```powershell
python -m unittest discover -s tests
```

Run FinQA-300 local planner:

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.local_planner.json
```

Inspect latest source-rerank failure report:

```powershell
Get-Content .\outputs\eval\finqa_300_local_planner\finqa_300_subset_source_rerank_full_local_planner_failures.md -Head 160
```

Inspect latest row/operation diagnostic:

```powershell
Get-Content .\outputs\eval\finqa_300_local_planner\finqa_300_subset_source_rerank_full_local_planner_row_operation_diagnostics.md -Head 180
```

## Paper Claim Boundary

Current results support an engineering-progress and diagnostic story, not a
strong benchmark superiority claim. Before AAAI submission, still needed:

- Stronger baselines, especially dense retrieval and retrieve-then-read RAG.
- Larger benchmark runs beyond the 300-example diagnostic subset.
- Cleaner failure analysis and qualitative case studies.
- Better open-retrieval performance.
- Careful separation of oracle-doc, open BM25, open hybrid, and source-rerank
  results in tables and prose.

## Git Note

The attempted Headroom project integration was reverted on 2026-06-22. Do not
re-add it to the EviGraph codebase unless explicitly requested as project code.
Headroom cannot be installed into Codex's internal context manager from this
repo; use this checkpoint file instead.
