# Submission Experiment Closure

This file defines what "experiment closed" means for the EviGraph-RAG submission package.
It is intentionally stricter than "we ran many experiments".

## Current Closure Status

Overall: closed for the current deterministic local-planner submission package.

The closure check now passes after the final FinQA-600 component closure and the
TAT-QA-100 method-ordering closure:

- FinQA-600 v48 component closure is complete across oracle-doc, open BM25,
  and source-rerank.
- TAT-QA-100 v50 method closure is complete across oracle-doc and open BM25.
- `scripts/check_experiment_closure.py` reports PASS.

## Closed Claims

| Claim | Artifact | Status |
| --- | --- | --- |
| FinQA-600 oracle/source reasoning is stable around 0.50 EM | `outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/summary.md` | Closed |
| Open BM25 is a hard stress setting, not a solved setting | `outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/*open_bm25*.csv` | Closed |
| Retrieval exposure and verifier-guided portfolio improve Open EM | `outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/portfolio_report.md` | Closed |
| TAT-QA portability clears the pre-set gate | `outputs/eval/tatqa_100_portability_v50/summary.md` | Closed |
| Failure analysis is available for supported-wrong numeric errors | `*_failures.md` and `*_row_operation_diagnostics.md` under v48/v50 outputs | Closed |

## Not Yet Closed

| Gap | Why it matters | Minimal run |
| --- | --- | --- |
| Optional FinQA-600 LLM Direct RAG baseline | Could strengthen external model comparison, but costs API budget | `configs/experiments.finqa_600.llm_direct_rag.json` |
| Full TAT-QA benchmark | Would strengthen cross-benchmark scope, but is beyond the current local closure | New fixed-seed manifest |

## Gates

Run:

```powershell
python .\scripts\check_experiment_closure.py
```

Current expected behavior:

- PASS on main FinQA-600 Full EviGraph gates.
- PASS on guarded retrieval portfolio.
- PASS on TAT-QA-100 portability.
- PASS on FinQA-600 v48 component closure.
- PASS on TAT-QA-100 method closure.

## Minimal Next Commands

```powershell
cd .
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.submission_component_closure_v48.json
python .\scripts\analyze_statistics.py --inputs .\outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv .\outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv .\outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_source_rerank_component_closure_v48.csv --output .\outputs\eval\finqa_600_submission_component_closure_v48\statistical_confidence.md
python .\scripts\run_manifest.py --manifest .\configs\experiments.tatqa_100.submission_method_closure_v50.json
python .\scripts\check_experiment_closure.py
```

## Paper Use

Use the v48 FinQA-600 Full EviGraph result as the main result.
Use v46 guarded portfolio as the open-retrieval improvement result.
Use v50 TAT-QA-100 as the portability result.
Use the v48 component closure as the final deterministic ablation table.
Use v28 ablation only as historical development context.
