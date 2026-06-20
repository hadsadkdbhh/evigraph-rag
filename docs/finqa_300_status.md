# FinQA 300-Example Validation Status

This note records the first scaled FinQA validation run beyond the 100-example
smoke subset. It is intended as an experiment checkpoint, not a final paper
claim.

## Dataset

- Source dataset: `dreamerdeo/finqa`
- Split: `validation`
- Pool size: 600 rows fetched through the Hugging Face rows API
- Sample size: 300 answerable examples
- Seed: `13`
- Raw records: `data/raw/finqa_300_subset.jsonl`
- Corpus directory: `data/finqa_300_corpus`
- Manifest: `configs/experiments.finqa_300.json`

The downloader filters out rows with missing answers before sampling. The
benchmark gate passed with 300 records, no duplicate IDs, no missing queries,
no missing answers, and source-document coverage of 1.0.

## Reproduction Commands

```powershell
python .\scripts\download_finqa_subset.py --split validation --pool-size 600 --sample-size 300 --seed 13 --raw-output data/raw/finqa_300_subset.jsonl --corpus-output data/finqa_300_corpus --clean-corpus
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.json
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa_300 --output-dir .\paper\generated\finqa_300
```

## Main Results

| setting | full EviGraph EM | strongest baseline EM | note |
| --- | ---: | ---: | --- |
| Oracle-doc | 0.297 | 0.303 | `evigraph_wo_verifier` is slightly higher on raw EM, but lacks verifier metrics. |
| Open BM25 | 0.203 | 0.233 | Top-k has higher EM; full EviGraph has stronger support diagnostics. |
| Open hybrid | 0.210 | 0.230 | Similar pattern to BM25. |
| BM25 + source rerank | 0.273 | 0.293 | Top-k remains higher EM; full EviGraph improves support diagnostics. |

Full EviGraph support diagnostics remain high relative to EM:

| setting | answer supported | calculation supported | operation semantics | row grounded |
| --- | ---: | ---: | ---: | ---: |
| Oracle-doc | 0.710 | 0.373 | 0.750 | 0.733 |
| Open BM25 | 0.723 | 0.370 | 0.750 | 0.727 |
| Open hybrid | 0.720 | 0.367 | 0.747 | 0.723 |
| BM25 + source rerank | 0.733 | 0.383 | 0.760 | 0.743 |

## Failure Profile

For full EviGraph under BM25 + source rerank:

| category | count |
| --- | ---: |
| wrong numeric operation or row | 49 |
| no numeric answer, other | 45 |
| no numeric answer, percent | 52 |
| no numeric answer, additive or lookup | 40 |
| no numeric answer, ratio | 27 |
| unsupported textual prediction | 5 |

Row/operation diagnostics for the wrong-row/wrong-operation subset:

| diagnostic | count |
| --- | ---: |
| wrong numerator | 9 |
| wrong denominator | 8 |
| wrong year or period | 8 |
| wrong row label | 9 |
| wrong operation type | 10 |
| ambiguous supported wrong number | 20 |

## Interpretation

The 300-example run is a useful reality check: the 100-example smoke subset was
too optimistic. Scaling reveals that full EviGraph currently provides better
support/verification diagnostics than plain top-k, but its raw EM is not yet
competitive enough for a final AAAI claim.

The next implementation priority should be a more general operation planner and
executor, especially for:

- multiplication programs such as `average price * volume * 365`;
- percent-of-increase queries where the denominator is an increase, not a base
  value;
- year/period selection when table headers and row labels both contain dates;
- ratio queries where numerator and denominator share overlapping row terms.
