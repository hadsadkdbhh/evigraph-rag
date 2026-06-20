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
| Oracle-doc | 56/100 |
| Open BM25 | 47/100 |
| Open hybrid | 47/100 |
| BM25 + source rerank | 56/100 |

These numbers are diagnostic smoke results, not final benchmark claims.

## Main Bottleneck

The largest remaining failure classes are wrong numeric operation or row
selection and unresolved percent-style operations under open retrieval. Open
BM25 improved after retrieval-prior selection, ordered support extraction,
less brittle risk wording, stricter row grounding, retrieval-rank anchoring,
additional percent-change routing, year-label table fallback, and
caption/header-aware row selection, prose/table percent-of-total normalization,
ordinary ratio execution over year-value tables, multi-column ratio selection,
weak prose-match rejection, and adjacency chunks used as context-only support.
The deterministic open hybrid reranker adds table, year, number, and operation
overlap features, but it currently ties open BM25 on exact match at 47/100 while
slightly improving verifier diagnostics. This indicates that the next push
should focus on row/operation selection errors and unresolved percent operations
inside retrieved evidence rather than simple lexical reranking.

The row/operation diagnostic now splits wrong numeric full EviGraph answers into
multi-label causes. On the current 100-example FinQA smoke subset, open hybrid
has 19 wrong numeric operation/row cases: 6 wrong-numerator signals, 5
wrong-denominator signals, 2 wrong-year-or-period signals, 3 wrong-row-label
signals, 1 wrong-operation-type signal, and 7 ambiguous supported wrong-number
cases. The highest-yield next engineering target is therefore operand selection
for ratio/percent-change calculations, followed by reducing ambiguous supported
wrong-number cases with better operation intent tracing.
