# AAAI Readiness Notes

This file tracks what the current repository can and cannot support as paper evidence.

## Supported Claims Now

- The codebase runs an end-to-end EviGraph-style pipeline on a controlled mock evidence task.
- The pipeline creates candidate evidence, scores utility and risk, selects a support subgraph, executes explicit evidence actions, verifies claims, and logs artifacts.
- The manifest runner can build a local index, convert raw question files, run ablations, run a budget sweep, summarize results, and write an experiment card.
- The current smoke tests verify misleading-evidence rejection, table parsing, calculation triggering, and claim verification on the mock setup.
- The synthetic stress suite shows that risk-aware evidence selection can reject hand-authored forecast, draft, and press distractors while simple top-k and utility-only baselines accept noisy evidence.
- A 20-example real FinQA validation subset is checked in with deterministic sampling metadata and a retrieval corpus built from source pre-text, tables, and post-text.
- On the checked-in 100-example FinQA smoke subset, the current oracle-document setting reaches 12/100 numeric exact-match accuracy with transparent calculations for ratio, percent-change, row-average, year-range-average, and difference cases.
- Open BM25 reaches 9/100 and source-rerank reaches 10/100 for full EviGraph on the same subset; these are diagnostic baselines, not final claims.
- The manifest runner writes a failure report for batch experiments, grouping unresolved examples by error category for paper-oriented failure analysis.

## Claims Not Yet Supported

- Do not claim benchmark-level performance beyond the checked-in FinQA smoke subset.
- Do not claim robustness on real multimodal documents.
- Do not claim superiority over strong dense-retrieval or agentic RAG baselines.
- Do not claim statistical significance.
- Do not claim generality beyond the current controlled mock, synthetic stress, and small FinQA smoke tasks.
- Do not present the synthetic stress suite as a public benchmark.
- Do not present the current FinQA result as open-retrieval performance; the manifest uses the provided `source_doc` to constrain retrieval to the gold source document.

## Evidence Needed Before Submission

- Scale the real benchmark subset beyond the checked-in 20-example FinQA smoke subset.
- Add stronger baselines, including dense retrieval and retrieve-then-read RAG.
- Add task-appropriate metrics beyond brittle numeric/string exact match.
- Add failure analysis and qualitative case studies from real examples.
- Add reproducibility checks that can run from a clean checkout.
- Replace hand-authored stress distractors with real retrieval confounders from benchmark corpora.
- Improve real-table numerical reasoning; the current rule generator does not solve the FinQA subset yet.
- Separate oracle-document reasoning from open-document retrieval in future benchmark tables.
- Improve table operation coverage before using FinQA results as a positive performance claim; current top-k can still outperform full EviGraph in oracle-doc accuracy.

## Next Engineering Step

Improve the table numerical reasoning path on the FinQA subset before scaling the
sample size or reporting benchmark claims.
