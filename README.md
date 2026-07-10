# Evidence State Optimization with EviGraph-RAG

Evidence State Optimization (ESO) for numerically grounded RAG.

Core claim: retrieved information is not evidence. This project formulates RAG
as a search problem over an Evidence State Space (ESS). EviGraph-RAG is the
current implementation: it turns retrieval outputs into candidate evidence
states, scores their utility and risks, searches for a Minimal Reliable Support
Subgraph (MRSG), and generates grounded answers from that subgraph only.

## Reviewer-Facing Thesis

EviGraph-RAG is not primarily another GraphRAG retriever. Its central thesis is:

> Evidence is not the same object as retrieval.

Most RAG pipelines expose a top-\(K\) list of chunks to a reader. EviGraph-RAG
instead treats retrieval as a proposal step and asks a second question: which
candidate state is executable, low-risk, and sufficient to support the answer?

The paper story is intentionally focused on three contributions:

1. **Evidence State Optimization.** We define the problem as searching over
   states \(S \subseteq V\), not feeding a raw top-\(K\) prefix to a reader.
2. **Utility-Risk State Search.** We search states by trading off semantic/task
   utility against structural, temporal, source, operation, and verifier risks.
3. **Minimal Reliable Support Subgraph.** We generate answers only from the
   smallest compact support subgraph whose citations, operands, operations, and
   verifier checks are sufficient.

This is the boundary with generic GraphRAG/KG-RAG systems: those systems usually
retrieve or traverse nodes; ESO searches an evidence state space and verifies
whether the selected state is usable for numerical reasoning.

## Method Contract

For a query \(q\), retrieval produces a candidate evidence graph
\(G_q=(V_q,E_q)\).

**Evidence unit.** A node \(v \in V_q\) is a text span, table row/fragment,
source cue, parsed value, operation candidate, or verifier judgment that may
contribute to answering \(q\).

**Evidence state.** A state is a subset \(S_t \subseteq V_q\) at controller step
\(t\). It is not assumed to be correct evidence; it is a candidate support
configuration.

**Evidence state space.** The state space is
\(\Omega_q=(\mathcal{S}_q,\mathcal{T}_q)\), where \(\mathcal{S}_q\subseteq
2^{V_q}\) is the set of candidate states and \(\mathcal{T}_q\) contains
expansion, merge, prune, ranking, and repair transitions.

**Reliable support subgraph.** A state is reportable only when the induced
subgraph \(G_q[S]\) contains cited source values, executable operations, and
verifier checks sufficient for the final answer trace.

The controller is explicit rather than a black box:

1. **Expansion** gathers candidate passages, table fragments, source-local
   context, and retrieval-portfolio alternatives.
2. **Pruning** removes unsupported or high-risk nodes using source, period,
   operation, and verifier diagnostics.
3. **Ranking/selection** greedily builds a compact state under a budget.
4. **Repair** uses verifier failures to revisit operands, periods, or source
   exposure without accepting free-form numeric guesses.

A simplified risk-adjusted coverage objective is:

\[
f(S)=\sum_{a\in\mathcal{A}_q} w_a
\left(1-\prod_{v\in S}(1-\rho_v u_{v,a})\right),
\qquad
\rho_v=\exp(-\lambda_s r_v^{src}-\lambda_t r_v^{time}
-\lambda_o r_v^{op}-\lambda_c r_v^{conflict}).
\]

Here \(\mathcal{A}_q\) contains required aspects such as entity, year/period,
row label, denominator, and operation cue coverage. The discount \(\rho_v\)
reduces the value of nodes with source, temporal, operation, or conflict risk.
This coverage form is monotone submodular, so greedy evidence-state pruning has
the standard \((1-1/e)\) approximation guarantee under a cardinality budget.

The ideal MRSG target is the constrained problem:

\[
S^\star =
\arg\min_{S\in\mathcal{S}_q}|S|
\quad
\text{s.t.}\quad
\operatorname{Cov}(S,q)\ge\tau,\;
\operatorname{Risk}(S,q)\le\delta,\;
\operatorname{Conn}(G_q[S])=1,\;
\operatorname{Exec}(S,q)=1,\;
\operatorname{Ver}(S,q)=1.
\]

The current implementation uses deterministic verifier-guided state search:
initialize from retrieval candidates, expand source/table/operation evidence,
rank by utility-risk coverage, prune unsafe states, and repair only diagnosed
operand/source/period/operation failures.

## Submission Artifact Index

For the current AAAI-oriented paper package, start with:

- `docs/submission_artifact_index.md`

That file records the current reportable FinQA-300, FinQA-600, TAT-QA-50, and
TAT-QA-100 results, the command map for regenerating each table, and the claim
boundaries that should not be crossed in the paper.

## Reproducible FinQA-300 Pipeline

The current primary experiment is the 300-example FinQA local-planner diagnostic
run. It uses only the Python standard library and the checked-in FinQA subset,
so no API key or GPU is required.

From a clean checkout, run:

```powershell
python -m pip install -r requirements.txt
python scripts/run_pipeline.py --refresh-results
```

The full refresh performs the reproducibility gate end to end:

1. Runs the unit test suite.
2. Converts the checked-in FinQA-300 raw subset.
3. Builds the local BM25 index.
4. Runs oracle-doc, open BM25, and source-rerank full EviGraph evaluations.
5. Regenerates failure reports and row/operation diagnostics.
6. Rebuilds paper-ready Markdown and LaTeX tables.
7. Runs the experiment-closure gate over all expected CSVs, diagnostics, paper
   tables, and the experiment card.
8. Writes pipeline and closure reports under `outputs/pipeline/`.

After one successful full refresh, the faster local check is:

```powershell
python scripts/run_pipeline.py
```

The quick path reuses the generated evaluation CSVs under `outputs/eval/` and
only reruns tests plus paper-table generation. Because `outputs/` is ignored by
Git, a fresh clone should use `--refresh-results` first.

For the broader paper-submission experiment suite, run:

```powershell
python scripts/run_pipeline.py --suite submission --skip-llm-direct-rag
```

This checks the FinQA-300 main result, component ablations, retrieval baselines,
and the FinQA-600 stress subset. Remove `--skip-llm-direct-rag` only after
setting `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`; the LLM
Direct RAG baselines are intentionally API-backed and are not treated as
complete without those variables.

To refresh all local submission-suite results, run:

```powershell
python scripts/run_pipeline.py --suite submission --refresh-results --skip-llm-direct-rag
```

Expected current FinQA-300 exact-match results:

| setting | full EviGraph EM |
| --- | ---: |
| Oracle-doc | 0.523 |
| Open BM25 | 0.407 |
| BM25 + source rerank | 0.523 |

FinQA-600 is also checked in as a stronger validation-scale stress subset.
Current local-planner Full EviGraph exact-match results are:

| setting | full EviGraph EM |
| --- | ---: |
| Oracle-doc | 0.403 |
| Open BM25 | 0.295 |
| BM25 + source rerank | 0.400 |

Main reproducibility artifacts:

- `outputs/pipeline/pipeline_report.md`
- `outputs/pipeline/experiment_closure_report.md`
- `outputs/eval/finqa_300_local_planner_operand_repair_v4/summary.md`
- `outputs/eval/finqa_300_local_planner_operand_repair_v4/experiment_card.md`
- `outputs/eval/finqa_300_local_planner_operand_repair_v4/*_failures.md`
- `outputs/eval/finqa_300_local_planner_operand_repair_v4/*_row_operation_diagnostics.md`
- `outputs/eval/finqa_300_local_planner/summary.md`
- `outputs/eval/finqa_300_local_planner/experiment_card.md`
- `outputs/eval/finqa_300_local_planner/*_failures.md`
- `outputs/eval/finqa_300_local_planner/*_row_operation_diagnostics.md`
- `paper/generated/finqa_300_local_planner_operand_repair_v4/finqa_results_summary.md`
- `paper/generated/finqa_300_local_planner_operand_repair_v4/finqa_results_tables.tex`
- `paper/generated/finqa_300_local_planner/finqa_results_summary.md`
- `paper/generated/finqa_300_local_planner/finqa_results_tables.tex`
- `paper/generated/finqa_300_local_planner_ablation/finqa_results_summary.md`
- `paper/generated/finqa_300_local_planner_ablation/finqa_results_tables.tex`
- `paper/generated/finqa_300_local_planner_strong_retrieval_baselines/finqa_results_summary.md`
- `paper/generated/finqa_300_local_planner_strong_retrieval_baselines/finqa_results_tables.tex`
- `paper/generated/finqa_600_local_planner/finqa_results_summary.md`
- `paper/generated/finqa_600_local_planner/finqa_results_tables.tex`

These are diagnostic subset results, not final benchmark claims.

## MVP-0

Run a toy end-to-end pipeline with mock retrieved candidates:

```powershell
python scripts/run_query.py --method full_evigraph --query "According to the chart, how much higher was 2023 than 2022?"
```

The run writes:

- `outputs/runs/<run_id>/trace.jsonl`
- `outputs/runs/<run_id>/graph.json`
- `outputs/runs/<run_id>/answer.md`
- `outputs/runs/<run_id>/cost.json`

## Experiment Harness

Run baseline comparisons on the toy JSONL:

```powershell
python scripts/run_batch_eval.py --questions data/questions.jsonl --output outputs/eval/smoke.csv
```

Available methods:

- `topk`
- `full_context`
- `utility_only`
- `evigraph_wo_risk`
- `evigraph_wo_verifier`
- `evigraph_wo_support`
- `full_evigraph`

Run the default ablation suite:

```powershell
python scripts/run_ablation.py --questions data/questions.jsonl --output outputs/eval/ablation.csv
```

Run a tiny accuracy-cost Pareto sweep:

```powershell
python scripts/run_pareto.py --questions data/questions.jsonl --output outputs/eval/pareto.csv
```

CSV outputs include accuracy, support verification, citation correctness,
misleading acceptance, selected input tokens, tool calls, and latency.

Summarize one or more experiment CSV files as Markdown tables:

```powershell
python scripts/summarize_experiments.py --inputs outputs/eval/ablation.csv outputs/eval/pareto.csv --output outputs/eval/summary.md
```

Run an end-to-end experiment manifest that builds the local index, runs
ablation and Pareto sweeps, and writes a Markdown summary:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.mock.json
```

The manifest runner also writes `outputs/eval/manifest/experiment_card.md`,
which records datasets, methods, result files, environment details, git commit,
and current limitations for paper auditing.

Run the quick MVP0 acceptance gate used by CI:

```powershell
python scripts/run_mvp0_acceptance.py
```

Run the full MVP0 acceptance gate, including the checked-in 100-example FinQA
smoke subset:

```powershell
python scripts/run_mvp0_acceptance.py --with-finqa
```

Convert external benchmark files into the internal JSONL question format:

```powershell
python scripts/convert_dataset.py --input data/raw/mock_external.jsonl --output outputs/eval/converted_questions.jsonl --dataset-name mock_report
```

Manifests may also set `raw_questions` and `field_map` to run this conversion
automatically before evaluation.

Build a deterministic benchmark subset before conversion:

```powershell
python scripts/build_subset.py --input data/raw/full_annotations.jsonl --output data/raw/chartqa_subset.jsonl --corpus data/chartqa_corpus --sample-size 20 --seed 13 --require-source-doc --profile chartqa
```

Inspect converted benchmark questions before reporting results:

```powershell
python scripts/inspect_dataset.py --questions outputs/eval/converted_questions.jsonl --corpus data/corpus --md-output outputs/eval/dataset_inspection.md
```

Use `--fail-on-gate` to make inspection fail when records, required fields, or
source-document coverage do not meet the configured threshold.

Run the synthetic stress suite with official reports plus high-relevance
forecast, draft, and press distractors:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.stress.json
```

On the current stress suite, `full_evigraph` reaches perfect numeric accuracy
and rejects noisy evidence, while `topk` and `utility_only` fail on two of three
questions because they accept distracting evidence. This is a stress test, not a
public benchmark result.

Run the real FinQA validation subset:

```powershell
python scripts/download_finqa_subset.py --split validation --pool-size 100 --sample-size 20 --seed 13
python scripts/run_manifest.py --manifest configs/experiments.finqa.json
```

The checked-in FinQA subset uses `dreamerdeo/finqa`, validation split, pool size
100, sample size 100, and seed 13. The generated corpus serializes the source
pre-text, table, and post-text to Markdown and excludes the gold answer and gold
evidence annotations from retrieval.

The current FinQA-300 local-planner manifest uses the sample `source_doc` field
to evaluate oracle-document reasoning before open retrieval. On this diagnostic
subset, the latest operand-repair v4 pass reaches 0.523 exact match in
oracle-doc mode, 0.407 in open BM25 mode, and 0.523 in BM25 + source-rerank
mode. The CSVs also
report diagnostic verifier metrics including arithmetic support,
calculation-result support, operation-semantics checking, row-operation
grounding, and semantic grounding. These are diagnostic baselines, not final
benchmark claims.
The local-planner ablation manifest also includes a no-operation-planner
condition that keeps retrieval, evidence graph selection, support extraction,
executor, and verifier fixed while disabling the program-planner fallback.

Run the local-planner baseline/ablation manifest:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.finqa_300.local_planner_ablation.json
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa_300_local_planner_ablation --output-dir paper/generated/finqa_300_local_planner_ablation --preset finqa_300_local_ablation
```

Run the stronger non-API open-retrieval baseline suite. This adds Open TF-IDF
beside Open BM25 and Open hybrid; install the optional scikit-learn dependency
first if it is not already available:

```powershell
python -m pip install -r requirements-optional-baselines.txt
python scripts/run_manifest.py --manifest configs/experiments.finqa_300.local_planner_strong_retrieval_baselines.json
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa_300_local_planner_strong_retrieval_baselines --output-dir paper/generated/finqa_300_local_planner_strong_retrieval_baselines --preset finqa_300_local_strong_retrieval_baselines
```

Run the neural open-retrieval baseline suite after installing the optional
sentence-transformer dependency. By default this uses
`sentence-transformers/all-MiniLM-L6-v2`; set `EVIGRAPH_NEURAL_DENSE_MODEL` to
swap in a stronger embedding model.

```powershell
python -m pip install -r requirements-neural-retrieval.txt
$env:EVIGRAPH_NEURAL_DENSE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
python scripts/run_manifest.py --manifest configs/experiments.finqa_300.neural_retrieval_baselines.json
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa_300_neural_retrieval_baselines --output-dir paper/generated/finqa_300_neural_retrieval_baselines --preset finqa_300_neural_retrieval_baselines
```

Run the external LLM Direct RAG baseline after setting an OpenAI-compatible
chat-completions endpoint:

```powershell
$env:LLM_PROVIDER="openai_compatible"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_API_KEY="YOUR_KEY"
$env:LLM_MODEL="YOUR_MODEL"
python scripts/run_manifest.py --manifest configs/experiments.finqa_300.llm_direct_rag.json
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa_300_llm_direct_rag --output-dir paper/generated/finqa_300_llm_direct_rag --preset finqa_300_llm_direct_rag
```

Before spending on the full 300-example Kimi run, use the 30-example Open BM25
prompt pilot:

```powershell
$env:LLM_PROVIDER="openai_compatible"
$env:LLM_BASE_URL="YOUR_OPENAI_COMPATIBLE_BASE_URL"
$env:LLM_API_KEY="YOUR_KEY"
$env:LLM_MODEL="kimi-k2.6"
python scripts/run_manifest.py --manifest configs/experiments.finqa_30.open_bm25.kimi_k26_direct_rag.json
```

The pilot writes to `outputs/eval/finqa_30_kimi_k26_direct_rag_open_bm25/`.
Scale to the full 300-example manifest only if the pilot substantially reduces
refusal-style failures and improves exact match over the earlier Kimi Open BM25
pilot.

To run the same 30-example pilot with `gpt-5.4`, set your provider credentials
and use the GPT-5.4 manifest:

```powershell
$env:LLM_PROVIDER="openai_compatible"
$env:LLM_BASE_URL="YOUR_OPENAI_COMPATIBLE_BASE_URL"
$env:LLM_API_KEY="YOUR_KEY"
$env:LLM_MODEL="gpt-5.4"
python scripts/run_manifest.py --manifest configs/experiments.finqa_30.open_bm25.gpt54_direct_rag.json
```

The config also pins `model: gpt-5.4` in
`configs/default_gpt54_llm_direct_rag.yaml` and uses `chat_completions` wire
format because many relay providers do not expose the newer Responses API. If
your API provider uses a different exact model id or requires Responses API,
update that file before running.

If the 30-example pilot is healthy, scale GPT-5.4 to the 300-example Open BM25
baseline:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.finqa_300.open_bm25.gpt54_direct_rag.json
```

The 300-example run writes to
`outputs/eval/finqa_300_gpt54_direct_rag_open_bm25/`.
The current GPT-5.4 Open BM25 300-example result is `0.523` exact match with
`0.273` answer support; report it as a strong external accuracy baseline and a
grounding stress test.

To complete the GPT-5.4 three-setting comparison, run oracle-doc and
source-rerank only:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.finqa_300.oracle_source.gpt54_direct_rag.json
```

This writes to `outputs/eval/finqa_300_gpt54_direct_rag_oracle_source/` and
does not rerun the completed Open BM25 GPT-5.4 baseline.
Current GPT-5.4 Direct RAG exact match is `0.693` oracle-doc, `0.523` Open
BM25, and `0.690` source-rerank; answer support remains much lower at `0.343`,
`0.273`, and `0.340`.

Run the same 30-example Open BM25 prompt pilot with GLM-5.1:

```powershell
$env:LLM_PROVIDER="openai_compatible"
$env:LLM_BASE_URL="YOUR_OPENAI_COMPATIBLE_BASE_URL"
$env:LLM_API_KEY="YOUR_KEY"
$env:LLM_MODEL="glm-5.1"
python scripts/run_manifest.py --manifest configs/experiments.finqa_30.open_bm25.glm51_direct_rag.json
```

The GLM-5.1 pilot writes to
`outputs/eval/finqa_30_glm51_direct_rag_open_bm25/`.

Run the stronger FinQA-600 local-planner stress subset:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.finqa_600.local_planner.json
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa_600_local_planner --output-dir paper/generated/finqa_600_local_planner --preset finqa_600_local
```

Run the FinQA-600 LLM Direct RAG baseline with the same API variables:

```powershell
python scripts/run_manifest.py --manifest configs/experiments.finqa_600.llm_direct_rag.json
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa_600_llm_direct_rag --output-dir paper/generated/finqa_600_llm_direct_rag --preset finqa_600_llm_direct_rag
```

Generate a failure report for the FinQA ablation output:

```powershell
python scripts/analyze_failures.py --csv outputs/eval/finqa/finqa_subset_ablation.csv --method full_evigraph --output outputs/eval/finqa/finqa_subset_ablation_failures.md
```

Break wrong numeric operation/row failures into actionable diagnostic labels:

```powershell
python scripts/analyze_row_operation_errors.py --csv outputs/eval/finqa/finqa_subset_open_hybrid_ablation.csv --method full_evigraph --output outputs/eval/finqa/finqa_subset_open_hybrid_row_operation_diagnostics.md
```

The manifest runner writes this row/operation diagnostic automatically for each
batch experiment. The labels separate wrong numerator, wrong denominator,
wrong year or period, wrong row label, wrong operation type, and ambiguous
supported wrong-number cases.

Before reporting real benchmark numbers, follow the protocol in
`docs/benchmark_protocol.md`. A ChartQA-style manifest template is available at
`configs/experiments.chartqa.example.json`; populate `data/raw/chartqa_subset.jsonl`
and `data/chartqa_corpus` before running it.

## Paper and Submission Assets

The AAAI working draft lives in `paper/main.tex`. The supplementary entrypoint
is `paper/supplement.tex`, which compiles `paper/appendix.tex` separately from
the main submission PDF. The current submission plan, release notes, and claim
boundaries are tracked in:

- `docs/submission_readiness_aaai27.md`
- `docs/submission_artifact_index.md`
- `docs/code_data_release_note.md`
- `docs/aaai_readiness.md`
- `docs/project_status.md`

Refresh the paper-ready FinQA result tables after a manifest run:

```powershell
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa --output-dir paper/generated
```

The generated LaTeX table file is included from `paper/main.tex`, and the
matching Markdown summary is written to `paper/generated/finqa_results_summary.md`.

Run the current FinQA-300 local-planner pipeline from existing outputs:

```powershell
python scripts/run_pipeline.py
```

Refresh the FinQA-300 local-planner experiment outputs and then rebuild paper
assets. Use this command first on a clean checkout because `outputs/` is not
tracked by Git:

```powershell
python scripts/run_pipeline.py --refresh-results
```

The pipeline writes a reproducibility report to `outputs/pipeline/` and
paper-ready snippets to `paper/generated/`. Runtime outputs are ignored by Git;
promote only stable tables, reports, or release notes into tracked paper/docs
paths.

Run the no-API submission-suite gate from existing outputs:

```powershell
python scripts/run_pipeline.py --suite submission --skip-llm-direct-rag
```

Refresh all no-API submission-suite outputs from a clean checkout:

```powershell
python scripts/run_pipeline.py --suite submission --refresh-results --skip-llm-direct-rag
```

Check official AAAI page budget with a pdfLaTeX-capable TeX Live or MiKTeX
runtime:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement
```

The official `aaai2027.sty` rejects XeTeX/Tectonic, so this page-budget check
requires `pdflatex`, `bibtex`, `pdfinfo`, and `pdftotext` on the local machine.
On Windows, the current checked setup uses MiKTeX plus Strawberry Perl.

## Local Retrieval MVP-1

Build a local JSON index from files under `data/corpus`:

```powershell
python scripts/build_index.py --corpus data/corpus --output outputs/index/index.json
```

Run the same pipeline against that index:

```powershell
python scripts/run_query.py --method full_evigraph --corpus outputs/index/index.json --query "According to the chart, how much higher was 2023 than 2022?"
```

Run batch baselines against the same index:

```powershell
python scripts/run_batch_eval.py --questions data/questions.jsonl --corpus outputs/index/index.json --output outputs/eval/local_smoke.csv
```

Supported local corpus formats are `.txt`, `.md`, `.jsonl`, `.json`, `.csv`,
and `.pdf` when `pypdf` is installed.

## LLM Judge Scoring

The default scorer is rule-based so the repo runs without API keys. To enable an
OpenAI-compatible judge, set environment variables and change
`configs/default.yaml`:

```powershell
$env:LLM_PROVIDER="openai_compatible"
$env:LLM_BASE_URL="https://your-endpoint/v1"
$env:LLM_API_KEY="..."
$env:LLM_MODEL="your-chat-model"
```

```yaml
scoring:
  provider: hybrid
  llm_weight: 0.5
  llm_provider: openai_compatible
```

Use `provider: llm` for pure LLM judging, or `provider: hybrid` to blend LLM and
rule scores with automatic rule fallback.

## LLM Numeric Planner Fallback

The numeric answer path is rule-first by default. You can enable an
OpenAI-compatible planner that only proposes a structured operation plan; local
code still validates that all planned numeric values appear in the cited
context, then executes the calculation with `TableOperationExecutor`.

```yaml
numeric_planner:
  enabled: true
  llm_provider: openai_compatible
  llm_base_url: https://your-endpoint/v1
  llm_api_key: ...
  llm_model: your-chat-model
```

The planner is used only when the deterministic numeric reasoner cannot produce
an answer. Its supported operations are `difference`, `ratio`,
`percent_change`, `average`, and `sum`.

Run the dedicated FinQA planner manifest after setting the LLM environment:

```powershell
python scripts/check_llm_planner_ready.py
python scripts/run_manifest.py --manifest configs/experiments.finqa.planner.json
```

## Feasibility Check

Run the unit and smoke tests:

```powershell
python scripts/run_tests.py
```

Run the current end-to-end feasibility suite:

```powershell
python scripts/run_feasibility.py --corpus data/corpus --report outputs/eval/feasibility_report.json
```

The check verifies local index construction, misleading-evidence rejection,
grounded numeric support, calculation action triggering, and hybrid scorer
fallback.

For the local smoke corpus, the full EviGraph path should expose an action trace
like:

```text
PARSE_TABLE -> RUN_CALCULATION -> STOP -> VERIFY_CLAIM
```

This trace is intended to feed paper case studies and failure analysis.

Export any run directory as a case study:

```powershell
python scripts/export_case_study.py --run-dir outputs/runs/<run_id>
```
