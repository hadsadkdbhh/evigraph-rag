# FinQA Subset

This directory contains a deterministic 20-example smoke subset from the
`dreamerdeo/finqa` Hugging Face dataset.

- Source dataset: `dreamerdeo/finqa`
- Config: `default`
- Split: `validation`
- Dataset Viewer endpoint: `https://datasets-server.huggingface.co`
- Pool: first 100 validation rows
- Sample size: 100
- Seed: 13
- Raw questions: `data/raw/finqa_subset.jsonl`
- Retrieval corpus: `data/finqa_corpus/`

Regenerate the files with:

```powershell
python scripts/download_finqa_subset.py --split validation --pool-size 100 --sample-size 100 --seed 13 --clean-corpus
```

The corpus Markdown files include the source pre-text, table, and post-text.
They intentionally exclude the gold answer and gold evidence annotations. The
raw JSONL keeps `gold_evidence` as metadata for later failure analysis, but the
manifest conversion ignores it for evaluation input.
