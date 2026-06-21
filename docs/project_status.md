# Project Status

Last updated from the checked-in FinQA MVP0 run.

## Current Stage

- Engineering pipeline: complete for MVP0 reproducibility.
- MVP0 experiment loop: complete for toy, stress, 100-example FinQA smoke, and a
  300-example FinQA validation-scale diagnostic run.
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
| Oracle-doc | 63/100 |
| Open BM25 | 55/100 |
| Open hybrid | 54/100 |
| BM25 + source rerank | 64/100 |

These numbers are diagnostic smoke results, not final benchmark claims.

The 300-example validation-scale run is now checked in as a reproducibility
asset and documented in `docs/finqa_300_status.md`. It is a harder reality
check than the 100-example smoke run:

| setting | full EviGraph exact match |
| --- | ---: |
| Oracle-doc | 89/300 |
| Open BM25 | 61/300 |
| Open hybrid | 63/300 |
| BM25 + source rerank | 82/300 |

These 300-example numbers should be treated as diagnostic engineering evidence,
not as the final paper claim. They show that support diagnostics are much
stronger than raw exact match, and that the main unsolved issue is still
operation and operand selection under realistic table variation.

## Main Bottleneck

The largest remaining failure classes are wrong numeric operation or row
selection and unresolved percent-style operations under open retrieval. Open
BM25 improved after retrieval-prior selection, ordered support extraction,
less brittle risk wording, stricter row grounding, retrieval-rank anchoring,
additional percent-change routing, year-label table fallback,
caption/header-aware row selection, prose/table percent-of-total normalization,
ordinary ratio execution over year-value tables, multi-column ratio selection,
weak prose-match rejection, adjacency chunks used as context-only support, and
cross-chunk continuation-table stitching for period-end rows. The latest
operation-intent pass also handles relative row differences such as "percent
higher than" and percentage-point row differences such as "X as a percentage of
Y between years." The current numeric path now also scores year-label
percent-change candidates across contexts, which helps fiscal schedules such as
estimated amortization expense, and combines same-source table/prose evidence for
total-denominator ratios such as segment operating income over total operating
income. The current numeric path also supports horizontal and vertical
maturity/payment schedule ratios, such as thereafter-over-total obligations. The
deterministic open hybrid reranker adds table, year, number, and
operation overlap features, but it remains slightly below open BM25 on exact
match while improving some verifier diagnostics. This indicates that the next
push should focus on row/operation intent and operand selection inside retrieved
evidence rather than simple lexical reranking.

The row/operation diagnostic now splits wrong numeric full EviGraph answers into
multi-label causes. On the current 100-example FinQA smoke subset, open hybrid
has 13 wrong numeric operation/row cases: 3 wrong-numerator signals, 2
wrong-denominator signals, 2 wrong-year-or-period signals, 2 wrong-row-label
signals, 0 wrong-operation-type signals, and 6 ambiguous supported wrong-number
cases. The highest-yield next engineering targets are numerator/denominator
selection for ratio and percent-change calculations, especially cases such as
ADI mutual-fund allocation, LKQ rental-expense period selection, GS commodities
base-year selection, IP denominator selection, and AMT twelve-month versus
three-month period intent.

The numeric planner fallback has moved one step closer to a program-style
executor: an LLM plan may now identify table cells by row label plus year/column
selector, while the local executor parses the markdown table, retrieves the
evidence value, executes `difference`, `ratio`, `percent_change`,
`percent_of_increase`, `sum`, `average`, or `product`, and records the resolved
row/column references in the calculation trace. Percent-of-increase questions
are routed to this planner path before the older ratio-percent heuristic, which
prevents the system from answering with a current-value ratio when the question
asks for contribution to a period-over-period increase. This is the intended
path for future failure-driven fixes because it separates operation planning
from locally auditable arithmetic.

The table-cell resolver now also accepts period selectors such as `three months
ended`, `six months ended`, `nine months ended`, and `twelve months ended`.
Period selectors are used in column matching and row matching, so planner
programs can avoid confusing a quarterly column with a year-to-date or annual
column when the same fiscal year appears multiple times.

The 300-example LLM-planner manifest is available at
`configs/experiments.finqa_300.planner.json`. To run it from PowerShell, first
set the LLM environment variables, then run:

```powershell
python .\scripts\check_llm_planner_ready.py
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.planner.json
```

The manifest writes to `outputs/eval/finqa_300_planner` and should be compared
against the non-planner 300-example run in `outputs/eval/finqa_300`.

The first FinQA-300 planner run completed and is summarized in
`docs/finqa_300_planner_status.md`. Because the configured CC Switch `lucen`
provider failed as an LLM backend, the run used the local heuristic fallback.
It did not improve exact match, but it raised calculation-support diagnostics by
about three points across oracle-doc, open BM25, and source-rerank settings.
Treat this as a negative diagnostic and infrastructure validation, not as an
LLM-planner result.

A stronger fully local program planner is now available through
`configs/default_local_planner.yaml` and
`configs/experiments.finqa_300.local_planner.json`. It avoids external API
dependencies and supports ratio-percent, ordinary ratio, difference, lookup,
sum, average, product, percent-of-increase, period-aware percent change,
same-row `due after` ratios, and complement-percent operations. On FinQA-300
full EviGraph it improves exact match from 0.297 to 0.313 under oracle-doc,
0.203 to 0.217 under open BM25, and 0.273 to 0.293 under BM25 plus
source-rerank. The larger movement is in calculation support: oracle-doc rises
from 0.373 to 0.497, open BM25 from 0.370 to 0.463, and source-rerank from
0.383 to 0.500. The latest refinements reduce source-rerank
wrong-operation-or-row diagnostics from 83 to 76, primary wrong-operation-type
cases from 43 to 38, and wrong-numerator labels from 9 to 7. This is now the
best reproducible numeric-planner baseline in the repo.
