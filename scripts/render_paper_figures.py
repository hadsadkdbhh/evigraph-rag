from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "paper" / "figures"


PALETTE = {
    "ink": "#1f2933",
    "muted": "#5f6b7a",
    "line": "#9aa7b5",
    "blue": "#2f6f9f",
    "green": "#2f7d5c",
    "amber": "#b7791f",
    "red": "#b74b4b",
    "panel": "#f7f9fb",
    "white": "#ffffff",
}


def _box(ax, xy, width, height, title, body="", fc="#ffffff", ec="#9aa7b5", fontsize=8.5):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        linewidth=1.2,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    multiline_title = "\n" in title
    multiline_body = "\n" in body
    title_y = 0.70 if multiline_title and body else 0.67 if multiline_body else 0.64
    body_y = 0.27 if multiline_title else 0.29 if multiline_body else 0.33
    ax.text(
        x + width / 2,
        y + height * title_y,
        title,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=PALETTE["ink"],
        linespacing=0.95,
    )
    if body:
        ax.text(
            x + width / 2,
            y + height * body_y,
            body,
            ha="center",
            va="center",
            fontsize=fontsize - 1.2,
            color=PALETTE["muted"],
            linespacing=1.15,
        )
    return patch


def _arrow(ax, start, end, color=None, rad=0.0, lw=1.2):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=lw,
        color=color or PALETTE["line"],
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arrow)
    return arrow


def render_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(7.6, 4.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.02,
        0.96,
        "EviGraph-RAG: from retrieved context to verified evidence state",
        fontsize=11,
        fontweight="bold",
        color=PALETTE["ink"],
        va="top",
    )
    ax.text(
        0.02,
        0.90,
        "Retrieved candidates are not treated as evidence until selected, executed, and verified.",
        fontsize=8.5,
        color=PALETTE["muted"],
        va="top",
    )

    _box(ax, (0.03, 0.64), 0.13, 0.15, "Question", "numeric QA\nsource cues", fc="#eef6fb", ec=PALETTE["blue"])
    _box(ax, (0.22, 0.77), 0.15, 0.115, "BM25", "lexical state", fc="#f2f7fb", ec=PALETTE["blue"], fontsize=8)
    _box(ax, (0.22, 0.60), 0.15, 0.115, "Neural hybrid", "dense + lexical\nstate", fc="#f2f8f5", ec=PALETTE["green"], fontsize=8)
    _box(ax, (0.22, 0.43), 0.15, 0.115, "Source-rerank", "analysis-only", fc="#fbf7ef", ec=PALETTE["amber"], fontsize=8)

    _box(
        ax,
        (0.43, 0.58),
        0.18,
        0.20,
        "Candidate graph",
        "passages, tables, rows\nedges: source, year,\nrisk, adjacency",
        fc=PALETTE["panel"],
        ec=PALETTE["line"],
    )
    _box(
        ax,
        (0.68, 0.58),
        0.17,
        0.20,
        "Evidence-state\nselector",
        "utility - risk\nsupport flags\nportfolio confidence",
        fc="#f4fbf7",
        ec=PALETTE["green"],
    )
    _box(
        ax,
        (0.43, 0.20),
        0.18,
        0.18,
        "Operation executor",
        "row/column select\nsum, diff, ratio\n% change, average",
        fc="#fff8ee",
        ec=PALETTE["amber"],
    )
    _box(
        ax,
        (0.68, 0.20),
        0.17,
        0.18,
        "Verifier",
        "citation, arithmetic\nrow grounding\noperation semantics",
        fc="#fdf4f4",
        ec=PALETTE["red"],
    )
    _box(
        ax,
        (0.89, 0.39),
        0.10,
        0.18,
        "Answer",
        "value +\ntrace +\ncitations",
        fc="#f7f9fb",
        ec=PALETTE["ink"],
        fontsize=8,
    )

    _arrow(ax, (0.16, 0.71), (0.22, 0.82), PALETTE["blue"])
    _arrow(ax, (0.16, 0.71), (0.22, 0.66), PALETTE["green"])
    _arrow(ax, (0.16, 0.71), (0.22, 0.50), PALETTE["amber"])
    for y in [0.82, 0.66, 0.50]:
        _arrow(ax, (0.37, y), (0.43, 0.68), rad=0.08)
    _arrow(ax, (0.61, 0.68), (0.68, 0.68), PALETTE["green"])
    _arrow(ax, (0.765, 0.58), (0.52, 0.38), PALETTE["amber"], rad=0.17)
    _arrow(ax, (0.61, 0.29), (0.68, 0.29), PALETTE["red"])
    _arrow(ax, (0.85, 0.29), (0.89, 0.45), PALETTE["ink"], rad=-0.12)
    _arrow(ax, (0.765, 0.38), (0.765, 0.58), PALETTE["red"], rad=0.0, lw=1.0)

    ax.text(
        0.66,
        0.49,
        "reject or repair\nunsupported states",
        fontsize=7.1,
        color=PALETTE["red"],
        ha="left",
        va="center",
    )
    ax.text(
        0.04,
        0.08,
        "Key distinction: retrieval exposure is only a candidate pool;\n"
        "the submitted evidence is the selected, executable, verified state.",
        fontsize=7.5,
        color=PALETTE["muted"],
        ha="left",
        va="bottom",
    )

    fig.tight_layout(pad=0.4)
    _save(fig, "evigraph_pipeline")


def render_portfolio_experiment() -> None:
    fig = plt.figure(figsize=(7.8, 3.75))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.05], wspace=0.36)
    ax = fig.add_subplot(gs[0, 0])
    mech = fig.add_subplot(gs[0, 1])

    labels = ["BM25\nprimary", "Neural\nhybrid", "v44\ncons.", "v45\nconf.", "v46\nguard"]
    em = [0.377, 0.363, 0.388, 0.407, 0.407]
    colors = [PALETTE["blue"], "#7aa7bf", PALETTE["green"], PALETTE["amber"], PALETTE["green"]]
    bars = ax.bar(range(len(em)), em, color=colors, edgecolor=PALETTE["ink"], linewidth=0.6)
    ax.set_ylim(0.32, 0.43)
    ax.set_ylabel("Exact match", fontsize=8.5)
    ax.set_title("A. FinQA-600 open retrieval", fontsize=9.6, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.tick_params(axis="y", labelsize=7.5)
    ax.grid(axis="y", color="#d8dee6", linewidth=0.6, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, val in zip(bars, em):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.003, f"{val:.3f}", ha="center", va="bottom", fontsize=7.5)

    ax.annotate(
        "18 wins / 0 losses\nMcNemar p < 0.001",
        xy=(4, 0.407),
        xytext=(2.62, 0.423),
        arrowprops=dict(arrowstyle="-|>", color=PALETTE["green"], lw=1.0),
        fontsize=7.3,
        color=PALETTE["green"],
        ha="left",
    )

    mech.set_xlim(0, 1)
    mech.set_ylim(0, 1)
    mech.axis("off")
    mech.set_title("B. Evidence-state routing", fontsize=9.6, fontweight="bold", pad=6)
    _box(mech, (0.04, 0.70), 0.41, 0.17, "BM25 state", "source-hit but\nfallback or wrong\noperand", fc="#f2f7fb", ec=PALETTE["blue"], fontsize=7.8)
    _box(mech, (0.56, 0.70), 0.40, 0.17, "Hybrid state", "complementary\ncoverage or executable\ncalculation", fc="#f2f8f5", ec=PALETTE["green"], fontsize=7.8)
    _box(mech, (0.20, 0.40), 0.60, 0.17, "No-gold confidence selector", "fallback status, query/year coverage,\ncalculation, support flags", fc=PALETTE["panel"], ec=PALETTE["line"], fontsize=7.8)
    _box(mech, (0.22, 0.13), 0.56, 0.15, "Guarded output", "switch only when evidence state is\nmore executable and not weaker", fc="#f4fbf7", ec=PALETTE["green"], fontsize=7.8)
    _arrow(mech, (0.25, 0.70), (0.40, 0.58), PALETTE["blue"])
    _arrow(mech, (0.75, 0.70), (0.60, 0.58), PALETTE["green"])
    _arrow(mech, (0.50, 0.40), (0.50, 0.28), PALETTE["green"])
    mech.text(
        0.04,
        0.02,
        "No answer strings, gold labels, or accuracy fields are used for routing.",
        fontsize=7.1,
        color=PALETTE["muted"],
        ha="left",
        va="bottom",
    )

    fig.subplots_adjust(left=0.06, right=0.985, bottom=0.18, top=0.88, wspace=0.36)
    _save(fig, "retrieval_portfolio_mechanism")


def _save(fig, stem: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / f"{stem}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    render_pipeline()
    render_portfolio_experiment()
    print(f"Wrote figures to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
