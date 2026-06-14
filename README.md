# EviGraph-RAG

Utility-Risk Evidence State Control for Multimodal RAG.

Core claim: retrieved information is not evidence. This project treats retrieval
outputs as candidate evidence states, scores their utility and risks, selects a
minimal reliable support subgraph, and generates grounded answers from that
subgraph only.

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

Convert external benchmark files into the internal JSONL question format:

```powershell
python scripts/convert_dataset.py --input data/raw/mock_external.jsonl --output outputs/eval/converted_questions.jsonl --dataset-name mock_report
```

Manifests may also set `raw_questions` and `field_map` to run this conversion
automatically before evaluation.

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

Before reporting real benchmark numbers, follow the protocol in
`docs/benchmark_protocol.md`. A ChartQA-style manifest template is available at
`configs/experiments.chartqa.example.json`; populate `data/raw/chartqa_subset.jsonl`
and `data/chartqa_corpus` before running it.

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
