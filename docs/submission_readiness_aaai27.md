# AAAI-27 Submission Readiness Plan

Verified against the official AAAI-27 conference pages on 2026-06-20.

Sources:

- AAAI-27 main page: https://aaai.org/conference/aaai/aaai-27/
- AAAI-27 main technical track call: https://aaai.org/conference/aaai/aaai-27/main-technical-track-call/

## External Constraints

- Abstract deadline: 2026-07-21, 11:59 PM UTC-12.
- Full paper deadline: 2026-07-28, 11:59 PM UTC-12.
- Supplementary material and code deadline: 2026-07-31, 11:59 PM UTC-12.
- Main-track submissions may use up to 7 pages of technical content, with additional pages only for references.
- Reviewers are not required to inspect supplementary material, so core claims, tables, and proofs needed for evaluation must fit in the main paper.
- The reproducibility checklist is mandatory.
- Code and data can be submitted as supplementary material, so this repository should remain runnable from a clean checkout.

## Current Submission Position

EviGraph-RAG is a plausible AAAI methodology paper only if we frame it as an
evidence-state control framework with diagnostic FinQA evidence, not as a
state-of-the-art financial QA benchmark paper.

Current strengths:

- End-to-end reproducible pipeline with manifest-driven experiments.
- Deterministic 300-example and 600-example FinQA validation subsets with source documents recorded.
- Clearly separated retrieval settings: oracle-doc, open BM25, neural dense, neural hybrid, retrieval portfolio selection, and source-rerank analysis.
- Generated paper tables for exact match, support diagnostics, and failure categories.
- Generated row/operation diagnostic tables that split wrong numeric answers by operand, year/period, row-label, operation-type, and ambiguous supported wrong-number signals.
- Formal subgraph-selection objective with monotone submodular structure.
- Failure reports that identify the next engineering target instead of relying on anecdotal inspection.

Current blockers:

- The paper now has a first-pass related-work section, but it still needs final tightening and citation polish.
- The method figure is now present as a lightweight LaTeX diagram, but it should be polished if space allows.
- Open retrieval now includes lexical BM25, sentence-transformer dense retrieval, neural hybrid retrieval, and a no-gold guarded retrieval-portfolio selector.
- FinQA-600 is now available as a larger pressure test.
- A small public TAT-QA-50 arithmetic pilot now runs through the same manifest
  pipeline; it reduces the FinQA-only concern, but it is a portability check
  rather than a full second-benchmark claim. The latest v50 repair reaches
  0.540 oracle-doc and 0.460 open BM25 exact match on this pilot.
- A fixed-seed TAT-QA-100 portability check now clears the planned second-dataset
  gate with 0.520 oracle-doc and 0.410 open BM25 exact match. Use this as
  cross-format evidence, not as a full TAT-QA leaderboard claim.
- The paper needs a full reproducibility checklist and a clear code/data release note.
- The exact-match results are diagnostic, not strong enough to sell as benchmark superiority.
- The current FinQA-600 open-retrieval target has crossed 0.40 with guarded
  portfolio selection, but this should be framed as evidence-state selection
  over heterogeneous retrieval states rather than a solved retrieval benchmark.

## Submission-Safe Claim Strategy

Safe main claim:

EviGraph-RAG improves auditability for numerically grounded RAG by representing
retrieved context as an evidence graph, selecting a compact risk-adjusted
support subgraph, executing table operations locally, and verifying final
answers against cited evidence.

Unsafe claims until more work is done:

- Do not claim state-of-the-art FinQA performance.
- Do not claim dense-retrieval superiority.
- Do not claim robustness on native PDFs or multimodal documents.
- Do not claim that source-rerank is a deployable open-retrieval setting.
- Do not merge oracle-doc and open-retrieval results into one headline number.

## Work Plan to Submission

Priority 1: make the paper defensible.

- Tighten related work around RAG, financial/table QA, and verifiable/tool-augmented QA.
- Polish the method figure if space allows.
- Keep the formal subgraph-selection proof concise enough for the 7-page limit.
- Add a reproducibility checklist draft and map every reported table to a command.

Priority 2: strengthen the empirical story.

- Use `docs/next_phase_goals.md` as the target gate for the next empirical
  phase.
- Keep dense/neural-hybrid retrieval baselines and retrieval-portfolio selection
  in a separate open-retrieval stress block.
- Add BM25 top-k reader, LLM direct RAG, retrieve-then-program, and top-k plus
  local numeric executor baselines.
- Add ablations for no risk scoring, no verifier, no evidence-graph selection,
  no operation planner, planner without verifier-grounded rejection, and top-k
  with the same answer generator.
- Scale the new public TAT-QA pilot beyond 50 examples only after the adapter
  and failure reports remain stable; until then, report it as a small
  cross-benchmark pilot.
- Keep oracle-doc, open BM25, hybrid/dense open retrieval, and source-rerank analysis in separate table blocks.
- Track failure categories and row/operation diagnostics after every manifest run and prioritize the largest open-retrieval error classes.

Priority 3: prepare supplement.

- Include exact manifests, seed, source_doc handling, environment notes, and code-running instructions.
- Include generated failure reports and representative case studies.
- Include any extended proof or additional ablation details that cannot fit in the main 7 pages.
