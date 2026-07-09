from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "paper" / "figures"


PALETTE = {
    "ink": "#1b2430",
    "muted": "#667085",
    "line": "#9aa8b7",
    "blue": "#356f95",
    "blue_fill": "#eaf3f8",
    "green": "#4f8066",
    "green_fill": "#edf6f0",
    "amber": "#b9852e",
    "amber_fill": "#fbf2df",
    "rose": "#a85757",
    "rose_fill": "#fbefef",
    "purple": "#8a6fa4",
    "purple_fill": "#f3eef8",
    "slate": "#475467",
    "panel": "#f7f8fa",
    "grid": "#dce3ea",
    "white": "#ffffff",
}


def _box(ax, xy, width, height, title, body="", fc=None, ec=None, fontsize=8.5, lw=1.2, radius=0.025):
    fc = fc or PALETTE["white"]
    ec = ec or PALETTE["line"]
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0.015,rounding_size={radius}",
        linewidth=lw,
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


def _panel(ax, xy, width, height, title="", fc=None, ec=None, lw=1.6, radius=0.025):
    patch = _box(ax, xy, width, height, "", "", fc=fc or PALETTE["white"], ec=ec or PALETTE["ink"], lw=lw, radius=radius)
    if title:
        x, y = xy
        ax.text(
            x + 0.02,
            y + height - 0.04,
            title,
            ha="left",
            va="top",
            fontsize=8.8,
            fontweight="bold",
            color=ec or PALETTE["ink"],
        )
    return patch


def _tag(ax, xy, text, fc, ec, fontsize=7.6):
    x, y = xy
    ax.text(
        x,
        y,
        text,
        ha="left",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=ec,
        bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.08", fc=fc, ec=ec, lw=1.2),
    )


def _circle_node(ax, xy, text, fc=None, ec=None, r=0.033, fontsize=7.3, weight="bold"):
    fc = fc or PALETTE["white"]
    ec = ec or PALETTE["ink"]
    circ = Circle(xy, r, facecolor=fc, edgecolor=ec, linewidth=1.35)
    ax.add_patch(circ)
    ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=fontsize, fontweight=weight, color=PALETTE["ink"], linespacing=0.95)
    return circ


def _agent_step(ax, xy, width, height, title, body, fc, ec, icon, fontsize=7.0):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.022",
        linewidth=1.35,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    cx = x + width * 0.22
    cy = y + height * 0.54
    if icon == "target":
        ax.add_patch(Circle((cx, cy), height * 0.20, facecolor=PALETTE["white"], edgecolor=ec, linewidth=1.3))
        ax.add_patch(Circle((cx, cy), height * 0.09, facecolor="none", edgecolor=ec, linewidth=1.1))
        ax.plot([cx - height * 0.25, cx + height * 0.25], [cy, cy], color=ec, lw=1.0)
        ax.plot([cx, cx], [cy - height * 0.25, cy + height * 0.25], color=ec, lw=1.0)
    elif icon == "gear":
        ax.add_patch(Circle((cx, cy), height * 0.18, facecolor=ec, edgecolor=ec, linewidth=1.0))
        ax.add_patch(Circle((cx, cy), height * 0.08, facecolor=fc, edgecolor=fc, linewidth=1.0))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7)]:
            ax.plot([cx, cx + dx * height * 0.25], [cy, cy + dy * height * 0.25], color=ec, lw=1.2)
    elif icon == "shield":
        pts = [
            (cx, cy + height * 0.24),
            (cx + height * 0.20, cy + height * 0.13),
            (cx + height * 0.16, cy - height * 0.14),
            (cx, cy - height * 0.25),
            (cx - height * 0.16, cy - height * 0.14),
            (cx - height * 0.20, cy + height * 0.13),
        ]
        ax.add_patch(Polygon(pts, closed=True, facecolor=PALETTE["white"], edgecolor=ec, linewidth=1.3))
        ax.plot([cx - height * 0.08, cx - height * 0.01, cx + height * 0.11], [cy - height * 0.02, cy - height * 0.10, cy + height * 0.09], color=ec, lw=1.5)
    ax.text(x + width * 0.62, y + height * 0.65, title, ha="center", va="center", fontsize=fontsize, fontweight="bold", color=PALETTE["ink"])
    ax.text(x + width * 0.62, y + height * 0.31, body, ha="center", va="center", fontsize=fontsize - 1.1, color=PALETTE["muted"], linespacing=1.05)
    return patch


def _arrow(ax, start, end, color=None, rad=0.0, lw=1.2, linestyle="-", scale=10):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=scale,
        linewidth=lw,
        color=color or PALETTE["line"],
        linestyle=linestyle,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arrow)
    return arrow


def render_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(7.8, 4.45))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _panel(ax, (0.015, 0.02), 0.97, 0.95, fc=PALETTE["white"], ec=PALETTE["ink"], lw=1.9, radius=0.018)
    _box(
        ax,
        (0.06, 0.86),
        0.90,
        0.08,
        "EviGraph-RAG Evidence-State Reasoning",
        "retrieved text/tables are candidate evidence states, not final evidence",
        fc=PALETTE["white"],
        ec=PALETTE["ink"],
        fontsize=9.3,
        lw=1.7,
        radius=0.020,
    )

    _panel(ax, (0.045, 0.30), 0.23, 0.47, "Retrieved Candidates", fc=PALETTE["panel"], ec=PALETTE["blue"], lw=1.45)
    docs = [(0.078, 0.555), (0.158, 0.555), (0.078, 0.405), (0.158, 0.405)]
    for i, (x, y) in enumerate(docs):
        ax.add_patch(Rectangle((x, y), 0.052, 0.105, facecolor=PALETTE["white"], edgecolor=PALETTE["ink"], linewidth=0.9))
        ax.add_patch(Polygon([(x + 0.038, y + 0.105), (x + 0.052, y + 0.090), (x + 0.052, y + 0.105)], closed=True, facecolor=PALETTE["panel"], edgecolor=PALETTE["ink"], linewidth=0.7))
        ax.plot([x + 0.009, x + 0.037], [y + 0.056, y + 0.056], color=PALETTE["line"], lw=0.8)
        ax.plot([x + 0.009, x + 0.037], [y + 0.042, y + 0.042], color=PALETTE["line"], lw=0.8)
        ax.plot([x + 0.009, x + 0.030], [y + 0.028, y + 0.028], color=PALETTE["line"], lw=0.8)
        if i == 0:
            _tag(ax, (x + 0.006, y + 0.014), "10.0B\n2018", PALETTE["blue_fill"], PALETTE["blue"], fontsize=5.0)
        if i == 1:
            _tag(ax, (x + 0.006, y + 0.014), "14.0B\n2017", PALETTE["blue_fill"], PALETTE["blue"], fontsize=5.0)
    ax.text(0.16, 0.345, "retrieved by BM25 /\nhybrid retriever", ha="center", va="center", fontsize=7.0, color=PALETTE["muted"], linespacing=1.1)

    _panel(ax, (0.315, 0.265), 0.31, 0.52, "Candidate Evidence Graph", fc=PALETTE["white"], ec=PALETTE["ink"], lw=1.7)
    ax.text(0.555, 0.705, r"$G=(V,E)$", fontsize=8.1, color=PALETTE["muted"], ha="left", va="center")
    ax.add_patch(Ellipse((0.425, 0.555), 0.205, 0.235, facecolor="none", edgecolor=PALETTE["green"], linewidth=2.1, alpha=0.82))
    ax.add_patch(Ellipse((0.515, 0.475), 0.185, 0.200, facecolor="none", edgecolor=PALETTE["rose"], linewidth=2.0, alpha=0.82))
    _circle_node(ax, (0.375, 0.640), "v1\n2018\n10.0B", fc=PALETTE["green_fill"], ec=PALETTE["green"], r=0.038, fontsize=6.4)
    _circle_node(ax, (0.455, 0.640), "v2\n2017\n14.0B", fc=PALETTE["green_fill"], ec=PALETTE["green"], r=0.038, fontsize=6.4)
    _circle_node(ax, (0.395, 0.455), "v3\ntable\nrisk", fc=PALETTE["amber_fill"], ec=PALETTE["amber"], r=0.038, fontsize=6.2)
    _circle_node(ax, (0.535, 0.535), "v4\nnearby\nnums", fc=PALETTE["rose_fill"], ec=PALETTE["rose"], r=0.039, fontsize=6.0)
    _circle_node(ax, (0.555, 0.365), "v5\nsource\ncue", fc=PALETTE["blue_fill"], ec=PALETTE["blue"], r=0.037, fontsize=6.1)
    ax.text(0.420, 0.545, "support\nhyperedge", fontsize=7.1, fontweight="bold", color=PALETTE["green"], ha="center", va="center")
    ax.text(0.515, 0.455, "risk\nhyperedge", fontsize=7.0, fontweight="bold", color=PALETTE["rose"], ha="center", va="center")
    for start, end, col in [
        ((0.405, 0.632), (0.430, 0.615), PALETTE["green"]),
        ((0.460, 0.612), (0.520, 0.548), PALETTE["rose"]),
        ((0.408, 0.505), (0.515, 0.455), PALETTE["line"]),
    ]:
        _arrow(ax, start, end, col, lw=1.0, scale=8)

    _panel(ax, (0.655, 0.265), 0.185, 0.52, "", fc=PALETTE["white"], ec=PALETTE["purple"], lw=1.55)
    ax.text(0.748, 0.735, "EviGraph\nAgent Loop", fontsize=8.0, fontweight="bold", color=PALETTE["purple"], ha="center", va="center", linespacing=0.9)
    _agent_step(ax, (0.678, 0.585), 0.135, 0.105, "Select State", "max utility\nminus risk", PALETTE["green_fill"], PALETTE["green"], "target", fontsize=6.8)
    _agent_step(ax, (0.678, 0.430), 0.135, 0.105, "Execute\nOperation", "select years\nsum(10,14)", PALETTE["amber_fill"], PALETTE["amber"], "gear", fontsize=6.8)
    _agent_step(ax, (0.678, 0.275), 0.135, 0.105, "Verify Trace", "citation\narithmetic\noperation", PALETTE["purple_fill"], PALETTE["purple"], "shield", fontsize=6.7)
    _box(ax, (0.872, 0.410), 0.085, 0.21, "Verified\nAnswer", "24 billion", fc=PALETTE["green_fill"], ec=PALETTE["ink"], fontsize=7.2, lw=1.7)
    shield_x, shield_y = 0.914, 0.515
    ax.add_patch(Polygon(
        [
            (shield_x, shield_y + 0.040),
            (shield_x + 0.028, shield_y + 0.024),
            (shield_x + 0.022, shield_y - 0.020),
            (shield_x, shield_y - 0.045),
            (shield_x - 0.022, shield_y - 0.020),
            (shield_x - 0.028, shield_y + 0.024),
        ],
        closed=True,
        facecolor=PALETTE["green"],
        edgecolor=PALETTE["green"],
        linewidth=1.0,
        alpha=0.92,
    ))
    ax.plot([shield_x - 0.012, shield_x - 0.003, shield_x + 0.017], [shield_y - 0.004, shield_y - 0.018, shield_y + 0.018], color=PALETTE["white"], lw=2.0)
    _arrow(ax, (0.625, 0.585), (0.655, 0.635), PALETTE["green"], rad=0.10, lw=1.3)
    _arrow(ax, (0.745, 0.585), (0.745, 0.535), PALETTE["amber"], lw=1.3)
    _arrow(ax, (0.745, 0.430), (0.745, 0.380), PALETTE["purple"], lw=1.3)
    _arrow(ax, (0.840, 0.515), (0.872, 0.515), PALETTE["ink"], lw=1.3)
    _arrow(ax, (0.865, 0.455), (0.815, 0.625), PALETTE["rose"], rad=-0.30, lw=1.2, linestyle="--", scale=8)
    ax.text(0.863, 0.645, "repair / rethink", fontsize=6.4, color=PALETTE["rose"], rotation=72, ha="center", va="center")

    _arrow(ax, (0.275, 0.535), (0.315, 0.535), PALETTE["blue"], lw=1.5, scale=12)
    _arrow(ax, (0.625, 0.660), (0.655, 0.660), PALETTE["green"], lw=1.5, scale=12)
    legend_y = 0.135
    _circle_node(ax, (0.125, legend_y), "", fc=PALETTE["green_fill"], ec=PALETTE["green"], r=0.012, fontsize=4)
    ax.text(0.148, legend_y, "Support hyperedge", fontsize=6.6, color=PALETTE["ink"], va="center")
    _circle_node(ax, (0.300, legend_y), "", fc=PALETTE["rose_fill"], ec=PALETTE["rose"], r=0.012, fontsize=4)
    ax.text(0.323, legend_y, "Risk hyperedge", fontsize=6.6, color=PALETTE["ink"], va="center")
    _circle_node(ax, (0.460, legend_y), "", fc=PALETTE["blue_fill"], ec=PALETTE["blue"], r=0.012, fontsize=4)
    ax.text(0.483, legend_y, "Source cue", fontsize=6.6, color=PALETTE["ink"], va="center")
    _arrow(ax, (0.625, legend_y), (0.690, legend_y), PALETTE["blue"], lw=1.2, scale=9)
    ax.text(0.702, legend_y, "Flow", fontsize=6.6, color=PALETTE["ink"], va="center")
    _arrow(ax, (0.780, legend_y), (0.845, legend_y), PALETTE["rose"], lw=1.2, linestyle="--", scale=9)
    ax.text(0.858, legend_y, "Feedback", fontsize=6.6, color=PALETTE["ink"], va="center")

    fig.tight_layout(pad=0.4)
    _save(fig, "evigraph_pipeline")


def render_portfolio_experiment() -> None:
    fig = plt.figure(figsize=(7.8, 3.95))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.05], wspace=0.36)
    ax = fig.add_subplot(gs[0, 0])
    mech = fig.add_subplot(gs[0, 1])

    labels = ["BM25\nprimary", "Neural\nhybrid", "v44\ncons.", "v45\nconf.", "v46\nguard"]
    em = [0.377, 0.363, 0.388, 0.407, 0.407]
    colors = [PALETTE["blue"], "#91b5c6", PALETTE["green"], PALETTE["amber"], PALETTE["green"]]
    bars = ax.bar(range(len(em)), em, color=colors, edgecolor=PALETTE["ink"], linewidth=0.6)
    ax.set_ylim(0.32, 0.43)
    ax.set_ylabel("Exact match", fontsize=8.5)
    ax.set_title("A. FinQA-600 open retrieval", fontsize=9.6, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.tick_params(axis="y", labelsize=7.5)
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.65, alpha=0.86)
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
    mech.set_title("B. Retrieval portfolio as evidence-state routing", fontsize=9.4, fontweight="bold", pad=7)
    _panel(mech, (0.04, 0.08), 0.91, 0.82, fc=PALETTE["white"], ec=PALETTE["ink"], lw=1.55, radius=0.016)
    _box(mech, (0.08, 0.68), 0.35, 0.15, "BM25 state", "high lexical hit\nbut wrong operand\nrisk", fc=PALETTE["blue_fill"], ec=PALETTE["blue"], fontsize=7.3, lw=1.3)
    _box(mech, (0.57, 0.68), 0.34, 0.15, "Hybrid state", "complementary\nsource exposure\n+ calculation", fc=PALETTE["green_fill"], ec=PALETTE["green"], fontsize=7.3, lw=1.3)
    _box(mech, (0.25, 0.43), 0.49, 0.14, "Confidence selector", "fallback status, source/year coverage,\noperation trace, support flags", fc=PALETTE["panel"], ec=PALETTE["line"], fontsize=7.1, lw=1.35)
    _box(mech, (0.30, 0.20), 0.39, 0.12, "Guarded answer", "switch only when the evidence state\nis more executable and not weaker", fc=PALETTE["green_fill"], ec=PALETTE["green"], fontsize=6.9, lw=1.35)
    _arrow(mech, (0.255, 0.68), (0.41, 0.57), PALETTE["blue"], lw=1.35, scale=11)
    _arrow(mech, (0.735, 0.68), (0.59, 0.57), PALETTE["green"], lw=1.35, scale=11)
    _arrow(mech, (0.495, 0.43), (0.495, 0.32), PALETTE["green"], lw=1.35, scale=11)
    _arrow(mech, (0.70, 0.24), (0.78, 0.70), PALETTE["rose"], rad=-0.36, lw=1.05, linestyle="--", scale=9)
    mech.text(0.84, 0.39, "verifier guard\nblocks unsafe\nswitches", fontsize=6.0, color=PALETTE["rose"], ha="center", va="center", linespacing=1.05)
    mech.text(
        0.50,
        0.13,
        "Routing uses no answer strings, gold labels,\nor accuracy fields.",
        fontsize=6.1,
        color=PALETTE["muted"],
        ha="center",
        va="bottom",
        linespacing=1.05,
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
    labels = ["BM25", "Hybrid", "v44", "v45", "v46"]
    values = [0.377, 0.363, 0.388, 0.407, 0.407]
    x_line = list(range(len(labels)))
    ax2.plot(x_line, values, color=PALETTE["green"], linewidth=2.0, marker="o", markersize=4.7, label="portfolio EM")
    ax2.plot([0, 1], [values[0], values[1]], color=PALETTE["blue"], linewidth=1.4, marker="o", markersize=4.2, label="retriever-only")
    ax2.fill_between(x_line, [0.36] * len(values), values, color=PALETTE["green_fill"], alpha=0.65)
    ax2.set_title("B. FinQA-600 open retrieval trajectory", fontsize=9.2, fontweight="bold")
    ax2.set_ylabel("EM", fontsize=8)
    ax2.set_ylim(0.33, 0.43)
    ax2.set_xticks(x_line)
    ax2.set_xticklabels(labels, fontsize=7.3)
    ax2.tick_params(axis="y", labelsize=7.2)
    for i, v in enumerate(values):
        ax2.text(i, v + 0.0035, f"{v:.3f}", ha="center", va="bottom", fontsize=6.9, color=PALETTE["ink"])
    ax2.text(2.25, 0.423, "v46: 18 wins / 0 losses", color=PALETTE["green"], fontsize=7.1)
    ax2.legend(frameon=False, fontsize=6.8, loc="lower right")
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
        ("GPT-5.4\nDirect RAG", 0.523, 0.273, PALETTE["rose"], (0.004, 0.010)),
        ("Direct RAG", 0.453, 0.740, PALETTE["amber"], (0.004, 0.010)),
        ("Retrieve-\nprogram", 0.483, 0.803, PALETTE["blue"], (0.004, 0.010)),
        ("Full\nEviGraph", 0.517, 0.840, PALETTE["green"], (-0.010, 0.030)),
        ("Full v38", 0.523, 0.853, "#5a8f76", (0.004, 0.000)),
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

    fig.suptitle("Experimental story: evidence-state control improves auditable RAG behavior", fontsize=10.4, fontweight="bold", y=0.995)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.08, top=0.90, hspace=0.46, wspace=0.30)
    _save(fig, "experimental_story_panel")


def _style_axis(ax) -> None:
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.65, alpha=0.86)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#2b3037")
    ax.spines[["left", "bottom"]].set_linewidth(0.8)


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
