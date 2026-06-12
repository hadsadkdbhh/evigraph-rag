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
