# FinQA 600-Example Validation Status

This note records the stronger FinQA validation-scale subset added after the
FinQA-300 artifact loop was closed. It is intended to test whether the current
mechanism story survives a larger diagnostic sample.

## Dataset

- Source dataset: `dreamerdeo/finqa`
- Split: `validation`
- Pool size: 1000 rows fetched through the Hugging Face rows API
- Sample size: 600 answerable examples
- Seed: `13`
- Raw records: `data/raw/finqa_600_subset.jsonl`
- Corpus directory: `data/finqa_600_corpus`
- Local-planner manifest: `configs/experiments.finqa_600.local_planner.json`
- LLM Direct RAG manifest: `configs/experiments.finqa_600.llm_direct_rag.json`

The downloader filters out rows with missing answers before sampling. The raw
file and corpus are checked into the repository so later runs do not depend on
the Hugging Face rows API.

## Reproduction Commands

```powershell
python .\scripts\download_finqa_subset.py --split validation --pool-size 1000 --sample-size 600 --seed 13 --raw-output data/raw/finqa_600_subset.jsonl --corpus-output data/finqa_600_corpus --clean-corpus
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.local_planner.json
```

Run the LLM Direct RAG baseline only after setting a named
OpenAI-compatible model:

```powershell
$env:LLM_PROVIDER="openai_compatible"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_API_KEY="YOUR_KEY"
$env:LLM_MODEL="YOUR_MODEL"
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.llm_direct_rag.json
```

## Current Status

The dataset, manifests, local-planner run, failure reports, row/operation
diagnostics, experiment card, and paper-table artifacts are wired.
The LLM Direct RAG baseline still needs a configured API model.

## Local Planner Results

| setting | full EviGraph EM | answer supported | calculation supported | row grounded |
| --- | ---: | ---: | ---: | ---: |
| Oracle-doc | 0.403 | 0.780 | 0.543 | 0.808 |
| Open BM25 | 0.295 | 0.732 | 0.468 | 0.752 |
| BM25 + source-rerank | 0.400 | 0.780 | 0.543 | 0.808 |

These numbers are lower than FinQA-300, so the larger subset is a better
stress test for paper claims. The main remaining problem remains operand and
operation selection rather than citation availability.

## Failure Profile

Full EviGraph failure categories:

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 116 | 60 | 86 | 57 | 35 | 4 |
| Open BM25 | 126 | 68 | 104 | 64 | 43 | 18 |
| BM25 + source-rerank | 115 | 62 | 86 | 58 | 35 | 4 |

Row/operation diagnostics:

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 19 | 11 | 10 | 8 | 28 | 52 |
| Open BM25 | 18 | 15 | 12 | 20 | 23 | 61 |
| BM25 + source-rerank | 18 | 11 | 10 | 7 | 27 | 53 |

## Artifacts

- Results: `outputs/eval/finqa_600_local_planner/summary.md`
- Failure reports: `outputs/eval/finqa_600_local_planner/*_failures.md`
- Row/operation diagnostics: `outputs/eval/finqa_600_local_planner/*_row_operation_diagnostics.md`
- Paper assets: `paper/generated/finqa_600_local_planner/`
