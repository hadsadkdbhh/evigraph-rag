# EviGraph-RAG Experiment Data Package for Paper Writing

Created: 2026-07-14

Assume all relative paths below are resolved from the repository root:

```text
<repo-root>
```

This file lists the experiment data, result files, generated paper tables, and
paper-safe claims needed by the writing teammate. It is a pointer package, not a
copy of the raw CSV contents.

## 1. What To Use First

Use these files first when writing the experiment section:

```text
docs/submission_artifact_index.md
docs/experiments/submission_closure_check.md
docs/submission_pipeline_check.md
paper/generated/finqa_600_submission_component_closure_v48/finqa_results_summary.md
outputs/eval/finqa_600_submission_component_closure_v48/summary.md
outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/portfolio_report.md
outputs/eval/tatqa_100_submission_method_closure_v50/summary.md
```

Recommended writing order:

1. Use FinQA-600 v48 as the main deterministic component/baseline closure.
2. Use FinQA-600 guarded retrieval portfolio as the open-retrieval stress result.
3. Use TAT-QA-50/100 as a second-dataset portability check.
4. Use GPT-5.4 Direct RAG only as an API-backed reader sanity check, not as the
   deterministic main method.

## 2. Raw And Constructed Dataset Files

### FinQA

```text
data/raw/finqa_300_subset.jsonl
data/raw/finqa_600_subset.jsonl
data/finqa_300_corpus/
data/finqa_600_corpus/
```

Roles:

- `finqa_300_subset.jsonl`: development diagnostic subset used during method
  iteration and mechanism checks.
- `finqa_600_subset.jsonl`: larger fixed validation subset used for final
  submission closure and stress testing.
- `data/finqa_300_corpus/` and `data/finqa_600_corpus/`: serialized evidence
  corpus files used by retrieval and oracle/source settings.

### TAT-QA

```text
data/raw/tatqa_50_subset.jsonl
data/raw/tatqa_100_subset.jsonl
data/tatqa_50_corpus/
data/tatqa_100_corpus/
```

Roles:

- `tatqa_50_subset.jsonl`: inspected cross-format pilot used for small
  failure-driven repairs.
- `tatqa_100_subset.jsonl`: scaled portability check used in the final closure.
- TAT-QA results should be described as a portability check, not a full TAT-QA
  benchmark.

### Stress Suite

```text
data/raw/stress_external.jsonl
data/stress_corpus/
```

Role:

- Small synthetic/controlled stress suite with official-report and distractor
  evidence. Use only as mechanism debugging evidence, not as a benchmark claim.

## 3. Final Experiment Output Directories

### Main FinQA-600 Submission Closure

Directory:

```text
outputs/eval/finqa_600_submission_component_closure_v48/
```

Important files:

```text
summary.md
experiment_card.md
statistical_confidence.md
finqa_600_subset_oracle_doc_component_closure_v48.csv
finqa_600_subset_open_bm25_component_closure_v48.csv
finqa_600_subset_source_rerank_component_closure_v48.csv
*_failures.md
*_row_operation_diagnostics.md
*_retrieval_diagnostics.md
*_process_trace.md
```

Main Full EviGraph results:

| Setting | n | EM | Answer support |
| --- | ---: | ---: | ---: |
| Oracle-doc | 600 | 0.503 | 0.820 |
| Open BM25 | 600 | 0.377 | 0.787 |
| BM25 + source rerank | 600 | 0.502 | 0.822 |

Baseline / ablation values from the same closure:

| Setting | Direct RAG EM | Retrieve-then-program EM | Utility-only EM | No planner EM | Full EviGraph EM |
| --- | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0.460 | 0.485 | 0.478 | 0.445 | 0.503 |
| Open BM25 | 0.320 | 0.348 | 0.315 | 0.325 | 0.377 |
| BM25 + source rerank | 0.460 | 0.483 | 0.440 | 0.443 | 0.502 |

Component deltas to cite:

| Setting | Full vs no planner | Full vs retrieve-then-program | Full vs utility-only |
| --- | ---: | ---: | ---: |
| Oracle-doc | +0.058 | +0.018 | +0.025 |
| Open BM25 | +0.052 | +0.028 | +0.062 |
| BM25 + source rerank | +0.058 | +0.018 | +0.062 |

Failure analysis highlights:

| Setting | Wrong row/op | No numeric | No percent | Additive/lookup | Ratio | Unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 96 | 54 | 64 | 46 | 27 | 5 |
| Open BM25 | 116 | 63 | 90 | 55 | 37 | 4 |
| BM25 + source rerank | 96 | 55 | 64 | 47 | 27 | 4 |

Row/operation diagnostic highlights:

| Setting | Wrong year/period | Wrong row label | Wrong operation type | Ambiguous |
| --- | ---: | ---: | ---: | ---: |
| Oracle-doc | 7 | 9 | 19 | 69 |
| Open BM25 | 9 | 17 | 15 | 87 |
| BM25 + source rerank | 6 | 9 | 18 | 70 |

### FinQA-600 Retrieval Portfolio

Directory:

```text
outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/
```

Important file:

```text
portfolio_report.md
```

Main results:

| Selector | n | EM | 95% Wilson CI |
| --- | ---: | ---: | --- |
| BM25 primary | 600 | 0.377 | [0.339, 0.416] |
| Neural-hybrid candidate | 600 | 0.363 | [0.326, 0.403] |
| Guarded portfolio v46 | 600 | 0.407 | [0.368, 0.446] |

Paired comparison:

```text
Switches: 74
Wins vs BM25 primary: 18
Losses vs BM25 primary: 0
Paired McNemar p-value: < 0.001
```

Paper-safe interpretation:

- Better retrieval exposure alone does not guarantee better answers.
- Neural-hybrid candidates become useful only when a no-gold, verifier-guided
  evidence-state selector chooses the more executable state.

### TAT-QA-100 Submission Closure

Directory:

```text
outputs/eval/tatqa_100_submission_method_closure_v50/
```

Important files:

```text
summary.md
experiment_card.md
tatqa_100_oracle_doc_method_closure_v50.csv
tatqa_100_open_bm25_method_closure_v50.csv
*_failures.md
*_row_operation_diagnostics.md
*_retrieval_diagnostics.md
```

Main Full EviGraph results:

| Setting | n | EM | Answer support | Source hit@8 |
| --- | ---: | ---: | ---: | ---: |
| Oracle-doc | 100 | 0.520 | 0.750 | n/a |
| Open BM25 | 100 | 0.410 | 0.850 | 0.900 |

Baseline / ablation values:

| Setting | Direct RAG EM | Retrieve-then-program EM | Utility-only EM | No planner EM | Full EviGraph EM |
| --- | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0.490 | 0.520 | 0.520 | 0.480 | 0.520 |
| Open BM25 | 0.400 | 0.440 | 0.420 | 0.350 | 0.410 |

Paper-safe interpretation:

- TAT-QA-100 is a cross-format portability check.
- Do not claim full TAT-QA benchmark performance.
- Note that retrieve-then-program is competitive on TAT-QA-100 Open BM25; this
  reinforces the conservative claim boundary.

### TAT-QA-50 Pilot

Directory:

```text
outputs/eval/tatqa_50_senior_notes_issuance_sum_v50/
```

Main Full EviGraph results:

| Setting | n | EM | Answer support | Source hit@8 |
| --- | ---: | ---: | ---: | ---: |
| Oracle-doc | 50 | 0.540 | 0.740 | n/a |
| Open BM25 | 50 | 0.460 | 0.900 | 0.960 |

Use:

- Failure-driven pilot before scaling to TAT-QA-100.
- Good for appendix/failure-analysis narrative.

### GPT-5.4 Direct RAG Baseline

Directories:

```text
outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/
outputs/eval/finqa_300_gpt54_direct_rag_oracle_source/
paper/generated/finqa_300_gpt54_direct_rag/
```

Paper-facing summary:

| Setting | n | EM | Answer support |
| --- | ---: | ---: | ---: |
| Oracle-doc | 300 | 0.693 | 0.343 |
| Open BM25 | 300 | 0.523 | 0.273 |
| BM25 + source rerank | 300 | 0.690 | 0.340 |

Paper-safe interpretation:

- GPT-5.4 Direct RAG can match or exceed exact match in some settings.
- Its verifier-checked answer support is much lower, supporting the paper's
  EM/support-gap argument.
- This is API-backed and should be reported separately from deterministic local
  no-API closure.

## 4. Paper-Generated Table Directories

Use these when inserting tables into LaTeX:

```text
paper/generated/finqa_600_submission_component_closure_v48/
paper/generated/retrieval_portfolio_ablation/
paper/generated/statistical_confidence/
paper/generated/tatqa_50_cross_benchmark/
paper/generated/tatqa_100_portability_v50/
paper/generated/finqa_300_gpt54_direct_rag/
```

Specific LaTeX files:

```text
paper/generated/finqa_600_submission_component_closure_v48/finqa_main_tables.tex
paper/generated/finqa_600_submission_component_closure_v48/finqa_results_tables.tex
paper/generated/retrieval_portfolio_ablation/finqa_retrieval_portfolio_ablation.tex
paper/generated/statistical_confidence/main_confidence_table.tex
paper/generated/tatqa_50_cross_benchmark/tatqa_50_results.tex
paper/generated/tatqa_100_portability_v50/tatqa_100_results.tex
```

Usage:

- `finqa_main_tables.tex`: compact main-paper FinQA-600 tables.
- `finqa_results_tables.tex`: full diagnostic tables for appendix/artifact
  review.
- Retrieval portfolio, confidence, and TAT-QA tables are currently included in
  `paper/main.tex`.

## 5. Manifests For Reproduction

Final closure manifests:

```text
configs/experiments.finqa_600.submission_component_closure_v48.json
configs/experiments.tatqa_100.submission_method_closure_v50.json
configs/experiments.finqa_600.local_planner_guarded_top8_repair_v43.json
configs/experiments.finqa_600.neural_retrieval_full_evigraph_v43.json
```

TAT-QA pilot manifests:

```text
configs/experiments.tatqa_50.senior_notes_issuance_sum_v50.json
configs/experiments.tatqa_100.senior_notes_issuance_sum_v50.json
```

LLM Direct RAG manifests:

```text
configs/experiments.finqa_300.open_bm25.gpt54_direct_rag.json
configs/experiments.finqa_300.oracle_source.gpt54_direct_rag.json
```

## 6. Reproduction Commands

Final engineering gate:

```powershell
python .\scripts\check_submission_pipeline.py
```

Experiment closure check only:

```powershell
python .\scripts\check_experiment_closure.py
```

Run final FinQA-600 component closure:

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.submission_component_closure_v48.json
```

Generate FinQA-600 paper tables:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa_600_submission_component_closure_v48 --output-dir .\paper\generated\finqa_600_submission_component_closure_v48 --preset finqa_600_submission_component_closure_v48
```

Run TAT-QA-100 method closure:

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.tatqa_100.submission_method_closure_v50.json
```

Official AAAI compile/page check:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement
```

## 7. Current Gate Status

Final gate report:

```text
docs/submission_pipeline_check.md
```

Latest checked status:

```text
Overall status: PASS
Unit tests: 401 OK
Submission experiment closure: PASS
Official AAAI page budget: PASS
Main PDF: 7/7 main-content pages, references start on page 8
Supplement compile: PASS
LaTeX unresolved references/citations: none detected
```

## 8. Paper-Safe Claims

Safe to claim:

- EviGraph-RAG formulates numerically grounded RAG as Evidence State
  Optimization over candidate evidence states.
- FinQA-600 v48 provides the final deterministic component/baseline closure for
  the current submission boundary.
- Open-retrieval stress results show a gap between retrieval exposure and
  executable evidence-state selection.
- The guarded retrieval portfolio improves FinQA-600 Open BM25 from 0.377 to
  0.407 with 18 paired wins and 0 paired losses.
- TAT-QA-50/100 provides a second public financial QA portability check.
- GPT-5.4 Direct RAG shows that high exact match can still have weak
  verifier-checked answer support.

Do not claim:

- Do not claim state-of-the-art FinQA or TAT-QA performance.
- Do not present source-rerank as a deployable open-retrieval setting.
- Do not merge oracle-doc, open BM25, source-rerank, neural-hybrid, and
  portfolio numbers into one headline.
- Do not describe TAT-QA-100 as a full TAT-QA benchmark.
- Do not describe the current controller as reinforcement learning or a learned
  policy.

## 9. Quick Copy Tables For Paper

### Main Result Table

| Dataset / setting | Method | n | EM | Answer support |
| --- | --- | ---: | ---: | ---: |
| FinQA-600 Oracle-doc | Full EviGraph | 600 | 0.503 | 0.820 |
| FinQA-600 Open BM25 | Full EviGraph | 600 | 0.377 | 0.787 |
| FinQA-600 Source rerank | Full EviGraph | 600 | 0.502 | 0.822 |
| FinQA-600 Open BM25 | Guarded portfolio | 600 | 0.407 | 0.807 |
| TAT-QA-100 Oracle-doc | Full EviGraph | 100 | 0.520 | 0.750 |
| TAT-QA-100 Open BM25 | Full EviGraph | 100 | 0.410 | 0.850 |

### Baseline Ladder On FinQA-600

| Method | Oracle EM | Open EM | Source-rerank EM |
| --- | ---: | ---: | ---: |
| Direct RAG | 0.460 | 0.320 | 0.460 |
| Retrieve-then-program | 0.485 | 0.348 | 0.483 |
| Utility-only | 0.478 | 0.315 | 0.440 |
| No operation planner | 0.445 | 0.325 | 0.443 |
| Full EviGraph | 0.503 | 0.377 | 0.502 |

### GPT-5.4 Direct RAG Contrast

| Setting | EM | Answer support |
| --- | ---: | ---: |
| FinQA-300 Oracle-doc | 0.693 | 0.343 |
| FinQA-300 Open BM25 | 0.523 | 0.273 |
| FinQA-300 Source rerank | 0.690 | 0.340 |

Use the GPT-5.4 table to argue that exact-match accuracy alone is not enough
for grounded numerical RAG.
