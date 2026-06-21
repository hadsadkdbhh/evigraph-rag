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
