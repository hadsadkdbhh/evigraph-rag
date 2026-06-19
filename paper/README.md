# AAAI Paper Skeleton

This folder contains the working AAAI-style paper skeleton.

Current status:

- Title, abstract, introduction, method, experiments, failure analysis, and conclusion placeholders are present.
- The main results and failure-analysis tables are generated from `outputs/eval/finqa/*.csv`.
- The method figure is a text placeholder; replace it with a proper graph diagram before submission.

Refresh paper assets after each manifest run:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa --output-dir .\paper\generated
```

The draft is intentionally conservative: current FinQA results are oracle-document reasoning baselines, not final open-retrieval benchmark claims.
