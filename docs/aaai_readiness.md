# AAAI Readiness Notes

This file tracks what the current repository can and cannot support as paper evidence.

## Supported Claims Now

- The codebase runs an end-to-end EviGraph-style pipeline on a controlled mock evidence task.
- The pipeline creates candidate evidence, scores utility and risk, selects a support subgraph, executes explicit evidence actions, verifies claims, and logs artifacts.
- The manifest runner can build a local index, convert raw question files, run ablations, run a budget sweep, summarize results, and write an experiment card.
- The current smoke tests verify misleading-evidence rejection, table parsing, calculation triggering, and claim verification on the mock setup.
- The synthetic stress suite shows that risk-aware evidence selection can reject hand-authored forecast, draft, and press distractors while simple top-k and utility-only baselines accept noisy evidence.
- A 100-example real FinQA validation subset is checked in with deterministic sampling metadata and a retrieval corpus built from source pre-text, tables, and post-text.
- On the checked-in 100-example FinQA smoke subset, the current oracle-document setting reaches 63/100 numeric exact-match accuracy with transparent calculations for ratio, percent-of-total, percent-change, row-average, row/column lookup, year-range-average, ROI, prose average, cross-chunk ratio, cross-chunk continuation-table stitching, relative row difference, percentage-point row difference, fiscal schedule percent-change, grouped table/prose ratio, horizontal and vertical maturity-schedule ratios, and difference cases.
- Open BM25 reaches 55/100, deterministic open hybrid reaches 54/100, and source-rerank reaches 64/100 for full EviGraph on the same subset; these are diagnostic baselines, not final claims.
- The experiment CSVs now separate exact match from verifier diagnostics: arithmetic support, calculation-result support, operation-semantics checking, row-operation grounding, semantic grounding, and final answer support.
- The manifest runner writes a failure report for batch experiments, grouping unresolved examples by error category for paper-oriented failure analysis.
- The row/operation diagnostic splits wrong numeric answers into wrong numerator, wrong denominator, wrong year or period, wrong row label, wrong operation type, and ambiguous supported wrong-number cases.
- The latest calculation-aware verifier raises support auditing fidelity by accepting reproducible calculation results while keeping exact-match claims separate from support diagnostics; row/operation grounding remains a paper-critical risk before making strong benchmark claims.

## Claims Not Yet Supported

- Do not claim benchmark-level performance beyond the checked-in FinQA smoke subset.
- Do not claim robustness on real multimodal documents.
- Do not claim superiority over strong dense-retrieval or agentic RAG baselines.
- Do not claim statistical significance.
- Do not claim generality beyond the current controlled mock, synthetic stress, and small FinQA smoke tasks.
- Do not present the synthetic stress suite as a public benchmark.
- Do not conflate oracle-document or source-rerank results with deployable open-retrieval performance; report open BM25 and open hybrid separately.

## Evidence Needed Before Submission

- Scale the real benchmark subset beyond the checked-in 100-example FinQA smoke subset.
- Add stronger baselines, including dense retrieval and retrieve-then-read RAG; the current deterministic open hybrid baseline is a first reproducible lexical/numeric reranker, not a substitute for dense retrieval.
- Add task-appropriate metrics beyond brittle numeric/string exact match.
- Add failure analysis and qualitative case studies from real examples.
- Keep the MVP0 acceptance gate green from a clean checkout.
- Replace hand-authored stress distractors with real retrieval confounders from benchmark corpora.
- Improve real-table numerical reasoning; current diagnostics point first to numerator/denominator selection for ratio and percent-change calculations, period intent disambiguation, and then ambiguous supported wrong-number cases.
- Separate oracle-document reasoning from open-document retrieval in future benchmark tables.
- Improve table operation coverage before using FinQA results as a positive performance claim; current top-k remains a close smoke baseline rather than a solved comparator.

## Next Engineering Step

Improve the table numerical reasoning path on the FinQA subset before scaling the
sample size or reporting benchmark claims.
