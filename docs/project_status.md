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
| Oracle-doc | 49/100 |
| Open BM25 | 44/100 |
| BM25 + source rerank | 49/100 |

These numbers are diagnostic smoke results, not final benchmark claims.

## Main Bottleneck

The largest remaining failure classes are wrong numeric operation or row
selection and unresolved percent-style operations under open retrieval. Open
BM25 improved after retrieval-prior selection, ordered support extraction,
less brittle risk wording, stricter row grounding, retrieval-rank anchoring,
additional percent-change routing, year-label table fallback, and
caption/header-aware row selection; it now slightly exceeds the current top-k
smoke baseline, so the next push should focus on operation planning and row
grounding for the retrieved evidence.
