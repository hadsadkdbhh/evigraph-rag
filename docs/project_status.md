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
| Oracle-doc | 58/100 |
| Open BM25 | 50/100 |
| Open hybrid | 49/100 |
| BM25 + source rerank | 59/100 |

These numbers are diagnostic smoke results, not final benchmark claims.

## Main Bottleneck

The largest remaining failure classes are wrong numeric operation or row
selection and unresolved percent-style operations under open retrieval. Open
BM25 improved after retrieval-prior selection, ordered support extraction,
less brittle risk wording, stricter row grounding, retrieval-rank anchoring,
additional percent-change routing, year-label table fallback,
caption/header-aware row selection, prose/table percent-of-total normalization,
ordinary ratio execution over year-value tables, multi-column ratio selection,
weak prose-match rejection, adjacency chunks used as context-only support, and
cross-chunk continuation-table stitching for period-end rows. The deterministic
open hybrid reranker adds table, year, number, and operation overlap features,
but it remains slightly below open BM25 on exact match while improving some
verifier diagnostics. This indicates that the next push should focus on
row/operation intent and operand selection inside retrieved evidence rather than
simple lexical reranking.

The row/operation diagnostic now splits wrong numeric full EviGraph answers into
multi-label causes. On the current 100-example FinQA smoke subset, open hybrid
has 16 wrong numeric operation/row cases: 4 wrong-numerator signals, 3
wrong-denominator signals, 2 wrong-year-or-period signals, 3 wrong-row-label
signals, 1 wrong-operation-type signal, and 7 ambiguous supported wrong-number
cases. The highest-yield next engineering targets are operand selection for
ratio/percent-change calculations and reducing ambiguous supported wrong-number
cases with better operation intent tracing.
