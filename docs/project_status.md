# Project Status

Last updated from the checked-in FinQA MVP0 run.

## Current Stage

- Engineering pipeline: complete for MVP0 reproducibility.
- MVP0 experiment loop: complete for toy, stress, 100-example FinQA smoke, and a
  300-example FinQA validation-scale diagnostic run.
- FinQA-300 experiment loop: 100% complete as an artifact-closure workflow.
  This means dataset, manifest, three retrieval settings, failure reports,
  row/operation diagnostics, paper tables, experiment card, and closure report
  are all checked by `python scripts/run_pipeline.py`.
- FinQA-300 local-planner pipeline: closed as a one-command reproducibility
  path for tests, optional result refresh, diagnostics, and paper tables.
- Clean-checkout pipeline contract: documented in `README.md`; a fresh clone
  should run `python scripts/run_pipeline.py --refresh-results` first because
  `outputs/` is ignored by Git, while `python scripts/run_pipeline.py` is the
  quick path after generated CSVs exist.
- AAAI readiness: early research prototype; the system is not yet at submission-quality benchmark performance.
- Next phase goals are fixed in `docs/next_phase_goals.md`: raise Oracle-doc to
  `0.50+`, source-rerank to `0.45+`, and open BM25 to `0.35+`; add baselines
  and ablations; and rewrite the paper emphasis around operation planner,
  verifier, and evidence graph rather than rule patches.

## Reproducibility Gates

Run the current FinQA-300 local-planner pipeline without refreshing results:

```powershell
python scripts/run_pipeline.py
```

Run the full FinQA-300 refresh gate:

```powershell
python scripts/run_pipeline.py --refresh-results
```

The pipeline writes:

- `outputs/pipeline/pipeline_report.json`
- `outputs/pipeline/pipeline_report.md`
- `outputs/pipeline/pipeline_report_quick.md`
- `outputs/pipeline/pipeline_report_full_refresh.md`
- `outputs/pipeline/experiment_closure_report.md`
- `paper/generated/finqa_300_local_planner/finqa_results_summary.md`
- `paper/generated/finqa_300_local_planner/finqa_results_tables.tex`

The pipeline now starts with an internal preflight check. It verifies the
manifest, config, raw question file, corpus directory, and, for the quick path,
the presence of generated evaluation CSVs. If a clean checkout tries the quick
path first, it fails with an explicit instruction to run `--refresh-results`.
The pipeline now ends with an experiment-closure gate. That gate validates the
three 300-row evaluation CSVs, failure reports, row/operation diagnostics,
dataset inspection/gate artifacts, experiment card, and generated paper tables.

The 2026-06-25 full refresh passed all three stages: unit tests
(`203 tests OK`), FinQA-300 manifest, and paper-asset generation. The refreshed
FinQA-300 local-planner exact-match results are 0.420 oracle-doc, 0.333 open
BM25, and 0.387 BM25 plus source rerank.

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
full EviGraph it improves exact match from 0.297 to 0.317 under oracle-doc,
0.203 to 0.220 under open BM25, and 0.273 to 0.297 under BM25 plus
source-rerank. The larger movement is in calculation support: oracle-doc rises
from 0.373 to 0.497, open BM25 from 0.370 to 0.463, and source-rerank from
0.383 to 0.500. The latest refinements reduce source-rerank
wrong-operation-or-row diagnostics from 83 to 75, primary wrong-operation-type
cases from 43 to 38, wrong-numerator labels from 9 to 7, and ambiguous supported
wrong-number cases from 21 to 20. This is now the best reproducible
numeric-planner baseline in the repo.

The current code also includes a stricter local-planner guard for percent,
portion, share, and ratio questions. Questions phrased as "percent of DEN that
was NUM" are now planned as ratio programs, and erroneous `sum` plans are
rejected for ratio-like queries. This fixes the UNP 2008 accrued-wages ratio
case in open retrieval and reduces source-rerank wrong-operation-or-row
diagnostics from 75 to 71 on FinQA-300. The exact-match result is mixed:
oracle-doc is 0.313, open BM25 is 0.223, and source-rerank is 0.297. The next
highest-yield target remains wrong-operation-type and operand selection, not
more ad hoc arithmetic rules.

The newest operation-intent pass corrects local planner year direction for
`from BASE to TARGET` percent-change questions and prioritizes semantically
matched `respectively` prose evidence over weak table rows. This fixes examples
where the system reversed 2007-to-2008 decline calculations or used RSU share
counts instead of prose compensation-cost values. The current FinQA-300 local
planner numbers are 0.320 oracle-doc, 0.233 open BM25, and 0.300 source-rerank.
Source-rerank wrong-operation-or-row diagnostics are down to 66, with
wrong-operation-type labels down to 30. The next target is now narrower:
chunk-truncated ratio evidence and operand semantics for cases such as HTM
investment securities versus the investment securities portfolio.

The latest chunk-truncated ratio-evidence pass fixes that HTM investment
securities case by adding source-rerank adjacent chunks as explicit
context-only expansions instead of promoting them as normal retrieved evidence.
The support extractor now accepts neighbors expanded from the selected anchor
chunk, including duplicated retrieved nodes that share the same chunk id. The
numeric reasoner adds same-year row-ratio recovery for `in YEAR ... ratio of
NUM compared to DEN` questions and filters OCR year noise such as `2013end`
from row operands. On FinQA-300, the current local planner numbers are 0.323
oracle-doc, 0.247 open BM25, and 0.303 source-rerank. The repaired JPM example
now predicts `0.19` from `47733 / 247980`. The next target is operand semantics
inside wrong-operation-type and ambiguous-supported-wrong-number cases rather
than chunk availability.

The current wrong-operation-type pass makes that diagnostic more honest and
fixes a real percent-change routing gap. Explicit percent-like change questions
such as `percent of the change` and `percentual increase` now route to
percent-change programs instead of raw difference or sum fallbacks, and the
verifier/diagnostic stack maps `planned_*` calculation names back to their base
operation families. On FinQA-300, the current local planner numbers are 0.330
oracle-doc, 0.253 open BM25, and 0.310 source-rerank. Source-rerank
wrong-operation-type labels fall from 30 to 11. The AON 2009 risk-and-insurance
segment revenue case now predicts `1.7%` from `(6305 - 6197) / 6197 * 100`.
The next target is no longer broad operation type; it is the larger
ambiguous-supported-wrong-number bucket and concrete operand semantics inside
ratio/percent-change cases.

The current ambiguous-supported-wrong-number pass fixes one concrete waterfall
contribution pattern: `percent of the change between DEN in BASE and TARGET was
due to NUM`. The planner now treats the contribution row as a numerator delta
and divides it by the denominator row's target-base change, while the executor
can resolve year-qualified row labels in single-value waterfall tables. The ETR
2008 rider-revenue case now returns `18%` from `3.9 / (252.7 - 231) * 100`. On
FinQA-300, oracle-doc rises to 0.333 and open BM25 rises to 0.257; source-rerank
stays at 0.310. This is a quota-conscious semantic repair, not a broad
breakthrough.

The latest operand-selection pass adds two bounded fixes inside
ambiguous-supported-wrong-number. Compact average ranges such as `2011-2013`
now expand to all included years, and `paid in cash` acquisition questions bind
to local `cash paid of $X` prose instead of nearby purchase-price components.
The HOLX R2 cash-paid ratio now returns `3.1%`, and the APD 2011-2013 GAAP
capital-expenditure average now uses all three years. FinQA-300 moves to 0.340
oracle-doc, 0.260 open BM25, and 0.317 source-rerank; source-rerank
ambiguous-supported-wrong-number is down to 37.

The newest percent-change operand pass fixes the repeated IPG 2015
interest-income failures by reading `respectively` prose where values follow
the years. It also reports positive magnitude only for the narrow `what percent
decrease` phrasing, with an explicit `abs(...)` calculation for verifier
support. FinQA-300 is now 0.350 oracle-doc, 0.270 open BM25, and 0.327
source-rerank. Source-rerank ambiguous-supported-wrong-number is down to 35.

The current row-token operand-selection pass fixes a concrete substring
matching error inside `ambiguous_supported_wrong_number`: `tangible` was
previously allowed to match inside `intangible`, causing the GPN acquisition
case to select `customer-related intangible assets` instead of `total
identifiable net assets`. `TableOperationExecutor.select_best_row` now matches
row labels by normalized tokens with a light plural stemmer, preserving common
financial variants such as `liability`/`liabilities` without accepting
misleading substrings. FinQA-300 moves to 0.360 oracle-doc, 0.270 open BM25,
and 0.333 source-rerank. Source-rerank wrong-operation-or-row falls to 64, and
ambiguous-supported-wrong-number falls to 32.

The current entity-difference pass adds a narrow local-planner path for
questions of the form `difference in METRIC between ENTITY_A and ENTITY_B`.
These questions ask for an absolute entity-to-entity difference rather than a
year-over-year signed change. The ETR 2017 payments case now resolves the
shared `payments (receipts)` column for `entergy arkansas` and `entergy
louisiana`, returning `abs(2 - 6) = 4` instead of subtracting Arkansas from
itself. FinQA-300 stays at 0.360 oracle-doc and 0.333 source-rerank, while open
BM25 rises from 0.270 to 0.273. The source-rerank row/operation bucket remains
64, so the next target is still operand selection in
`ambiguous_supported_wrong_number`.

The current year-anchored average pass fixes a concrete `_row_values_average`
regression rather than adding a new arithmetic rule. `NumericReasoner._keywords`
strips every 20XX token, so two rows that differ only by year in the label
(for example `liability at december 31 2006` and `... 2008`) tied in
`_best_query_row` and the earlier row always won. The IPG 2008 restructuring
question therefore averaged the 2006 row plus its `total` column, returning
`519.4` instead of `(1.2 + 5.7 + 5.9) / 3 = 4.3`. `_row_values_average` now
prefers a semantically matched row whose label carries the query year, and it
excludes a `total` summary column from the average. This fixes the IPG 2008
example across oracle-doc, open BM25, and source-rerank. On FinQA-300, exact
match rises to 0.363 oracle-doc, 0.277 open BM25, and 0.337 source-rerank.
Source-rerank wrong-operation-or-row falls to 63, with wrong-year-or-period
falling to 8 and wrong-row-label falling to 10. The next target remains operand
selection inside the larger `ambiguous_supported_wrong_number` bucket, and the
broader lesson is that average-row selection should respect the year anchor the
query provides before falling back to lexical row matching.

The latest pass adds a period-end row preference for change queries. A change
query (`change`/`increased`/`decreased`/`growth`) over a table carrying both a
period-beginning and a period-end row for the same metric used to tie on
`_best_query_row` score, and the earlier (beginning) row won. The JPM 2007 MSR
fair-value question therefore compared `fair value at beginning of period`
(`(7546 - 6682) / 6682 = 12.9%`) instead of `fair value at december 31`
(`(8632 - 7546) / 7546 = 14.4%`). The new `_change_period_preference` helper
rewards the period-end row (`at december 31`, `ending balance`) and penalizes
the period-beginning row, but only as a tiebreaker between rows that already
lexically match the query. The lexical coverage gate is essential: an earlier
ungated version promoted an unrelated `net mw in operation at december 31` row
for an earnings query whose true value lives in prose, regressing ETR 2002 from
`57.0%` to `14.8%`. Gating on coverage preserves the prose fallback and removes
the regression. This fixed the JPM 2007 and APD 2018 change questions with no
real regressions (oracle-doc gains six cases, loses none on the change path).
On FinQA-300, exact match rises to 0.367 oracle-doc, 0.280 open BM25, and 0.340
source-rerank. Source-rerank wrong-operation-or-row falls to 62 and
ambiguous_supported_wrong_number falls to 31. The lesson reinforced here is that
intent-based row preferences must not bypass lexical coverage, or they promote
unrelated rows and suppress the correct planner fallback.

The newest ambiguous-supported-wrong-number pass handles one chunk-truncated
year-range average pattern. In the JPM 2018 AFS investment-securities case, the
selected chunk preserved the serialized row text
`afs investment securities (period-end) 228681 200247 236670`, but the Markdown
table fragment was truncated before that row and exposed only distracting rows
such as `investment securities gains/(losses)`. The numeric reasoner now
recovers multi-year averages from an inline row when all requested years resolve
to the same row label. The target example moves from `-113.667` to `221866.0`
across oracle-doc, open BM25, and source-rerank. On FinQA-300, exact match rises
to 0.373 oracle-doc, 0.283 open BM25, and 0.343 source-rerank. Source-rerank
wrong-operation-or-row falls to 61 and ambiguous_supported_wrong_number falls to
30. The next target remains denominator/year/row-label operand selection inside
the remaining ambiguous supported calculations.

The latest denominator/year/row-label pass attacks a concrete IP sales-ratio
cluster. Same-source chunks are grouped before the single-chunk prose fallback
for year-specific `sales` denominator questions, so a prose numerator can be
combined with the scoped segment `sales` table row. The scoped table resolver
also handles chunk-truncated year-only headers where the table label column has
been shifted out of the header. This fixes IP 2006 foodservice over consumer
packaging (`437 / 2245 = 19.5%`), IP 2007 European industrial packaging over
industrial packaging (`1100 / 5245 = 21.0%`), and preserves IP 2009 North
American consumer packaging over consumer packaging (`2500 / 3195 = 78.2%`).
On FinQA-300, exact match rises to 0.383 oracle-doc, 0.300 open BM25, and
0.353 source-rerank. Source-rerank wrong-operation-or-row falls to 58 and
ambiguous_supported_wrong_number falls to 29.

The latest wrong-operation-type pass fixes a total-denominator ratio planner
failure. For VRTX 2003, the query asks what percent of total common stock plans
are related to the Vertex purchase plan. The local planner previously stripped
`total` from the denominator selector, and the executor selected the same
purchase-plan row for numerator and denominator, producing `100%`. The planner
now preserves `total` for ratio denominators, and the table executor prefers a
total row when total is an explicit selector term. The target case now computes
`249 / 22203 = 1.1%`. On FinQA-300, exact match rises to 0.390 oracle-doc,
0.307 open BM25, and 0.360 source-rerank. Source-rerank
wrong-operation-or-row falls to 56 and wrong-operation-type falls to 12.

The newest wrong-operation-type pass handles year-row-to-thereafter ratios in
debt maturity schedules. The ETFC 2007 query asks for the ratio of future debt
maturities for 2011 to the amounts after 2012. The local planner now maps that
shape to a target-year row over a `thereafter` row, the reasoner tries this
planner path before generic ratio-between-years recovery, and the verifier
classifies non-percent `planned_ratio` traces as plain ratios. The target case
now computes `453815 / 2996337 = 0.2`. On FinQA-300, exact match rises to 0.393
oracle-doc, 0.310 open BM25, and 0.363 source-rerank. Source-rerank
wrong-operation-or-row falls to 55 and wrong-operation-type falls to 11.

The latest denominator-selection pass extends the existing same-row column
ratio mechanism to named table columns. For BLK 2012, the query asks for
long-term retail/HNW in the Americas as a percentage of total long-term
retail/HNW. The system now selects the same `long-term retail/hnw` row,
`americas` as the numerator column, and `total` as the denominator column,
computing `298024 / 403484 = 73.9%` instead of using unrelated prose inflows as
the denominator. On FinQA-300, oracle-doc rises to 0.397, while open BM25 stays
0.310 and source-rerank stays 0.363. Oracle wrong-operation-or-row falls to 48
and oracle wrong-denominator falls to 2.

The next wrong-operation-type pass adds a narrow acquisition liability-to-asset
operation. For DRE 2007, the query asks for the ratio of debts to assets in a
purchase transaction; the correct operation combines `debt assumed` and `other
liabilities assumed`, then divides by `total assets acquired`. The system now
computes `(148527 + 5829) / 867558 * 100 = 17.8%` instead of selecting a noisy
single denominator row. On FinQA-300, oracle-doc rises to 0.400 and
source-rerank rises to 0.367, while open BM25 stays 0.310. Oracle
wrong-operation-or-row falls to 47; source-rerank wrong-operation-or-row falls
to 54 and source-rerank wrong-operation-type falls to 10.

The next operation-type pass handles `increase in X as a percentage of Y in
YEAR` questions where the numerator is a prose-supported sum of increase
components and the denominator is a year-labeled table row. For ETR 2004, the
system now sums the `other regulatory credits` increase components
(`14.3 + 11.8 + 11.4`) and divides by `2003 net revenue` (`973.7`), yielding
`3.9%` for the gold `3.85%`. On FinQA-300, oracle-doc rises to 0.403 and
source-rerank rises to 0.370, while open BM25 stays 0.310 because the open
retrieval setting still selects a misleading context for this example. Oracle
wrong-operation-or-row falls to 46; source-rerank wrong-operation-or-row falls
to 53 and source-rerank wrong-operation-type falls to 9.

The follow-up open-retrieval pass keeps the same operation but lets it combine
same-source chunks only after single-context evidence fails. This fixes the open
BM25 ETR 2004 case where the numerator prose and denominator table were
retrieved as adjacent chunks rather than as a full source context. Open BM25
rises to 0.313 without reducing oracle-doc or source-rerank, which remain 0.403
and 0.370.

The next open-retrieval split-chunk pass adds grouped prose-ratio support for
explicit `paid in cash` over `purchase price` questions. It fixes the HOLX 2007
case where the same-source evidence separately contained cash paid (`$6900`)
and estimated purchase price (`$220600`), moving the open answer from `100%` to
`3.1%`. Open BM25 rises to 0.317 without reducing oracle-doc or source-rerank,
which remain 0.403 and 0.370.

The latest shared-failure pass repairs ROI extraction from chunk-truncated
cumulative-return tables. The ROI path now inherits a previous year-header block
across adjacent parsed table blocks and retries same-source grouped chunks after
single-context failure. This fixes AAP 2011 S&P 500 ROI (`65.70` vs `100.00`,
or `-34.3%`) across oracle-doc, open BM25, and source-rerank. FinQA-300 rises to
0.407 oracle-doc, 0.320 open BM25, and 0.373 source-rerank.

The facilities square-footage pass adds targeted operand mapping for explicit
`major facilities by square footage are owned/leased` questions: owned or
leased facilities become the numerator and total facilities becomes the
denominator. This fixes both INTC 2013 owned and leased facility-share examples
across oracle-doc, open BM25, and source-rerank. FinQA-300 rises to 0.413
oracle-doc, 0.327 open BM25, and 0.380 source-rerank.

The prose/table ratio pass handles two shared failures without adding broad
rules: ETFC 2013 not-leased Alpharetta square footage uses the prose exception
as numerator and the exact Alpharetta table row as denominator, while ABMD 2006
office-facility closing uses the prose lease-expense sequence for fiscal 2006
instead of the future-minimum-lease-payments table. FinQA-300 rises to 0.420
oracle-doc, 0.333 open BM25, and 0.387 source-rerank.
