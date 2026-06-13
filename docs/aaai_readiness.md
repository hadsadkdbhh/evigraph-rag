# AAAI Readiness Notes

This file tracks what the current repository can and cannot support as paper evidence.

## Supported Claims Now

- The codebase runs an end-to-end EviGraph-style pipeline on a controlled mock evidence task.
- The pipeline creates candidate evidence, scores utility and risk, selects a support subgraph, executes explicit evidence actions, verifies claims, and logs artifacts.
- The manifest runner can build a local index, convert raw question files, run ablations, run a budget sweep, summarize results, and write an experiment card.
- The current smoke tests verify misleading-evidence rejection, table parsing, calculation triggering, and claim verification on the mock setup.

## Claims Not Yet Supported

- Do not claim benchmark-level performance.
- Do not claim robustness on real multimodal documents.
- Do not claim superiority over strong dense-retrieval or agentic RAG baselines.
- Do not claim statistical significance.
- Do not claim generality beyond the current controlled smoke task.

## Evidence Needed Before Submission

- Add at least one real benchmark subset with documented preprocessing.
- Add stronger baselines, including dense retrieval and retrieve-then-read RAG.
- Add task-appropriate metrics beyond numeric exact match.
- Add failure analysis and qualitative case studies from real examples.
- Add reproducibility checks that can run from a clean checkout.

## Next Engineering Step

Connect a small real chart/table QA benchmark subset through `scripts/convert_dataset.py`
and `configs/experiments.mock.json`-style manifests, then inspect whether the current
selector/action/verifier design still works without toy assumptions.
