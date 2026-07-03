# Next Phase Goals

Last updated: 2026-07-01

This file defines the next research phase after the FinQA-300 experiment loop
was closed as a reproducible artifact workflow. These are target gates for a
credible AAAI-oriented project, not claims about the current system.

## Current Starting Point

Latest FinQA-300 local-planner exact match:

| setting | current EM |
| --- | ---: |
| Oracle-doc full EviGraph | 0.510 |
| Open BM25 full EviGraph | 0.403 |
| BM25 + source-rerank full EviGraph | 0.510 |

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
- Oracle-doc has reached the `0.50+` minimum gate at `0.510`; Open BM25 has
  exceeded the `0.35+` open-retrieval sanity target at `0.403`; and
  source-rerank has cleared the `0.45+` analysis target at `0.510`. The next
  priority is no longer merely crossing these floors, but adding external
  baselines and increasing the margin so the empirical story is less fragile.

## Baselines To Add

Current local-planner baselines and ablations have been added in
`configs/experiments.finqa_300.local_planner_ablation.json` and generated under
`paper/generated/finqa_300_local_planner_ablation/`.
They cover Top-k Program, Full context, Utility-only, no-risk,
no-operation-planner, no-verifier, no-support, and Full EviGraph across
oracle-doc, open BM25, and source-rerank.
They now also include Direct RAG, retrieve-then-program, and
no-verifier-grounded-rejection.
Retrieval baselines have also been added in
`configs/experiments.finqa_300.local_planner_retrieval_baselines.json` and
generated under `paper/generated/finqa_300_local_planner_retrieval_baselines/`.
They compare Open BM25, local hashed dense, and open hybrid retrieval using the
same local planner and verifier. Current Full EviGraph EM is `0.403` for BM25,
`0.133` for local hashed dense, and `0.400` for hybrid. Under Open BM25,
Direct RAG reaches `0.370`, retrieve-then-program reaches `0.393`, and Full
EviGraph reaches `0.403`.
Before making a paper-level empirical claim, still add external baselines:

- Run the newly added LLM direct RAG baseline with the same retrieved context
  budget. The method is `llm_direct_rag`, the config is
  `configs/default_llm_direct_rag.yaml`, and the manifest is
  `configs/experiments.finqa_300.llm_direct_rag.json`.
- A true neural dense retrieval baseline if environment and dependencies allow;
  the current `open_dense` setting is only a deterministic local hashed-vector
  baseline.
- Retrieve-then-program baseline without evidence graph control if we want a
  separately named baseline beyond the current Top-k Program implementation.

Each baseline must write CSVs, summary tables, failure reports where applicable,
and be included in the experiment closure contract or a separate baseline
closure report.

## Ablations To Add

Current ablations:

- Full EviGraph.
- Direct RAG.
- Retrieve-then-program.
- No risk scoring.
- No verifier.
- No verifier-grounded rejection.
- No evidence-graph support selection.
- Retrieval-only top-k context with the same answer generator.
- Utility-only selection with the same answer generator.
- No operation planner, using the existing generator without planner fallback.

Still required:

- Open-retrieval-safe verifier-guided repair; the first repair loop is enabled
  only for oracle-doc and source-rerank because open retrieval can otherwise
  accept self-consistent repairs from the wrong document.
- Run the LLM Direct RAG manifest and generate paper tables under a dedicated
  output directory.
- Add a stronger retrieve-then-read baseline if the direct LLM baseline is not
  enough for reviewer comparison.

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

## Main-Conference Idea Additions

Four recent graph, multimodal, and agentic RAG papers suggest a stronger
method framing for the next phase:

- `MG^2-RAG` motivates multi-granularity evidence structure. For EviGraph-RAG,
  the transferable idea is not multimodal visual grounding, but representing
  retrieved evidence at document, chunk, table, row, cell/year, operation, and
  verifier-judgment granularities rather than treating each retrieved chunk as a
  flat passage.
- `MC-Search` motivates process-level evaluation. For EviGraph-RAG, convert a
  final numeric answer into a hop-wise trace: source hit, row hit, period hit,
  operand hit, operation hit, citation hit, and final exact match. This should
  become a paper table because it explains where failures occur instead of only
  reporting end accuracy.
- `DGPO/ARC` motivates fine-grained agentic capability metrics without forcing
  us to train with RL. For EviGraph-RAG, use the capability breakdown as a
  diagnostic template: retrieval coordination, evidence selection, operation
  planning, execution, and response synthesis.
- `ReAG` motivates critic-based evidence filtering. For EviGraph-RAG, add an
  `EvidenceCritic` that labels candidate evidence before selection with
  structured fields such as target entity present, target period present,
  required row present, numerator present, denominator present, operation cue
  present, and noise risk.

The recommended implementation order is:

1. Add `EvidenceCritic` as a deterministic first version, reusing existing
   scorer, verifier, and row-operation diagnostic signals rather than creating a
   new model dependency. Implemented as a diagnostic critic in
   `evigraph/process_trace.py`.
2. Add hop-wise numeric trace artifacts and a process accuracy table for
   FinQA-300. This should report source, row, period, operand, operation, and
   citation support separately from exact match. Implemented for manifest
   outputs as `*_process_trace.md` and for paper assets as
   Table `tab:finqa-process-diagnostics`.
3. Add verifier-guided repair as a bounded one-retry loop driven by critic and
   verifier labels: wrong denominator, wrong year/period, wrong row label, and
   wrong operation type.
4. Extend the evidence graph schema and paper figure to describe multi-
   granularity nodes. This is a method and visualization upgrade first; only
   measure accuracy after the critic and trace are in place.

Do not start RL training in this phase. The main-conference value should come
from auditable evidence-state control, process diagnostics, and bounded
verifier-guided repair, not from an underpowered reinforcement-learning claim.

Initial FinQA-300 process diagnostics show the next bottleneck clearly:
evidence availability, period alignment, row grounding, and citation checking
are high, while operand support is only about `0.52` across oracle-doc, Open
BM25, and source-rerank. Operation semantics are around `0.86--0.87`.
Therefore the next repair target should be operand selection, especially
wrong numerator/denominator and wrong year/period interactions, rather than
additional broad retrieval or row-label heuristics.

## Immediate Work Order

1. Run `configs/experiments.finqa_300.llm_direct_rag.json` with a named model
   and record the model, provider, temperature, and context budget.
2. Continue improving Oracle-doc beyond the exact `0.50` floor while monitoring
   source-rerank and open BM25 for regressions.
3. Add planner-without-verifier-grounded-rejection ablations.
4. Add, if feasible, a true neural dense retrieval baseline.
5. Rewrite the methodology section around operation planner, verifier, and
   evidence graph rather than rule patches.
