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
