# Retrieval Portfolio Ablation

## FinQA-600 Main Stress Setting

| Selector | EM | Switches | Wins | Losses |
| --- | ---: | ---: | ---: | ---: |
| BM25 top-8 primary | 0.377 | 0 | -- | -- |
| Neural-hybrid top-16 | 0.363 | 600 | -- | -- |
| Conservative portfolio v44 | 0.388 | 19 | 7 | 0 |
| Confidence portfolio v45 | 0.407 | 77 | 19 | 1 |
| Guarded confidence portfolio v46 | 0.407 | 74 | 18 | 0 |

## FinQA-300 Cross-Setting Sanity Check

| Selector | EM | Switches | Wins | Losses |
| --- | ---: | ---: | ---: | ---: |
| BM25 primary, Full EviGraph | 0.493 | 0 | -- | -- |
| Neural-hybrid, Full EviGraph | 0.507 | 300 | -- | -- |
| Guarded confidence portfolio, Full EviGraph | 0.503 | 18 | 3 | 0 |

## Interpretation

The conservative v44 policy is nearly risk-free but leaves many neural-hybrid-only wins unused. The confidence v45 policy crosses 0.40 on FinQA-600 but introduces one paired loss. The guarded v46 policy keeps the 0.407 EM while removing that loss by requiring complete year coverage for fallback percent-change questions with two query years.
