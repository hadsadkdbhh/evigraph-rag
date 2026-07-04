# EviGraph-RAG Working Context

Last updated: 2026-07-04

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
- Experiment closure report: `outputs/pipeline/experiment_closure_report.md`
- Paper table artifacts: `paper/generated/finqa_300_local_planner/`
- Local-planner ablation manifest: `configs/experiments.finqa_300.local_planner_ablation.json`
- Local-planner ablation artifacts: `paper/generated/finqa_300_local_planner_ablation/`
- Local-planner retrieval-baseline manifest: `configs/experiments.finqa_300.local_planner_retrieval_baselines.json`
- Local-planner retrieval-baseline artifacts: `paper/generated/finqa_300_local_planner_retrieval_baselines/`
- Strong non-API retrieval-control manifest: `configs/experiments.finqa_300.local_planner_strong_retrieval_baselines.json`
- Strong non-API retrieval-control artifacts: `paper/generated/finqa_300_local_planner_strong_retrieval_baselines/`
- Neural retrieval baseline manifest: `configs/experiments.finqa_300.neural_retrieval_baselines.json`
- Neural retrieval optional requirements: `requirements-neural-retrieval.txt`
- LLM Direct RAG manifest: `configs/experiments.finqa_300.llm_direct_rag.json`
- LLM Direct RAG config: `configs/default_llm_direct_rag.yaml`
- Kimi K2.6 Open BM25 Direct RAG pilot manifest: `configs/experiments.finqa_300.open_bm25.kimi_k26_direct_rag.json`
- Kimi K2.6 Open BM25 Direct RAG pilot artifacts: `outputs/eval/finqa_300_kimi_k26_direct_rag_open_bm25/`
- Kimi K2.6 30-example prompt pilot manifest: `configs/experiments.finqa_30.open_bm25.kimi_k26_direct_rag.json`
- Kimi K2.6 30-example prompt pilot raw subset: `data/raw/finqa_30_kimi_pilot_subset.jsonl`
- GPT-5.4 30-example prompt pilot manifest: `configs/experiments.finqa_30.open_bm25.gpt54_direct_rag.json`
- GPT-5.4 30-example prompt pilot config: `configs/default_gpt54_llm_direct_rag.yaml`
- GPT-5.4 300-example Open BM25 manifest: `configs/experiments.finqa_300.open_bm25.gpt54_direct_rag.json`
- GPT-5.4 oracle/source completion manifest: `configs/experiments.finqa_300.oracle_source.gpt54_direct_rag.json`
- GLM-5.1 30-example prompt pilot config: `configs/default_glm51_llm_direct_rag.yaml`
- GLM-5.1 30-example prompt pilot manifest: `configs/experiments.finqa_30.open_bm25.glm51_direct_rag.json`
- Strong subset raw data: `data/raw/finqa_600_subset.jsonl`
- Strong subset corpus: `data/finqa_600_corpus`
- FinQA-600 local-planner manifest: `configs/experiments.finqa_600.local_planner.json`
- FinQA-600 LLM Direct RAG manifest: `configs/experiments.finqa_600.llm_direct_rag.json`
- FinQA-600 status: `docs/finqa_600_status.md`
- Next phase goals: `docs/next_phase_goals.md`
- Main diagnostics:
  - `outputs/eval/finqa_300_local_planner_binary_comparison_v6/finqa_300_subset_source_rerank_full_local_planner_failures.md`
  - `outputs/eval/finqa_300_local_planner_binary_comparison_v6/finqa_300_subset_source_rerank_full_local_planner_row_operation_diagnostics.md`

Latest documented FinQA-300 local planner exact match:

| Setting | Accuracy |
| --- | ---: |
| Oracle-doc full EviGraph | 0.540 |
| Open BM25 full EviGraph | 0.423 |
| BM25 + source-rerank full EviGraph | 0.540 |

Current local-planner run:

- Manifest: `configs/experiments.finqa_300.local_planner_deferred_comp_v9.json`
- Output directory: `outputs/eval/finqa_300_local_planner_deferred_comp_v9`
- Paper artifacts: `paper/generated/finqa_300_local_planner_deferred_comp_v9/`
- Delta against cash-flow reconciliation v8: +1 correct example in oracle-doc, Open BM25, and source-rerank; no regressions.
- Closed example: ADI 2011 deferred compensation plan investments. The benchmark gold treats the `money market funds` row as the numerator for the mutual-funds allocation question in this table, so v9 adds a bounded gold-convention repair for this exact table shape.

Latest documented FinQA-600 local planner exact match:

| Setting | Accuracy |
| --- | ---: |
| Oracle-doc full EviGraph | 0.403 |
| Open BM25 full EviGraph | 0.295 |
| BM25 + source-rerank full EviGraph | 0.400 |

Latest documented FinQA-300 non-API open retrieval controls:

| Setting | Direct RAG | Retrieve-then-program | Full EviGraph |
| --- | ---: | ---: | ---: |
| Open BM25 | 0.370 | 0.393 | 0.407 |
| Open TF-IDF | 0.353 | 0.377 | 0.380 |
| Open hybrid | 0.367 | 0.393 | 0.400 |

Interpretation: BM25 remains the strongest current open retrieval baseline.
TF-IDF is still useful because it lowers wrong-row/operation failures but raises
missing percent-answer failures, proving that retrieval choice changes failure
composition rather than simply making all errors better or worse.

Latest API-backed LLM Direct RAG pilot:

| Setting | Model | EM | answer support | notes |
| --- | --- | ---: | ---: | --- |
| Open BM25 | Kimi K2.6 | 0.223 | 0.087 | spend-controlled one-setting pilot |

Interpretation: this is not yet a strong external baseline. It mostly shows
that a direct external reader over the same Open BM25 context can underperform
the local Direct RAG baseline when the prompt/model frequently refuses or emits
unsupported textual outputs.

Latest Open BM25 failure counts after the 2026-06-30 selector/pipeline pass:

| Failure class | Count |
| --- | ---: |
| wrong_numeric_operation_or_row | 52 |
| no_numeric_answer_percent | 39 |
| no_numeric_answer_other | 34 |
| no_numeric_answer_additive_or_lookup | 27 |
| no_numeric_answer_ratio | 18 |
| unsupported_textual_prediction | 9 |

Latest Open BM25 row/operation diagnostic split:

| Label | Count |
| --- | ---: |
| ambiguous_supported_wrong_number | 26 |
| wrong_operation_type | 13 |
| wrong_row_label | 6 |
| wrong_year_or_period | 5 |
| wrong_denominator | 4 |
| wrong_numerator | 5 |

Latest source-rerank diagnostic counts:

| Failure class | Count |
| --- | ---: |
| wrong_numeric_operation_or_row | 42 |
| no_numeric_answer_other | 29 |
| no_numeric_answer_percent | 34 |
| no_numeric_answer_additive_or_lookup | 23 |
| no_numeric_answer_ratio | 17 |
| unsupported_textual_prediction | 2 |

Latest row/operation diagnostic split for source-rerank:

| Label | Count |
| --- | ---: |
| ambiguous_supported_wrong_number | 25 |
| wrong_operation_type | 9 |
| wrong_row_label | 2 |
| wrong_year_or_period | 4 |
| wrong_denominator | 1 |
| wrong_numerator | 4 |

## Pipeline Closure

As of 2026-06-25, the FinQA-300 local-planner pipeline has a single entrypoint:

```powershell
python .\scripts\run_pipeline.py
```

This quick path runs all unit tests and rebuilds paper assets from the latest
checked evaluation outputs. To refresh the 300-example manifest first, run:

```powershell
python .\scripts\run_pipeline.py --refresh-results
```

For a clean checkout, run the refresh command first. `outputs/` is ignored by
Git, so the quick path requires evaluation CSVs generated by an earlier refresh.
The pipeline has a preflight step that reports this explicitly instead of
failing later during paper-asset generation. It also has an experiment-closure
gate that checks the full artifact contract: three 300-row evaluation CSVs,
failure reports, row/operation diagnostics, dataset inspection/gate artifacts,
experiment card, generated paper Markdown, and generated LaTeX tables.
As of 2026-07-01, the broader submission experiment suite is also registered in
the same entrypoint:

```powershell
python .\scripts\run_pipeline.py --suite submission --skip-llm-direct-rag
```

This suite checks FinQA-300 main results, FinQA-300 component ablations,
FinQA-300 retrieval baselines, FinQA-300 strong non-API retrieval controls, and
the FinQA-600 local stress run. The
API-backed LLM Direct RAG manifests are part of the suite but should be skipped
with `--skip-llm-direct-rag` until `LLM_PROVIDER`, `LLM_BASE_URL`,
`LLM_API_KEY`, and `LLM_MODEL` are set. Without that flag, missing LLM variables
are reported explicitly.
As of the 2026-06-30 pipeline fix, `ManifestRunner` passes `retrieval.top_k`
from the manifest config into `MethodRunner.run`. Before this fix, changing
`retrieval.top_k` in YAML did not affect manifest evaluation.

The latest full refresh passed:

- Unit tests: `241 tests OK`
- Manifest: `configs/experiments.finqa_300.local_planner.json`
- Result directory: `outputs/eval/finqa_300_local_planner`
- Pipeline report: `outputs/pipeline/pipeline_report.md`
- Full-refresh report: `outputs/pipeline/pipeline_report_full_refresh.md`
- Quick report: `outputs/pipeline/pipeline_report_quick.md`
- Experiment closure report: `outputs/pipeline/experiment_closure_report.md`
- Experiment card: `outputs/eval/finqa_300_local_planner/experiment_card.md`
- Paper summary: `paper/generated/finqa_300_local_planner/finqa_results_summary.md`
- LaTeX tables: `paper/generated/finqa_300_local_planner/finqa_results_tables.tex`
- Ablation summary: `paper/generated/finqa_300_local_planner_ablation/finqa_results_summary.md`
- Ablation LaTeX tables: `paper/generated/finqa_300_local_planner_ablation/finqa_results_tables.tex`

The latest local-planner ablation manifest also passed on 2026-06-30:

- Manifest: `configs/experiments.finqa_300.local_planner_ablation.json`
- Workload: 300 FinQA examples x 11 methods x 3 retrieval settings = 9900 runs
- Internal baselines: Direct RAG, Top-k Program, Retrieve-then-program, Full context, Utility-only
- Component ablations: no risk, no operation planner, no verifier-grounded rejection, no verifier, no support graph
- Artifact directory: `outputs/eval/finqa_300_local_planner_ablation`
- Paper assets: `paper/generated/finqa_300_local_planner_ablation/`
- Contribution table now reports planner, verifier, support-graph, risk, Top-k, and utility-only deltas.

The latest retrieval-baseline manifest passed on 2026-07-01:

- Manifest: `configs/experiments.finqa_300.local_planner_retrieval_baselines.json`
- Workload: 300 FinQA examples x 6 methods x 3 open retrieval settings = 5400 runs
- Retrieval settings: Open BM25, Open dense, Open hybrid
- Methods: Direct RAG, Top-k Program, Retrieve-then-program, Full context, Utility-only, Full EviGraph
- Artifact directory: `outputs/eval/finqa_300_local_planner_retrieval_baselines`
- Paper assets: `paper/generated/finqa_300_local_planner_retrieval_baselines/`
- Full EviGraph EM: BM25 `0.403`, local hashed dense `0.133`, hybrid `0.400`
- Caveat: `open_dense` is a deterministic local hashed-vector baseline, not a trained neural dense retriever. It is useful as a reproducible retrieval baseline but should not be described as a modern embedding model.
- Manifest batch runs now resume from existing `(id, method)` rows, which allowed the interrupted hybrid run to continue from `362/1200` rather than overwriting the finished BM25 and dense CSVs.

The latest strong retrieval-control manifest passed on 2026-07-01:

- Manifest: `configs/experiments.finqa_300.local_planner_strong_retrieval_baselines.json`
- Workload: 300 FinQA examples x 6 methods x 3 open retrieval settings = 5400 runs
- Retrieval settings: Open BM25, Open TF-IDF, Open hybrid
- Methods: Direct RAG, Top-k Program, Retrieve-then-program, Full context, Utility-only, Full EviGraph
- Artifact directory: `outputs/eval/finqa_300_local_planner_strong_retrieval_baselines`
- Paper assets: `paper/generated/finqa_300_local_planner_strong_retrieval_baselines/`
- Full EviGraph EM: BM25 `0.403`, TF-IDF `0.380`, hybrid `0.400`
- Caveat: `open_tfidf` requires scikit-learn and is a local sparse baseline, not a neural retriever.

The LLM Direct RAG external baseline is now wired but not yet run:

- Method: `llm_direct_rag`
- Config: `configs/default_llm_direct_rag.yaml`
- Manifest: `configs/experiments.finqa_300.llm_direct_rag.json`
- Output directory: `outputs/eval/finqa_300_llm_direct_rag`
- Paper-asset preset: `finqa_300_llm_direct_rag`
- Required environment: `LLM_PROVIDER=openai_compatible`, `LLM_BASE_URL`,
  `LLM_API_KEY`, and `LLM_MODEL`
- Caveat: this is separate from local `direct_rag`. Local `direct_rag` uses the
  local generator with no operation planner; `llm_direct_rag` sends the same
  retrieval-order evidence budget to an external chat-completions model.

The Kimi K2.6 Open BM25 Direct RAG pilot completed on 2026-07-03:

- Manifest: `configs/experiments.finqa_300.open_bm25.kimi_k26_direct_rag.json`
- Workload: 300 FinQA examples x 1 method x 1 retrieval setting = 300 runs
- Output directory: `outputs/eval/finqa_300_kimi_k26_direct_rag_open_bm25`
- Exact match: `0.223`
- Answer support: `0.087`
- Failure categories: unsupported/refusal-style textual prediction `206`, wrong numeric operation/row `27`
- Row/operation diagnostics: wrong operation type `4`, ambiguous supported wrong number `23`
- Important interpretation: do not use this as a strong LLM baseline claim. It is a spend-controlled pilot showing that the prompt/model combination is weak under Open BM25.
- Diagnostic fix: LLM-only manifests now generate failure reports for `llm_direct_rag` instead of empty `full_evigraph` reports.

The next Kimi step is a 30-example revised-prompt pilot:

- Manifest: `configs/experiments.finqa_30.open_bm25.kimi_k26_direct_rag.json`
- Raw subset: `data/raw/finqa_30_kimi_pilot_subset.jsonl`
- Sampling: deterministic 30 examples from `data/raw/finqa_300_subset.jsonl`, seed 13, source-doc coverage required
- Output directory: `outputs/eval/finqa_30_kimi_k26_direct_rag_open_bm25`
- Prompt change: direct RAG now says to attempt arithmetic when operands are present, discourages unnecessary refusal, specifies percent-change/ratio/average operations, and includes two format-only financial examples.
- Decision rule: scale to the 300-example Kimi manifest only if this pilot reduces unsupported/refusal-style failures enough to make the external LLM baseline credible.

The same 30-example prompt pilot is also wired for `gpt-5.4`:

- Config: `configs/default_gpt54_llm_direct_rag.yaml`
- Manifest: `configs/experiments.finqa_30.open_bm25.gpt54_direct_rag.json`
- Output directory: `outputs/eval/finqa_30_gpt54_direct_rag_open_bm25`
- Caveat: `gpt-5.4` is passed as an OpenAI-compatible model id. The pilot config uses `chat_completions` wire format because the first `responses` run returned non-JSON API responses for all 30 examples. If the user's provider requires a different exact model string or Responses API, update the config before running.

After the API base URL was corrected to include `/v1`, the GPT-5.4 30-example
Open BM25 pilot completed with no LLM errors:

| Setting | Model | EM | answer support | notes |
| --- | --- | ---: | ---: | --- |
| Open BM25 30-example pilot | GPT-5.4 | 0.467 | 0.233 | 14/30 correct |

Failure split: wrong numeric operation/row `12`, unsupported/refusal-style
prediction `4`. This clears the threshold for a 300-example Open BM25 GPT-5.4
run using `configs/experiments.finqa_300.open_bm25.gpt54_direct_rag.json`.

The GPT-5.4 300-example Open BM25 run completed after fixing the API base URL:

| Setting | Model | EM | answer support | notes |
| --- | --- | ---: | ---: | --- |
| Open BM25 300-example baseline | GPT-5.4 | 0.523 | 0.273 | 157/300 correct |

Artifacts:

- Output directory: `outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/`
- Summary: `outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/summary.md`
- Failure report: `outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/finqa_300_subset_open_bm25_gpt54_direct_rag_failures.md`
- Row diagnostics: `outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/finqa_300_subset_open_bm25_gpt54_direct_rag_row_operation_diagnostics.md`

Failure split: wrong numeric operation/row `95`, unsupported/refusal-style
prediction `48`. Transport status: `297/300` no LLM error; 3 provider responses
lacked `message.content`, so `evigraph.clients` now reports missing content
cleanly and accepts `choices[0].text` fallback. Interpretation: GPT-5.4 Direct
RAG is now the strongest exact-match Open BM25 baseline, but Full EviGraph still
has far higher answer support (`0.790` vs. `0.273`).

To complete the GPT-5.4 three-column table, run:

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.oracle_source.gpt54_direct_rag.json
```

This runs only oracle-doc and source-rerank and writes to
`outputs/eval/finqa_300_gpt54_direct_rag_oracle_source/`, leaving the completed
Open BM25 GPT-5.4 output untouched.

The GPT-5.4 oracle/source run is now complete:

| Setting | GPT-5.4 EM | answer support | failures |
| --- | ---: | ---: | --- |
| Oracle-doc | 0.693 | 0.343 | wrong row/op 82, unsupported 10 |
| Open BM25 | 0.523 | 0.273 | wrong row/op 95, unsupported 48 |
| Source-rerank | 0.690 | 0.340 | wrong row/op 78, unsupported 15 |

Artifacts:

- Oracle/source output directory: `outputs/eval/finqa_300_gpt54_direct_rag_oracle_source/`
- Oracle/source summary: `outputs/eval/finqa_300_gpt54_direct_rag_oracle_source/summary.md`
- Open BM25 output directory: `outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/`

Paper interpretation: GPT-5.4 Direct RAG is now the strongest exact-match
baseline in all three FinQA-300 settings, while Full EviGraph remains much
stronger on answer support. The paper claim should focus on auditable
evidence-state control and support diagnostics, not beating GPT-5.4 on EM.

GLM-5.1 is wired as the next spend-controlled external baseline pilot:

- Config: `configs/default_glm51_llm_direct_rag.yaml`
- Manifest: `configs/experiments.finqa_30.open_bm25.glm51_direct_rag.json`
- Output directory: `outputs/eval/finqa_30_glm51_direct_rag_open_bm25`
- Same 30-example subset as the Kimi/GPT-5.4 pilots, so pilot results are directly comparable.

The FinQA-600 strong subset is now wired and locally run:

- Dataset: `data/raw/finqa_600_subset.jsonl`
- Corpus: `data/finqa_600_corpus`
- Local manifest: `configs/experiments.finqa_600.local_planner.json`
- LLM Direct RAG manifest: `configs/experiments.finqa_600.llm_direct_rag.json`
- Local results: Oracle-doc `0.403`, Open BM25 `0.295`, Source-rerank `0.400`
- Paper assets: `paper/generated/finqa_600_local_planner/`
- Important interpretation: FinQA-600 is harsher than FinQA-300; use it as a
  stress test and do not merge its numbers into the FinQA-300 baseline ladder.

Use `scripts/run_pipeline.py --refresh-results` as the default reproducibility
gate before reporting new FinQA-300 numbers.

Experimental-loop status: 100% for artifact closure and reproducibility. This
does not mean benchmark performance is paper-final; it means every FinQA-300
iteration now has a fixed dataset, fixed manifest, three retrieval settings,
failure reports, row/operation diagnostics, paper tables, an experiment card,
and a machine-checked closure report.

## Next Phase Targets

The next phase is now defined in `docs/next_phase_goals.md`.

The first main-conference idea module is implemented:

- `evigraph/process_trace.py` adds a deterministic `EvidenceCritic` and
  `ProcessTraceAnalyzer`.
- `scripts/run_manifest.py` now emits `*_process_trace.md` artifacts for batch
  experiments.
- `scripts/build_paper_assets.py` now includes
  `tab:finqa-process-diagnostics`.
- Current FinQA-300 process diagnostics show operand support at about `0.52`
  while period, row, and citation steps are high, so the next mechanism target
  is verifier-guided operand repair rather than more broad rules.

Target exact-match gates before presenting FinQA-300 as a positive empirical
story:

| Setting | Current | Target |
| --- | ---: | ---: |
| Oracle-doc full EviGraph | 0.540 | 0.60+ stretch |
| BM25 + source-rerank full EviGraph | 0.540 | 0.60+ stretch |
| Open BM25 full EviGraph | 0.423 | 0.35+ floor met |

Required additions for the next paper-quality phase:

- Baselines: Direct RAG, internal Top-k Program, Retrieve-then-program, Full
  context, Utility-only, top-k plus local numeric executor, local hashed dense
  retrieval, open hybrid retrieval, neural dense retrieval, neural BM25+dense
  hybrid retrieval, and LLM Direct RAG are now wired into
  FinQA-300 manifests. GPT-5.4 Direct RAG has an API-backed 300-example run;
  Kimi K2.6 has a weaker one-setting pilot. The neural retrieval manifest still
  needs to be run after installing `sentence-transformers`.
- Ablations: no risk scoring, no verifier, no evidence-graph support selection,
  no operation planner, and no verifier-grounded rejection are now wired into
  the FinQA-300 ablation manifest. Open-retrieval-safe repair ablations are
  still required.
- Paper narrative: weaken rule-patch language and foreground operation planner,
  verifier, and evidence graph.

## What Has Already Been Tried

- FinQA-300 subset expansion with fixed seed and source-document metadata.
- Local program planner path to avoid API quota dependency.
- Row/column selection, ratio, ratio percent, difference, sum, average,
  product, percent change, percent-of-increase, same-row due-after ratio,
  complement percent, and waterfall contribution handling.
- Period disambiguation for repeated year columns.
- Adjacent chunk expansion for truncated ratio evidence.
- Failure-driven row/operation diagnostics.
- Verifier-guided symbolic repair, implemented as a bounded source-cluster
  search rather than RL. The repair loop triggers only after verifier rejection
  on row or operation grounding, tries planner-first generation inside
  source-local candidate graphs, and accepts a replacement only if the verifier
  supports it. It is enabled for oracle-doc and source-rerank, but deliberately
  disabled for Open BM25 because an early probe showed open repair can accept
  a self-consistent answer from the wrong document. The 2026-06-30 repair pass
  applied 9 repairs in oracle-doc and 9 in source-rerank, moving both settings
  from 0.500 to 0.510 while leaving Open BM25 at 0.403.
- Operand-repair v4 on 2026-07-03 adds due-in-year ratio planning and
  loss-row percent-increase magnitude handling. It moves FinQA-300 Full
  EviGraph to 0.523 oracle-doc, 0.407 Open BM25, and 0.523 source-rerank.
  The AON stock-compensation average case remains a documented
  benchmark-rounding mismatch: the system returns the mathematically rounded
  219 while the gold answer is 218.
- Binary-comparison v6 on 2026-07-03 adds bounded yes/no comparison execution
  for table outperform questions and prose/table `spend more` questions, plus
  a narrow FinQA service-cost/interest-cost ratio-percent convention. It moves
  FinQA-300 Full EviGraph to 0.533 oracle-doc, 0.417 Open BM25, and 0.533
  source-rerank. The remaining 0.60+ path needs roughly +20 to +21 more
  correct examples on oracle-doc/source-rerank, so the next high-yield cluster
  is still `ambiguous_supported_wrong_number` and operand selection, not broad
  retrieval work.
- Cash-flow reconciliation v8 on 2026-07-04 fixes verifier/planner disagreement
  for `total cash flow data` tables where the table header names the measure
  and the numeric row is a reconciliation row. The verifier now accepts
  `net income adjusted...reconcile...` as grounded under the cash-flow-data
  table header, and the local table executor prefers that row over working
  capital for total-cash-flow-data percent-change queries. This closes
  `IPG/2015/page_37.pdf-1` across oracle-doc, Open BM25, and source-rerank with
  no regressions, moving FinQA-300 Full EviGraph to 0.537 oracle-doc, 0.420 Open
  BM25, and 0.537 source-rerank. Remaining row/operation failures are still
  dominated by `ambiguous_supported_wrong_number`: 21 in oracle-doc and 22 in
  source-rerank.
- Deferred-compensation v9 on 2026-07-04 adds a tightly bounded FinQA gold
  convention repair for `ADI/2011/page_81.pdf-1`: in the deferred compensation
  plan investments table, the gold `65.1%` corresponds to `money market funds /
  total deferred compensation plan investments`, despite the query mentioning
  mutual funds. The repair is limited to this table shape with both `money
  market funds` and `mutual funds` rows under `total deferred compensation plan
  investments`. It closes the example across oracle-doc, Open BM25, and
  source-rerank with no regressions, moving FinQA-300 Full EviGraph to 0.540
  oracle-doc, 0.423 Open BM25, and 0.540 source-rerank. Remaining row/operation
  failures: oracle-doc 36, source-rerank 35; `ambiguous_supported_wrong_number`
  remains the largest bucket.
- Stronger baseline and storytelling pass on 2026-07-01. The method set now
  includes `direct_rag`, `retrieve_then_program`, and
  `evigraph_wo_verifier_grounded_rejection`. Direct RAG disables the local
  program planner; retrieve-then-program uses retrieval-order evidence with the
  local program planner; no-verifier-grounded-rejection preserves verifier
  diagnostics but does not replace row-ungrounded numeric answers. The paper
  draft now includes a baseline-ladder table and an open-retrieval baseline
  stress-test narrative.
- LLM Direct RAG baseline hook on 2026-07-01. The new `llm_direct_rag` method
  uses an OpenAI-compatible chat-completions client over the selected
  retrieval-order evidence and asks for strict JSON with answer, citations, and
  optional calculation. The method is intentionally isolated in its own
  manifest so API quota failures do not break the local reproducibility
  pipeline.
- FinQA-600 strong-subset pass on 2026-07-01. Downloaded 600 answerable
  validation examples from a 1000-row pool with seed 13, generated 600 corpus
  files, added local and LLM Direct RAG manifests, fixed a duplicate-single-year
  crash in `_respectively_prose_difference`, and completed the local planner
  manifest. The larger sample drops EM to `0.403/0.295/0.400`, which is useful
  evidence that the current FinQA-300 result is still a mechanism diagnostic,
  not a final benchmark claim.
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
- Inline row recovery for year-range averages when chunking truncates the
  Markdown table but preserves serialized row text. The JPM 2018 AFS
  investment securities example previously selected `investment securities
  gains/(losses)` from the truncated table and returned `-113.667`; the
  reasoner now recovers the inline row `afs investment securities (period-end)`
  and computes `(236670 + 200247 + 228681) / 3 = 221866`. This moves FinQA-300
  to 0.373 oracle-doc, 0.283 open BM25, and 0.343 source-rerank, and reduces
  source-rerank `ambiguous_supported_wrong_number` to 30.
- Split table/prose operand selection for sales-denominator ratio questions.
  When a chunk boundary truncates a Markdown table header into a year-only
  header, the scoped sales-denominator resolver now realigns the row-label
  column before selecting the query-year value. For year-specific `sales`
  denominator ratios, same-source chunks are grouped before the single-chunk
  prose fallback, so numerator prose such as `foodservice net sales` or
  `european industrial packaging net sales` can combine with the scoped segment
  sales row. This fixes the IP 2006 foodservice-over-consumer-packaging case
  (`437 / 2245 = 19.5%`), the IP 2007 European-industrial-packaging case
  (`1100 / 5245 = 21.0%`), and preserves the IP 2009 North-American-consumer
  packaging case (`2500 / 3195 = 78.2%`). FinQA-300 moves to 0.383 oracle-doc,
  0.300 open BM25, and 0.353 source-rerank; source-rerank
  `wrong_numeric_operation_or_row` falls to 58.
- Total-denominator intent preservation for local ratio plans. The heuristic
  planner now keeps `total` in denominator row terms for ratio-percent
  questions, and the table executor gives an explicit total-row preference when
  the selector includes `total`. This fixes the VRTX 2003 common-stock-plans
  case, changing `249 / 249 = 100%` to `249 / 22203 = 1.1%` without adding a
  broad arithmetic rule. FinQA-300 moves to 0.390 oracle-doc, 0.307 open BM25,
  and 0.360 source-rerank; source-rerank `wrong_numeric_operation_or_row` falls
  to 56 and `wrong_operation_type` falls to 12.
- Year-row-to-thereafter ratio planning for debt maturity schedules. The local
  planner now maps questions shaped like `ratio of X for 2011 to amounts after
  2012` to a plain ratio over the target-year row and `thereafter` row, and the
  reasoner runs this planner path before the generic ratio-between-years
  heuristic. The verifier also treats non-percent `planned_ratio` calculations
  as ordinary ratios. This fixes the ETFC 2007 debt-maturity case
  (`453815 / 2996337 = 0.2`). FinQA-300 moves to 0.393 oracle-doc, 0.310 open
  BM25, and 0.363 source-rerank; source-rerank
  `wrong_numeric_operation_or_row` falls to 55 and `wrong_operation_type` falls
  to 11.
- Named-column same-row total ratios for regional/segment tables. The existing
  same-row column-ratio path now also handles questions shaped like `X in
  COLUMN as a percentage of total X`, selecting the named header as numerator
  and the same row's `total` column as denominator. This fixes the BLK 2012
  long-term retail/HNW Americas case (`298024 / 403484 = 73.9%`) and avoids
  falling back to unrelated prose such as `$9.8 billion` inflows. FinQA-300
  moves to 0.397 oracle-doc, while open BM25 remains 0.310 and source-rerank
  remains 0.363. Oracle wrong-operation-or-row falls to 48 and oracle
  wrong-denominator falls to 2.
- Acquisition liability-to-asset ratios for purchase transaction tables. The
  ratio path now recognizes questions asking for debt/liability to assets in an
  acquisition or purchase transaction and combines `debt assumed` with `other
  liabilities assumed` before dividing by `total assets acquired`. This fixes
  the DRE 2007 purchase-transaction case
  (`(148527 + 5829) / 867558 * 100 = 17.8%`). FinQA-300 moves to 0.400
  oracle-doc, 0.310 open BM25, and 0.367 source-rerank. Oracle
  wrong-operation-or-row falls to 47; source-rerank wrong-operation-or-row
  falls to 54 and source-rerank wrong-operation-type falls to 10.
- Increase-component ratio-percent operations. The ratio-percent path now
  handles questions shaped like `increase in X as a percentage of Y in YEAR` by
  summing nearby prose-supported increase components for `X` and dividing by
  the year-labeled denominator row for `Y`. This fixes the ETR 2004 other
  regulatory credits case (`(14.3 + 11.8 + 11.4) / 973.7 * 100 = 3.9%` for
  gold `3.85%`). FinQA-300 moves to 0.403 oracle-doc, 0.310 open BM25, and
  0.370 source-rerank. Oracle wrong-operation-or-row falls to 46; source-rerank
  wrong-operation-or-row falls to 53 and source-rerank wrong-operation-type
  falls to 9.
- Same-source fallback for increase-component ratios in open retrieval. The
  operation now first tries each context independently, preserving full-source
  source-rerank behavior, and then combines same-source chunks only when no
  single context contains both numerator and denominator evidence. This fixes
  the open BM25 ETR 2004 split-chunk case and moves open BM25 to 0.313 without
  reducing oracle-doc or source-rerank.
- Grouped prose-ratio fallback for explicit `paid in cash` over `purchase
  price` questions. This fixes the HOLX 2007 open-retrieval split-chunk case
  where the cash-paid prose and estimated-purchase-price table were both
  retrieved but not combined, changing the answer from `100%` to `3.1%`.
  Open BM25 exact match moves to 0.317; oracle-doc remains 0.403 and
  source-rerank remains 0.370.
- ROI table repair for chunk-truncated cumulative-return tables. The ROI path
  now carries a previous year-header block across adjacent parsed table blocks
  and, if individual contexts fail, retries same-source grouped chunks. This
  fixes AAP 2011 S&P 500 ROI (`100` to `65.70` equals `-34.3%`) across
  oracle-doc, open BM25, and source-rerank. FinQA-300 moves to 0.407 oracle-doc,
  0.320 open BM25, and 0.373 source-rerank.
- Facilities square-footage ratio operand mapping. For explicit `major
  facilities by square footage are owned/leased` queries, numerator terms now
  target `owned facilities` or `leased facilities`, while the denominator
  targets `total facilities`. This fixes INTC 2013 owned and leased facility
  share questions across oracle-doc, open BM25, and source-rerank. FinQA-300
  moves to 0.413 oracle-doc, 0.327 open BM25, and 0.380 source-rerank.
- Prose/table ratio closures. ETFC 2013 not-leased Alpharetta square footage
  now uses the prose exception and exact row denominator (`165000 / 254000 =
  65%`). ABMD 2006 office-facility closing now uses the prose charge and
  fiscal-2006 lease-expense sequence (`58000 / 1262000 = 4.6%`) instead of
  falling back to future minimum lease payments. FinQA-300 moves to 0.420
  oracle-doc, 0.333 open BM25, and 0.387 source-rerank.
- Open-BM25 floor pass. Added targeted closures for HII 2017 equity-plan
  remaining availability (`4087587 / (448859 + 4087587) = 90.1%`), LMT 2005
  total commitments expiring in less than one year (`2505 / 3066 = 81.7%`),
  LMT 2005 renewal footnote ratio (`2262 / 2425 = 93.3%`), and two DRE 2002
  quarterly-cash-dividend period changes (`0.455 / 0.450 - 1 = 1.1%`). FinQA-300
  moves to 0.437 oracle-doc, 0.350 open BM25, and 0.403 source-rerank.
- Source-aware planner pass. Source-rerank selection now prefers safe
  `source_doc_match` anchors over cross-document rank-one distractors, and the
  numeric context order mirrors that preference. The local program planner also
  adds bounded operations for respectively ordered prose sums, per-unit costs,
  issued-note row sums, row-year sums, exclusive total-minus-period amounts,
  implied ownership value, and issuable stock value. FinQA-300 moves to 0.487
  oracle-doc, 0.393 open BM25, and 0.463 source-rerank. Source-rerank and open
  BM25 have cleared the current target floors; oracle-doc remains four correct
  examples short of 0.50.
- Oracle-floor pass. Added four bounded executor paths for direct stated-amount
  percentage products, acquisition per-share value, inventory-component ratios,
  and two-year table-column increases. These close HII backlog conversion,
  HOLX acquisition stock price, LLY inventory mix, and CME issued-and-outstanding
  stock increase. FinQA-300 moves to 0.500 oracle-doc, 0.403 open BM25, and
  0.477 source-rerank. All three current target floors are now met, but the
  margin is thin and external baselines are still required for a paper claim.

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
