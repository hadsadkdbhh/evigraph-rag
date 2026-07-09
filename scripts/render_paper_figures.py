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
    fig, ax = plt.subplots(figsize=(7.8, 4.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.02,
        0.96,
        "EviGraph-RAG teaser: retrieved context becomes evidence only after state control",
        fontsize=11,
        fontweight="bold",
        color=PALETTE["ink"],
        va="top",
    )
    ax.text(
        0.02,
        0.90,
        "A real TAT-QA failure-driven example: year-labeled prose is selected, executed, and verified.",
        fontsize=8.5,
        color=PALETTE["muted"],
        va="top",
    )

    _box(
        ax,
        (0.03, 0.60),
        0.25,
        0.23,
        "Question",
        "Total senior notes issued\nin fiscal 2018 and 2017?",
        fc="#eef6fb",
        ec=PALETTE["blue"],
        fontsize=8.6,
    )
    _box(
        ax,
        (0.03, 0.28),
        0.25,
        0.22,
        "Retrieved candidates",
        "correct prose sentence\n+ noisy table/prose chunks\n+ analysis-only source cue",
        fc=PALETTE["panel"],
        ec=PALETTE["line"],
        fontsize=8.4,
    )

    ax.text(
        0.315,
        0.81,
        "candidate evidence graph",
        fontsize=8,
        fontweight="bold",
        color=PALETTE["ink"],
        ha="left",
    )
    graph_nodes = [
        ((0.34, 0.62), "prose node\n$10.0B in 2018\n$14.0B in 2017", PALETTE["green"], "#f2f8f5"),
        ((0.34, 0.38), "table chunk\nsame source\nwrong row risk", PALETTE["amber"], "#fff8ee"),
        ((0.51, 0.50), "distractor\nnearby finance\nnumbers", PALETTE["red"], "#fdf4f4"),
    ]
    for (x, y), label, edge, fill in graph_nodes:
        _box(ax, (x, y), 0.13, 0.15, "", label, fc=fill, ec=edge, fontsize=7.9)
    _arrow(ax, (0.46, 0.69), (0.51, 0.58), PALETTE["line"], rad=-0.12)
    _arrow(ax, (0.46, 0.45), (0.51, 0.53), PALETTE["line"], rad=0.12)
    _arrow(ax, (0.40, 0.53), (0.40, 0.50), PALETTE["line"], lw=1.0)

    _box(
        ax,
        (0.66, 0.62),
        0.15,
        0.18,
        "State selector",
        "utility - risk\nsupport flags\nsource/year match",
        fc="#f4fbf7",
        ec=PALETTE["green"],
        fontsize=8.2,
    )
    _box(
        ax,
        (0.66, 0.35),
        0.15,
        0.18,
        "Executor",
        "year-labeled prose sum\n10 + 14 = 24",
        fc="#fff8ee",
        ec=PALETTE["amber"],
        fontsize=8.2,
    )
    _box(
        ax,
        (0.84, 0.35),
        0.13,
        0.45,
        "Verified answer",
        "24 billion\n\nchecks:\nsource\ncitation\narithmetic\noperation",
        fc="#f7f9fb",
        ec=PALETTE["ink"],
        fontsize=7.8,
    )

    _arrow(ax, (0.28, 0.70), (0.34, 0.70), PALETTE["blue"])
    _arrow(ax, (0.28, 0.39), (0.34, 0.45), PALETTE["line"])
    _arrow(ax, (0.64, 0.57), (0.66, 0.71), PALETTE["green"], rad=0.15)
    _arrow(ax, (0.735, 0.62), (0.735, 0.53), PALETTE["amber"])
    _arrow(ax, (0.81, 0.44), (0.84, 0.52), PALETTE["ink"], rad=-0.12)
    _arrow(ax, (0.86, 0.46), (0.81, 0.68), PALETTE["red"], rad=-0.18, lw=1.0)

    ax.text(
        0.54,
        0.24,
        "risk edges and verifier feedback\nprevent treating every retrieved number as evidence",
        fontsize=7.4,
        color=PALETTE["red"],
        ha="center",
        va="center",
    )
    ax.text(
        0.04,
        0.08,
        "Teaser message: retrieval exposes candidates; EviGraph selects the executable evidence state.",
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


def render_experimental_story() -> None:
    fig = plt.figure(figsize=(7.8, 5.0))
    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.30)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    # A. Component contribution on FinQA-300.
    components = ["Planner", "Support\ngraph", "Graph vs\nutility"]
    oracle = [0.070, 0.020, 0.030]
    open_bm25 = [0.060, 0.040, 0.120]
    x = list(range(len(components)))
    width = 0.34
    ax1.bar([i - width / 2 for i in x], oracle, width=width, color=PALETTE["blue"], label="Oracle-doc")
    ax1.bar([i + width / 2 for i in x], open_bm25, width=width, color=PALETTE["green"], label="Open BM25")
    ax1.set_title("A. FinQA-300 component gains", fontsize=9.2, fontweight="bold")
    ax1.set_ylabel("Delta EM", fontsize=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(components, fontsize=7.3)
    ax1.tick_params(axis="y", labelsize=7.2)
    ax1.set_ylim(0, 0.14)
    ax1.legend(frameon=False, fontsize=6.8, loc="upper left")
    _style_axis(ax1)

    # B. Retrieval portfolio on FinQA-600.
    labels = ["BM25", "Hybrid", "Guarded\nportfolio"]
    values = [0.377, 0.363, 0.407]
    ax2.bar(labels, values, color=[PALETTE["blue"], "#7aa7bf", PALETTE["green"]], edgecolor=PALETTE["ink"], linewidth=0.5)
    ax2.set_title("B. FinQA-600 open retrieval", fontsize=9.2, fontweight="bold")
    ax2.set_ylabel("EM", fontsize=8)
    ax2.set_ylim(0.33, 0.43)
    ax2.tick_params(axis="x", labelsize=7.3)
    ax2.tick_params(axis="y", labelsize=7.2)
    for i, v in enumerate(values):
        ax2.text(i, v + 0.003, f"{v:.3f}", ha="center", va="bottom", fontsize=7.2)
    ax2.text(1.1, 0.423, "18 wins / 0 losses", color=PALETTE["green"], fontsize=7.2)
    _style_axis(ax2)

    # C. Cross-format portability on TAT-QA.
    settings = ["TAT-QA-50", "TAT-QA-100"]
    oracle_vals = [0.540, 0.520]
    open_vals = [0.460, 0.410]
    x2 = list(range(len(settings)))
    ax3.bar([i - width / 2 for i in x2], oracle_vals, width=width, color=PALETTE["blue"], label="Oracle-doc")
    ax3.bar([i + width / 2 for i in x2], open_vals, width=width, color=PALETTE["green"], label="Open BM25")
    ax3.axhline(0.45, color=PALETTE["blue"], linestyle="--", linewidth=0.8, alpha=0.75)
    ax3.axhline(0.35, color=PALETTE["green"], linestyle="--", linewidth=0.8, alpha=0.75)
    ax3.text(1.42, 0.452, "oracle gate", fontsize=6.6, color=PALETTE["blue"], va="bottom")
    ax3.text(1.42, 0.352, "open gate", fontsize=6.6, color=PALETTE["green"], va="bottom")
    ax3.set_title("C. TAT-QA portability", fontsize=9.2, fontweight="bold")
    ax3.set_ylabel("EM", fontsize=8)
    ax3.set_ylim(0.30, 0.60)
    ax3.set_xticks(x2)
    ax3.set_xticklabels(settings, fontsize=7.3)
    ax3.tick_params(axis="y", labelsize=7.2)
    ax3.legend(frameon=False, fontsize=6.8, loc="upper right")
    _style_axis(ax3)

    # D. Accuracy-support gap.
    points = [
        ("GPT-5.4\nDirect RAG", 0.523, 0.273, PALETTE["red"], (0.004, 0.010)),
        ("Direct RAG", 0.453, 0.740, PALETTE["amber"], (0.004, 0.010)),
        ("Retrieve-\nprogram", 0.483, 0.803, PALETTE["blue"], (0.004, 0.010)),
        ("Full\nEviGraph", 0.517, 0.840, PALETTE["green"], (-0.010, 0.030)),
        ("Full v38", 0.523, 0.853, "#1f8a70", (0.004, 0.000)),
    ]
    for label, em, support, color, offset in points:
        ax4.scatter(em, support, s=46, color=color, edgecolor=PALETTE["ink"], linewidth=0.4)
        ax4.text(em + offset[0], support + offset[1], label, fontsize=6.5, color=PALETTE["ink"])
    ax4.set_title("D. EM is not support", fontsize=9.2, fontweight="bold")
    ax4.set_xlabel("Exact match", fontsize=8)
    ax4.set_ylabel("Answer support", fontsize=8)
    ax4.set_xlim(0.43, 0.55)
    ax4.set_ylim(0.20, 0.90)
    ax4.tick_params(axis="both", labelsize=7.2)
    _style_axis(ax4)

    fig.suptitle("Experimental story: evidence-state control improves auditable RAG behavior", fontsize=11, fontweight="bold", y=0.995)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.08, top=0.90, hspace=0.46, wspace=0.30)
    _save(fig, "experimental_story_panel")


def _style_axis(ax) -> None:
    ax.grid(axis="y", color="#d8dee6", linewidth=0.6, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def _save(fig, stem: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / f"{stem}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    render_pipeline()
    render_portfolio_experiment()
    render_experimental_story()
    print(f"Wrote figures to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
