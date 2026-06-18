# Project Status

Last updated from the checked-in FinQA MVP0 run.

## Current Stage

- Engineering pipeline: complete for MVP0 reproducibility.
- MVP0 experiment loop: complete for toy, stress, and 100-example FinQA smoke runs.
- AAAI readiness: early research prototype; the system is not yet at submission-quality benchmark performance.

## Reproducibility Gates

Run the quick MVP0 acceptance suite:

```powershell
python scripts/run_mvp0_acceptance.py
```

Run the full MVP0 suite including the 100-example FinQA real subset:

```powershell
python scripts/run_mvp0_acceptance.py --with-finqa
```

The acceptance script writes:

- `outputs/eval/mvp0_acceptance/acceptance_report.json`
- `outputs/eval/mvp0_acceptance/acceptance_report.md`

## Latest FinQA Smoke Metrics

The current checked-in FinQA validation subset uses 100 examples, seed 13, and
records `source_doc` for oracle-document and source-rerank evaluation.

| setting | full EviGraph exact match |
| --- | ---: |
| Oracle-doc | 43/100 |
| Open BM25 | 18/100 |
| BM25 + source rerank | 38/100 |

These numbers are diagnostic smoke results, not final benchmark claims.

## Main Bottleneck

The largest remaining failure class is percent-style numeric questions. The
open-retrieval setting is much weaker than oracle-doc and source-rerank, so the
next research/engineering push should focus on retrieval, chunking, and support
graph construction before adding more numeric rules.
