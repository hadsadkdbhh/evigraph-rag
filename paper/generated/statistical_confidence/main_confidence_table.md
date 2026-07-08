# Statistical Confidence Summary

| Setting | Method | EM | 95% Wilson CI |
| --- | --- | ---: | --- |
| FinQA-600 Open | BM25 primary | 0.377 | [0.339, 0.416] |
| FinQA-600 Open | Guarded portfolio | 0.407 | [0.368, 0.446] |
| FinQA-300 Open | BM25 Full EviGraph | 0.493 | [0.437, 0.550] |
| FinQA-300 Open | Guarded portfolio | 0.503 | [0.447, 0.560] |
| Stress suite | Top-K | 0.333 | [0.061, 0.792] |
| Stress suite | Full EviGraph | 1.000 | [0.438, 1.000] |

Notes:

- FinQA-600 portfolio vs BM25 primary: 18 paired wins, 0 losses, exact McNemar p < 0.001.
- FinQA-300 portfolio sanity check: 3 wins, 0 losses, exact McNemar p = 0.250.
- Stress suite has only 3 examples and should be described as a cross-benchmark smoke test, not a public benchmark claim.
