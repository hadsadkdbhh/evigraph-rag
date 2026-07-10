# Code and Data Release Note

Last updated: 2026-07-10

This note defines the submission-side code/data package for the current
EviGraph-RAG / Evidence State Optimization (ESO) draft. It is intended for
supplementary material, artifact handoff, and clean-checkout reproduction.

## Scope

The repository release contains:

- Deterministic ESO pipeline code under `evigraph/`.
- Manifest-driven experiment runners under `scripts/`.
- Fixed-seed FinQA subsets and corpora:
  - `data/raw/finqa_300_subset.jsonl`
  - `data/raw/finqa_600_subset.jsonl`
  - `data/finqa_300_corpus/`
  - `data/finqa_600_corpus/`
- Fixed-seed TAT-QA portability subsets and corpora:
  - `data/raw/tatqa_50_subset.jsonl`
  - `data/raw/tatqa_100_subset.jsonl`
  - `data/tatqa_50_corpus/`
  - `data/tatqa_100_corpus/`
- Paper-ready generated tables under `paper/generated/`.
- Main paper, supplement entrypoint, and appendix under `paper/`.
- Official AAAI-27 style and bibliography files under `paper/`.

The release intentionally does not track runtime outputs under `outputs/`.
Those directories can be regenerated from manifests and are ignored by Git.
API keys, `.env` files, model-provider credentials, and AutoFigure/image-edit
outputs are not part of the code/data release.

## Primary Reproduction Commands

Run unit tests:

```powershell
python -m unittest discover -s tests
```

Run the local submission-suite gate from existing outputs:

```powershell
python scripts/run_pipeline.py --suite submission --skip-llm-direct-rag
```

Refresh all local no-API submission outputs:

```powershell
python scripts/run_pipeline.py --suite submission --refresh-results --skip-llm-direct-rag
```

Rebuild paper tables from completed evaluations:

```powershell
python scripts/build_paper_assets.py --eval-dir outputs/eval/finqa --output-dir paper/generated
```

Run the official AAAI page-budget check with the local pdfLaTeX runtime:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement
```

## Reported Result Boundaries

The release supports the following conservative claims:

- ESO is implemented as deterministic verifier-guided evidence-state search,
  not reinforcement learning or learned policy optimization.
- FinQA-300 is the main mechanism and ablation subset.
- FinQA-600 is a larger open-retrieval stress subset.
- TAT-QA-50 and TAT-QA-100 are portability checks, not full TAT-QA leaderboard
  claims.
- Source-rerank is an analysis setting and should not be described as a
  deployable open-retrieval result.
- Synthetic stress examples are mechanism tests, not benchmark evidence.

Do not claim state-of-the-art FinQA or TAT-QA performance from this package.
The paper should emphasize evidence-state selection, verifier support, exact
match/support gaps, and failure-driven diagnostics.

## Privacy and Packaging Notes

- Keep private API keys out of the repository.
- Keep untracked `outputs/` out of Git commits unless a specific artifact is
  promoted into `paper/generated/` or `docs/`.
- Keep AutoFigure generated outputs out of the non-figure submission checkpoint.
- Before external sharing, rerun `git status --short` and confirm no `.env`,
  provider logs, raw API traces, or private attachments are staged.

## Known Environment Requirement

The official AAAI-27 style file requires pdfTeX. The bundled Tectonic path uses
XeTeX and is rejected by `aaai2027.sty`, so the final page-budget check requires
a local TeX Live or MiKTeX installation that provides `pdflatex`, `bibtex`, and
PDF inspection tools such as `pdfinfo` and `pdftotext`. On this Windows
machine, MiKTeX 25.12 plus Strawberry Perl satisfies that requirement; the
2026-07-10 check passes with main content 7/7 pages and supplement 6 pages.
