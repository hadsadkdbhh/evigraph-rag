# Figure Plan for AAAI Submission

This is a planning document, not the final artwork. The goal is to keep the
figures aligned with the paper story: retrieval exposure is necessary but not
sufficient; EviGraph-RAG contributes verifier-guided evidence-state selection.

## Figure 1: Pipeline Figure

Purpose:

- Show the end-to-end evidence-state control pipeline.
- Make clear that retrieval outputs are candidates, not final context.
- Emphasize auditable intermediate artifacts: graph, support subgraph,
  operation trace, verifier result.

Recommended panels:

1. Query and heterogeneous retrievers:
   - BM25.
   - Neural dense.
   - Neural hybrid.
   - Optional source-rerank analysis setting, visually marked as analysis-only.
2. Candidate evidence graph:
   - Nodes: passages, table chunks, row candidates, calculation candidates.
   - Edges: source adjacency, table-row relation, temporal/year alignment,
     contradiction or noisy-source risk.
3. Evidence-state selector:
   - Utility/risk scoring.
   - Verifier-support flags.
   - Retrieval portfolio selector choosing between BM25 and neural-hybrid
     evidence states.
4. Local operation executor:
   - Row/column selection.
   - Sum, difference, ratio, percent change, average.
5. Verifier and output:
   - Citation check.
   - Arithmetic check.
   - Row grounding.
   - Operation semantics.
   - Final answer plus trace.

Visual emphasis:

- Use arrows from multiple retrievers into a shared candidate evidence graph.
- Put the selector/verifier in the center, not the retriever.
- Avoid making the figure look like "better retriever = solved".

## Figure 2: Mechanism Figure

Purpose:

- Explain the main empirical insight from the portfolio experiment.
- Neural hybrid improves source exposure, but final accuracy only improves when
  a no-gold confidence selector chooses the better evidence state.

Recommended panels:

1. BM25 evidence state:
   - Example fallback prose or wrong numeric operation.
   - Mark as "retrieved but not executable" or "supported but wrong operand".
2. Neural-hybrid evidence state:
   - Example complementary candidate with better query/year coverage or an
     executable calculation.
3. Verifier-guided confidence selector:
   - Inputs: fallback status, query-token coverage, year coverage, calculation
     presence, support flags.
   - Guard: two-year percent-change fallback must cover both query years.
4. Outcome:
   - v44 conservative: 0.388, 7 wins, 0 losses.
   - v45 confidence: 0.407, 19 wins, 1 loss.
   - v46 guarded confidence: 0.407, 18 wins, 0 losses.

Visual emphasis:

- The mechanism is "choose evidence state", not "choose final answer by gold".
- Include a small note: no gold answers or accuracy fields are used for routing.
- Show the loss guard as a concrete repair to the selector, not as another
  numeric rule.

## Mermaid Draft

```mermaid
flowchart LR
  Q["Question"] --> R1["BM25 evidence state"]
  Q --> R2["Neural-hybrid evidence state"]
  R1 --> G["Candidate evidence graph"]
  R2 --> G
  G --> S["Verifier-guided evidence-state selector"]
  S --> E["Local table-operation executor"]
  E --> V["Verifier: citation, arithmetic, row, operation"]
  V --> A["Answer + trace"]
```

## Figure Placement

- Figure 1 should appear in Method, replacing or polishing the current
  lightweight LaTeX pipeline diagram.
- Figure 2 should appear in the Open-Retrieval Baseline Stress Test subsection
  near the retrieval portfolio ablation table.
