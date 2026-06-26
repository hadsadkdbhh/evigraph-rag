# Next Phase Goals

Last updated: 2026-06-26

This file defines the next research phase after the FinQA-300 experiment loop
was closed as a reproducible artifact workflow. These are target gates for a
credible AAAI-oriented project, not claims about the current system.

## Current Starting Point

Latest FinQA-300 local-planner exact match:

| setting | current EM |
| --- | ---: |
| Oracle-doc full EviGraph | 0.487 |
| Open BM25 full EviGraph | 0.393 |
| BM25 + source-rerank full EviGraph | 0.463 |

The engineering pipeline and experiment artifact closure are complete. The
remaining work is research quality: stronger numerical reasoning, stronger
open retrieval, baselines, ablations, and a cleaner paper narrative.

## Phase Target Metrics

Minimum target before treating FinQA-300 as a positive empirical story:

| setting | target EM |
| --- | ---: |
| Oracle-doc full EviGraph | 0.50+ |
| BM25 + source-rerank full EviGraph | 0.45+ |
| Open BM25 full EviGraph | 0.35+ |

Interpretation:

- Oracle-doc `0.50+` means the operation planner and verifier are doing enough
  real table reasoning when retrieval is controlled.
- Source-rerank `0.45+` means the evidence-state machinery remains useful when
  realistic retrieval noise is present but source metadata is available for
  analysis.
- Open BM25 has exceeded the `0.35+` minimum deployable open-retrieval sanity
  target at `0.393`, and source-rerank has cleared the `0.45+` analysis target
  at `0.463`; the next priority is to raise oracle-doc from `0.487` to `0.50+`
  without losing the open/source retrieval floors.

## Baselines To Add

Current local-planner baselines and ablations have been added in
`configs/experiments.finqa_300.local_planner_ablation.json` and generated under
`paper/generated/finqa_300_local_planner_ablation/`.
They cover top-k, utility-only, no-risk, no-verifier, no-support, and full
EviGraph for the applicable retrieval settings.
Before making a paper-level empirical claim, still add external baselines:

- BM25 top-k reader baseline.
- Dense retrieval baseline.
- LLM direct RAG baseline with the same retrieved context budget.
- Retrieve-then-program baseline without evidence graph control.
- Top-k plus local numeric executor baseline.

Each baseline must write CSVs, summary tables, failure reports where applicable,
and be included in the experiment closure contract or a separate baseline
closure report.

## Ablations To Add

Current ablations:

- Full EviGraph.
- No risk scoring.
- No verifier.
- No evidence-graph support selection.
- Retrieval-only top-k context with the same answer generator.
- Utility-only selection with the same answer generator.

Still required:

- No operation planner, using existing heuristic/generator path only.
- Planner without verifier-grounded rejection.
- Dense retrieval and retrieve-then-read baselines.

The paper should report exact match separately from support diagnostics:
answer support, calculation support, operation-semantics checking, row grounding,
semantic grounding, and citation correctness.

## Paper Narrative Constraint

Do not frame the project as a collection of FinQA-specific repair rules. The
paper should foreground:

- Evidence graph construction from retrieved candidates.
- Utility-risk support subgraph selection.
- Program-style operation planning.
- Local table operation execution.
- Verifier-grounded answer support.
- Failure-driven diagnostics as an analysis method, not as the main algorithm.

Use concrete FinQA repairs only as case studies that motivate general planner,
executor, or verifier mechanisms.

## Immediate Work Order

1. Continue improving Oracle-doc first until the operation planner reaches
   `0.50+`.
2. Once Oracle-doc moves, rerun source-rerank and open BM25 and inspect whether
   retrieval or reasoning is the bottleneck.
3. Add no-operation-planner and planner-without-verifier-grounded-rejection
   ablations.
4. Add dense retrieval and retrieve-then-read baselines.
5. Rewrite the methodology section around operation planner, verifier, and
   evidence graph rather than rule patches.
