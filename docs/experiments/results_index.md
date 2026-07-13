# Experiment Results Index

This index records the lightweight, Git-tracked evidence for the current
submission experiment closure. Raw evaluation CSVs remain under `outputs/eval`
and are intentionally ignored by Git to avoid committing large generated files.

## Closure Status

- Gate report: `docs/experiments/submission_closure_check.md`
- Closure definition: `docs/experiments/submission_closure.md`
- Long-term context: `docs/context/current_state.md`

## FinQA-600 Final Component Closure

- Manifest: `configs/experiments.finqa_600.submission_component_closure_v48.json`
- Local output directory:
  `outputs/eval/finqa_600_submission_component_closure_v48`
- Summary snapshot:
  `docs/experiments/snapshots/finqa_600_submission_component_closure_v48_summary.md`
- Statistical snapshot:
  `docs/experiments/snapshots/finqa_600_submission_component_closure_v48_statistics.md`

Headline Full EviGraph EM:

| Setting | EM |
| --- | ---: |
| Oracle-doc | 0.503 |
| Open BM25 | 0.377 |
| Source-rerank | 0.502 |

## TAT-QA-100 Method Closure

- Manifest: `configs/experiments.tatqa_100.submission_method_closure_v50.json`
- Local output directory:
  `outputs/eval/tatqa_100_submission_method_closure_v50`
- Summary snapshot:
  `docs/experiments/snapshots/tatqa_100_submission_method_closure_v50_summary.md`

Headline Full EviGraph EM:

| Setting | EM |
| --- | ---: |
| Oracle-doc | 0.520 |
| Open BM25 | 0.410 |

## Notes

- The deterministic local-planner closure is complete for the current claim
  boundary.
- FinQA-300 GPT-5.4 Direct RAG remains the API-backed LLM baseline. A FinQA-600
  LLM Direct RAG rerun is optional and budget-dependent.
- Source-rerank is an analysis setting, not a deployable open-retrieval claim.
