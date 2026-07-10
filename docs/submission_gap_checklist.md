# Submission Gap Checklist

Last updated: 2026-07-10

This checklist compares the current EviGraph-RAG / Evidence State Optimization
submission package against the kind of reviewer-facing material provided by
recent agentic GraphRAG papers such as EvoGraph-R1. The goal is not to copy their
claims. EvoGraph-R1 reports persistent self-evolving multimodal hypergraphs and
RL-trained graph actions; EviGraph-RAG should stay framed as deterministic,
query-local Evidence State Optimization for auditable numerical QA.

## What We Already Have

- Main formulation: Evidence Unit, Candidate Evidence Graph, Evidence State,
  Evidence State Space, ESO, and MRSG are defined in `paper/main.tex`.
- Main mechanism: evidence-state controller, utility-risk objective, executor,
  verifier, and retrieval portfolio are described.
- Main experimental structure: FinQA-300 mechanism table, FinQA-600 stress
  setting, TAT-QA-50/100 portability checks, confidence intervals, and retrieval
  portfolio paired test are already generated under `paper/generated/`.
- Supplement start: `paper/appendix.tex` contains the ESO state-search
  procedure, action/interface table, prompt/output contracts,
  evidence-distraction diagnostics, trace-style case studies, row/operation
  taxonomy, failure-to-fix provenance, metric definitions, dataset manifests,
  TAT-QA adapter boundary details, implementation details, ablation controls,
  retrieval portfolio details, boundary conditions, and reproducibility
  commands.
- Claim boundary: `docs/submission_artifact_index.md` and
  `docs/context/current_state.md` already warn against claiming RL, learned
  policy optimization, persistent graph editing, or SOTA.

## Highest-Priority Missing Pieces

1. Formal algorithm polish.
   - The appendix now has an executable ESO procedure and action table.
   - Current decision: keep the detailed procedure in the appendix for now and
     describe the controller compactly in the Method section. This avoids
     spending main-text space on implementation detail before the official AAAI
     page budget is known.
   - If space remains after template migration, compress the appendix procedure
     into a short main-text Algorithm 1.

## Medium-Priority Additions

2. Computational cost and traceability summary.
   - Added to `paper/appendix.tex`.
   - It reports input-token proxy, tool-call proxy, EM, and support for the main
     completed full-system runs, and documents the trace/failure-report audit
     trail.
   - Keep the wording modest. The claim is auditable evidence-state selection,
     not fastest inference.

3. Official-template compile note.
    - Official `aaai2027.sty` and `aaai2027.bst` are now checked into
      `paper/`.
    - `paper/main.tex` now uses `\usepackage[submission]{aaai2027}` and
      `\bibliographystyle{aaai2027}`.
    - `paper/supplement.tex` compiles `paper/appendix.tex` separately, so the
      supplement is no longer counted as main-paper pages.
    - Remaining blocker: install or provide a pdfLaTeX-capable TeX Live/MiKTeX
      runtime. Official `aaai2027.sty` rejects XeTeX/Tectonic.

## What Not To Borrow

- Do not claim persistent graph memory across queries.
- Do not add web search as a core method unless we can run controlled
  experiments and report costs.
- Do not describe deterministic repair as RL or learned policy optimization.
- Do not add multimodal claims beyond TAT-QA/financial table-text portability.
- Do not introduce a new hypergraph implementation unless it is tied to a
  measurable experiment.

## Next Concrete Writing Pass

Recommended next edit order:

1. Install/provide TeX Live or MiKTeX with `pdflatex`, `bibtex`, and `latexmk`.
2. Run `powershell -ExecutionPolicy Bypass -File .\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement`.
3. If the main paper exceeds 7 pages before references or 9 pages total, first
   compress figures/tables and references, not method definitions.
4. Only then decide whether a compact Algorithm 1 fits in the main paper.
