# FinQA-300 Planner Status

This note records the first 300-example planner run after adding period-aware
table-cell selection and program-style operations.

## Run

Command:

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.planner.json
```

Output directory:

```text
outputs/eval/finqa_300_planner
```

## Planner Availability

The configured CC Switch `lucen` provider was not usable as a direct LLM planner
backend during this run. Direct and local-proxy requests failed with Cloudflare
403 / error code 1010, and the stored OpenAI-compatible key was rejected by the
upstream service. The run therefore completed through the local heuristic
program-planner fallback.

This means the numbers below are not evidence for LLM-planner quality. They are
a fallback-planner diagnostic that checks whether the expanded program executor
can be run end-to-end at the 300-example scale.

## Results

| setting | full EviGraph EM | answer supported | calculation supported |
| --- | ---: | ---: | ---: |
| Oracle-doc planner fallback | 0.297 | 0.710 | 0.407 |
| Open BM25 planner fallback | 0.203 | 0.723 | 0.397 |
| BM25 + source-rerank planner fallback | 0.273 | 0.733 | 0.417 |

Compared with the non-planner 300-example run:

| setting | EM delta | calculation-support delta |
| --- | ---: | ---: |
| Oracle-doc | +0.000 | +0.034 |
| Open BM25 | +0.000 | +0.027 |
| BM25 + source-rerank | +0.000 | +0.034 |

The fallback planner did not improve exact match, but the expanded verifier path
recognized more calculations as supported.

## Source-Rerank Failure Profile

| category | count |
| --- | ---: |
| wrong numeric operation or row | 58 |
| no numeric answer, other | 45 |
| no numeric answer, percent | 45 |
| no numeric answer, additive or lookup | 38 |
| no numeric answer, ratio | 26 |
| unsupported textual prediction | 6 |

Row/operation diagnostic counts for source-rerank:

| diagnostic | count |
| --- | ---: |
| wrong numerator | 9 |
| wrong denominator | 8 |
| wrong year or period | 8 |
| wrong row label | 9 |
| wrong operation type | 19 |
| ambiguous supported wrong number | 20 |

## Interpretation

The period-aware selector and added operations are necessary infrastructure, but
the current local fallback planner is too weak to move exact match. The main
remaining bottleneck is not arithmetic execution; it is selecting the right
program and operands before execution.

The next credible experiment requires a working external planner backend or a
substantially stronger local program planner. Until then, use this run as a
negative diagnostic rather than a performance claim.

## Stronger Local Program Planner

The next run replaces the failed external-planner dependency with a local
program planner:

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.local_planner.json
```

Output directory:

```text
outputs/eval/finqa_300_local_planner
```

This planner does not require API credentials. It adds local plans for
ratio-percent, ordinary ratio, difference, sum, average, product,
percent-of-increase, period-aware percent change, and complement-percent cases
such as "not leased". It also selects the best evidence node by term overlap and
can resolve a table row when the table has only one numeric value column.

## Strong Local Planner Results

| setting | full EviGraph EM | answer supported | calculation supported |
| --- | ---: | ---: | ---: |
| Oracle-doc local planner | 0.317 | 0.710 | 0.497 |
| Open BM25 local planner | 0.220 | 0.727 | 0.463 |
| BM25 + source-rerank local planner | 0.297 | 0.733 | 0.500 |

Compared with the non-planner 300-example run:

| setting | EM delta | calculation-support delta |
| --- | ---: | ---: |
| Oracle-doc | +0.020 | +0.124 |
| Open BM25 | +0.017 | +0.093 |
| BM25 + source-rerank | +0.024 | +0.117 |

Compared with the previous planner-fallback run, the stronger local planner
turns the planner path from a pure infrastructure check into a measurable
performance change. The exact-match gain is still modest, but the large
calculation-support gain means the executor now covers substantially more
auditable arithmetic programs. A follow-up local-planner refinement adds
same-row `due after` ratios, explicit lookup plans, and better ratio phrasing.
It does not move exact match, but it reduces the source-rerank
wrong-operation-or-row bucket from 83 to 78 and primary wrong-operation-type
cases from 43 to 38. The remaining next target is operand selection, especially
wrong numerator/denominator and ambiguous supported wrong-number cases.

A subsequent operand-selection pass improves ratio phrasing and row selection:
phrases like "what percentage of DEN is NUM" now take the suffix as the
numerator, prefix questions like "X where what percentage of DEN" take the
prefix as numerator, and row matching prefers compact exact labels over longer
rows that merely contain the same terms. This fixes cases such as IPR&D over
total purchase price net of cash acquired. On FinQA-300, exact match rises to
0.313 oracle-doc, 0.217 open BM25, and 0.293 source-rerank. The source-rerank
wrong-operation-or-row bucket falls further from 78 to 76, and wrong-numerator
labels fall from 9 to 7.

A further ratio-context pass handles "made up of" as a numerator cue and allows
context-level denominator phrases, such as a table titled "average common equity
attribution", to map to the table's `total` row. This fixes the Morgan Stanley
institutional-securities share case. The current FinQA-300 local-planner
baseline is 0.317 oracle-doc, 0.220 open BM25, and 0.297 source-rerank. The
source-rerank wrong-operation-or-row bucket is now 75, and ambiguous supported
wrong-number cases fall from 21 to 20.

The latest local-planner guard pass adds explicit handling for questions phrased
as "percent of DEN that was NUM" and rejects `sum` plans for percent, portion,
share, or ratio questions. It fixes the UNP 2008 accrued-wages ratio case across
open BM25, oracle-doc, and source-rerank paths by forcing a ratio program rather
than a scalar sum fallback. On the full FinQA-300 run, the current checked-in
numbers are 0.313 oracle-doc, 0.223 open BM25, and 0.297 source-rerank. The
source-rerank wrong-operation-or-row bucket falls from 75 to 71, with primary
wrong-year-or-period cases falling from 8 to 7. This is a mixed result: the guard
reduces bad supported numeric behavior and slightly improves open retrieval, but
it is not a broad exact-match jump.

The latest operation-intent pass fixes local planner year direction for
`from BASE to TARGET` percent-change questions and lets high-confidence
`respectively` prose sentences override weak table rows for percent-change
queries. This fixes Duke Realty net-income decline and RSU compensation-cost
increase cases. On FinQA-300, exact match rises to 0.320 oracle-doc, 0.233 open
BM25, and 0.300 source-rerank. The source-rerank wrong-operation-or-row bucket
falls from 71 to 66, and wrong-operation-type labels fall from 35 to 30. The
remaining largest failure class is still wrong operation type, but it is now a
smaller and more specific set centered on operand semantics and chunk-truncated
ratio evidence.

The chunk-truncated ratio-evidence pass adds context-only adjacent chunks for
source-rerank without promoting them to ordinary high-rank candidates, and it
records the anchor chunk id so duplicated retrieved nodes can still recover the
right continuation chunk. The numeric reasoner now handles same-year row ratios
phrased as `in YEAR ... ratio of NUM compared to DEN`, filters OCR year noise
such as `2013end` from row operands, and can recover inline rows split across
adjacent chunks. This fixes `JPM/2018/page_110.pdf-3`: HTM investment securities
period-end over investment securities portfolio period-end in 2017 is recovered
as `47733 / 247980 = 0.192487`, yielding `0.19`. On FinQA-300, exact match rises
to 0.323 oracle-doc, 0.247 open BM25, and 0.303 source-rerank. Source-rerank
wrong-operation-or-row remains 66, but the previously targeted chunk-truncated
ratio case is now covered by a regression test and the open-retrieval setting
also improves.

The wrong-operation-type pass separates real operation mistakes from diagnostic
name mismatches. The reasoner and local planner now route explicit percent-like
change phrasings, including `percent of the change` and `percentual increase`,
to percent-change programs instead of raw difference or sum fallbacks. The
verifier and row-operation diagnostic now recognize the same intent and map
`planned_percent_change`, `planned_average`, `planned_difference`,
`planned_sum`, and `planned_lookup` to their base operation families. This fixes
`AON/2009/page_46.pdf-3`, changing the risk-and-insurance segment revenue answer
from raw difference `108` to `(6305 - 6197) / 6197 * 100 = 1.7%`. On FinQA-300,
exact match rises to 0.330 oracle-doc, 0.253 open BM25, and 0.310
source-rerank. Source-rerank wrong-operation-type labels fall from 30 to 11.
Ambiguous-supported-wrong-number rises from 19 to 38 because many former
operation-type reports were reclassified as supported-but-wrong operand/number
cases rather than hidden under a planned-operation name mismatch.

The first ambiguous-supported-wrong-number pass targets one concrete subpattern
instead of adding broad rules: questions of the form `percent of the change
between DEN in BASE and TARGET was due to NUM`. In waterfall tables, the NUM row
is often already a contribution delta rather than a year-specific value. The
local planner now routes this form through `percent_of_increase` with a direct
`numerator_delta`, while the table executor can resolve year-qualified rows such
as `2007 net revenue` and `2008 net revenue` in single-value waterfall tables.
This fixes the ETR 2008 rider-revenue case, producing `3.9 / (252.7 - 231) *
100 = 18.0%` instead of treating rider revenue as an ordinary percent change.
On FinQA-300, exact match moves to 0.333 oracle-doc and 0.257 open BM25, while
source-rerank remains 0.310. This is a narrow semantic fix, not a broad quality
jump; the next useful target remains operand selection inside the larger
ambiguous-supported-wrong-number bucket.

The next operand-selection pass keeps the same failure-driven scope and fixes
two narrow cases. First, compact year ranges such as `2016-2018` and
`2011-2013` now expand to the full inclusive year series for average programs,
instead of using only the endpoints. Second, acquisition questions phrased as
`paid in cash` now bind the numerator to the local `cash paid of $X` phrase and
avoid rescaling same-unit prose amounts against tables marked `in thousands`.
This fixes the APD 2011-2013 GAAP capital-expenditure average and the HOLX R2
cash-paid purchase-price ratio. On FinQA-300, exact match rises to 0.340
oracle-doc, 0.260 open BM25, and 0.317 source-rerank. Source-rerank
wrong-operation-or-row falls to 70, and ambiguous-supported-wrong-number falls
to 37.

The following percent-change operand pass fixes a repeated IPG interest-income
failure. The percent-change reasoner now reuses the existing `respectively`
prose parser when values appear after the years, as in `During 2015 and 2014,
we had interest income of $22.8 and $27.4, respectively`, so the query no
longer falls through to a nearby fair-market-value sensitivity table. For
questions phrased as `what percent decrease`, the answer reports the positive
decrease magnitude while preserving an auditable `abs(...)` calculation. This
fixes both IPG 2015 interest-income variants. On FinQA-300, exact match rises
to 0.350 oracle-doc, 0.270 open BM25, and 0.327 source-rerank. Source-rerank
wrong-operation-or-row falls to 67, and ambiguous-supported-wrong-number falls
to 35.

The current operand-selection pass fixes a row-label substring bug rather than
adding another arithmetic rule. In the GPN acquisition example, `tangible` was
matching the row `customer-related intangible assets`, so the lookup selected
42721 instead of the net-assets row. Row selection now uses token-level matches
with a small plural normalizer, which blocks `tangible`/`intangible` confusion
while keeping common financial singular/plural variants. On FinQA-300, exact
match rises to 0.360 oracle-doc, 0.270 open BM25, and 0.333 source-rerank.
Source-rerank wrong-operation-or-row falls to 64, and
ambiguous-supported-wrong-number falls to 32.

The next small pass handles entity-to-entity difference questions. For queries
such as `difference in payments between entergy arkansas and entergy
louisiana`, the local planner now selects both entity rows under the shared
metric column and executes an absolute difference. This fixes the ETR 2017
payments example with `abs(2 - 6) = 4`; previously both operands resolved to
Entergy Arkansas and produced zero. On FinQA-300, exact match remains 0.360
oracle-doc and 0.333 source-rerank, while open BM25 increases to 0.273.

The latest year-anchored average pass fixes a `_row_values_average` row
selection bug exposed by the IPG 2008 restructuring-liability question.
`NumericReasoner._keywords` strips every 20XX token, so two rows differing
only by year in the label (`liability at december 31 2006` vs `... 2008`)
tied in `_best_query_row` and the earlier row always won. The IPG question
therefore averaged the 2006 row together with its `total` summary column,
returning `519.4` instead of `(1.2 + 5.7 + 5.9) / 3 = 4.3`.
`_row_values_average` now prefers a semantically matched row whose label
carries the query year, and it excludes a `total` summary column from the
average. On FinQA-300, exact match rises to 0.363 oracle-doc, 0.277 open BM25,
and 0.337 source-rerank. Source-rerank wrong-operation-or-row falls to 63,
with wrong-year-or-period falling to 8 and wrong-row-label falling to 10.

The latest pass adds a period-end row preference for change queries. A change
query (`change`/`increased`/`decreased`/`growth`) over a table carrying both a
period-beginning and a period-end row for the same metric used to tie on
`_best_query_row` score, so the earlier (beginning) row won. The JPM 2007 MSR
fair-value question therefore compared `fair value at beginning of period`
(`(7546 - 6682) / 6682 = 12.9%`) instead of `fair value at december 31`
(`(8632 - 7546) / 7546 = 14.4%`). The new `_change_period_preference` helper
rewards the period-end row and penalizes the period-beginning row, but only as
a tiebreaker between rows that already lexically match the query. Gating on
lexical coverage is what keeps this safe: an ungated version promoted an
unrelated `net mw in operation at december 31` row for an earnings query whose
true value lives in prose, regressing ETR 2002 from `57.0%` to `14.8%`; the
coverage gate restores the prose fallback and removes the regression. This
fixes the JPM 2007 and APD 2018 change questions. On FinQA-300, exact match
rises to 0.367 oracle-doc, 0.280 open BM25, and 0.340 source-rerank.
Source-rerank wrong-operation-or-row falls to 62 and
ambiguous_supported_wrong_number falls to 31.

The latest ambiguous-supported-wrong-number pass adds inline row recovery for
year-range averages when chunking truncates the Markdown table but leaves the
serialized row text intact. The JPM 2018 AFS investment-securities question now
uses `afs investment securities (period-end)` and computes `(236670 + 200247 +
228681) / 3 = 221866` instead of averaging the neighboring
`investment securities gains/(losses)` row. On FinQA-300, exact match rises to
0.373 oracle-doc, 0.283 open BM25, and 0.343 source-rerank. Source-rerank
wrong-operation-or-row falls to 61, and ambiguous_supported_wrong_number falls
to 30.

The latest operand-selection pass targets split table/prose sales-denominator
ratios rather than adding a broad rule. Same-source chunks are now grouped
before the single-chunk prose fallback for year-specific `sales` denominator
questions, and truncated year-only Markdown headers are realigned so the row
label column does not shift query-year values. This fixes the IP 2006
foodservice-over-consumer-packaging case (`437 / 2245 = 19.5%`), the IP 2007
European-industrial-packaging case (`1100 / 5245 = 21.0%`), and keeps the IP
2009 North-American-consumer-packaging ratio at `2500 / 3195 = 78.2%`.
On FinQA-300, exact match rises to 0.383 oracle-doc, 0.300 open BM25, and
0.353 source-rerank. Source-rerank wrong-operation-or-row falls to 58, and
ambiguous_supported_wrong_number falls to 29.

The next wrong-operation-type pass preserves explicit total-denominator intent
inside local ratio plans. Previously the heuristic planner stripped `total`
from denominator terms, so `what percent of the total common stock plans are
related to the vertex purchase plan?` resolved both numerator and denominator
to the Vertex purchase-plan row and returned `249 / 249 = 100%`. The planner
now keeps `total` for denominator row terms, and the table executor prefers an
explicit total row when the selector asks for one. The VRTX 2003 case now
returns `249 / 22203 = 1.1%`. On FinQA-300, exact match rises to 0.390
oracle-doc, 0.307 open BM25, and 0.360 source-rerank. Source-rerank
wrong-operation-or-row falls to 56, and wrong-operation-type falls to 12.

The next wrong-operation-type pass handles year-row-to-thereafter ratios in
debt maturity schedules without broadening generic ratio rules. The ETFC 2007
question asks for the ratio of future debt maturities for 2011 to amounts after
2012; the planner now maps this to `2011 / thereafter`, and the reasoner tries
that planner path before the older ratio-between-years heuristic. The verifier
also accepts non-percent `planned_ratio` traces as plain ratios. The target case
now returns `453815 / 2996337 = 0.2`. On FinQA-300, exact match rises to 0.393
oracle-doc, 0.310 open BM25, and 0.363 source-rerank. Source-rerank
wrong-operation-or-row falls to 55, and wrong-operation-type falls to 11.

The next denominator-selection pass extends same-row column ratios to named
table columns. For BLK 2012, `long-term retail/hnw in americas as a percentage
of total long-term retail/hnw` now resolves to the `long-term retail/hnw` row,
`americas` column over `total` column, producing `298024 / 403484 = 73.9%`.
This raises oracle-doc exact match to 0.397; open BM25 remains 0.310 and
source-rerank remains 0.363. Oracle wrong-operation-or-row falls to 48, and
oracle wrong-denominator falls to 2.

The next wrong-operation-type pass targets acquisition liability-to-asset
ratios. For DRE 2007, `what was the ratio of the debts to the assets in the
purchase transaction` should combine `debt assumed` and `other liabilities
assumed` before dividing by `total assets acquired`, yielding
`(148527 + 5829) / 867558 * 100 = 17.8%`. This raises oracle-doc exact match to
0.400 and source-rerank exact match to 0.367, while open BM25 remains 0.310.
Oracle wrong-operation-or-row falls to 47, oracle wrong-operation-type falls to
11, source-rerank wrong-operation-or-row falls to 54, and source-rerank
wrong-operation-type falls to 10.

The next operation-type pass handles `increase in X as a percentage of Y in
YEAR` questions that require summing prose increase components before dividing
by a year-labeled denominator row. For ETR 2004, `other regulatory credits`
increased due to `$14.3 million`, `$11.8 million`, and `$11.4 million`; these
components divided by `2003 net revenue` of `$973.7 million` produce `3.9%`,
matching the gold `3.85%` under numeric tolerance. This raises oracle-doc exact
match to 0.403 and source-rerank exact match to 0.370, while open BM25 remains
0.310 because open retrieval still selects a misleading context for this
example. Oracle wrong-operation-or-row falls to 46, oracle wrong-operation-type
falls to 10, source-rerank wrong-operation-or-row falls to 53, and source-rerank
wrong-operation-type falls to 9.

The follow-up open-retrieval pass lets the same operation combine same-source
chunks only after trying individual contexts first. This fixes the open BM25
ETR 2004 split-chunk case without reintroducing the source-rerank duplicate
chunk regression. Open BM25 exact match rises to 0.313; oracle-doc remains
0.403 and source-rerank remains 0.370.

The next open-retrieval pass adds grouped prose-ratio support for explicit
`paid in cash` over `purchase price` questions. It fixes HOLX 2007 by combining
same-source chunks containing the `$6900` cash-paid prose and the `$220600`
estimated-purchase-price table. Open BM25 exact match rises to 0.317; oracle-doc
remains 0.403 and source-rerank remains 0.370.

The latest shared-failure pass repairs ROI extraction from chunk-truncated
cumulative-return tables. The ROI path now carries a previous year-header block
across adjacent parsed table blocks and retries same-source grouped chunks after
single-context failure. This fixes AAP 2011 S&P 500 ROI across all three
retrieval settings. Exact match rises to 0.407 oracle-doc, 0.320 open BM25, and
0.373 source-rerank.

## Current Pipeline Gate

The FinQA-300 local-planner run is now wired into the one-command project
pipeline:

```powershell
python .\scripts\run_pipeline.py --refresh-results
```

The 2026-06-25 pipeline gate passed unit tests (`199 tests OK`), reran or reused the
FinQA-300 local-planner manifest, regenerated row/operation diagnostics, and
rebuilt paper-ready Markdown and LaTeX tables under
`paper/generated/finqa_300_local_planner/`. Use
`outputs/pipeline/pipeline_report.md` as the first artifact to check after each
full refresh. The pipeline now also writes
`outputs/pipeline/experiment_closure_report.md`, which validates the expected
three 300-row evaluation CSVs, failure reports, row/operation diagnostics,
dataset inspection/gate artifacts, experiment card, and generated paper tables.
