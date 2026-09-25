#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def box(ax, x, y, w, h, title, subtitle=""):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.2,
        fill=False,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=11, weight="bold")
    if subtitle:
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center", fontsize=8, wrap=True)


def arrow(ax, start, end, label=""):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={"arrowstyle": "->", "linewidth": 1.2},
    )
    if label:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.025, label, ha="center", va="bottom", fontsize=8)


def architecture(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    box(ax, 0.03, 0.62, 0.16, 0.20, "Agent / Actor", "proposal or tool request")
    box(ax, 0.27, 0.62, 0.18, 0.20, "SDV", "Actor--Critic--Judge\noptional validation")
    box(ax, 0.53, 0.62, 0.18, 0.20, "Tool Gateway", "fail-closed authorization")
    box(ax, 0.79, 0.62, 0.18, 0.20, "External Tool", "side effect / result")

    arrow(ax, (0.19, 0.72), (0.27, 0.72), "proposal")
    arrow(ax, (0.45, 0.72), (0.53, 0.72), "approved request")
    arrow(ax, (0.71, 0.72), (0.79, 0.72), "permit")
    arrow(ax, (0.79, 0.66), (0.71, 0.66), "result")

    box(ax, 0.19, 0.20, 0.22, 0.22, "AARC Monitor", "commit order, anchors,\nhash chain, lifecycle")
    box(ax, 0.50, 0.20, 0.22, 0.22, "Runtime Event Log", "schema-valid events +\nState Vector snapshots")
    box(ax, 0.80, 0.20, 0.17, 0.22, "Verifier / Auditor", "offline or online\nconformance checks")

    arrow(ax, (0.11, 0.62), (0.27, 0.42), "events")
    arrow(ax, (0.36, 0.62), (0.34, 0.42), "decision receipt")
    arrow(ax, (0.62, 0.62), (0.40, 0.37), "authorization evidence")
    arrow(ax, (0.41, 0.31), (0.50, 0.31), "commit")
    arrow(ax, (0.72, 0.31), (0.80, 0.31), "verify")

    ax.text(
        0.5,
        0.94,
        "AARC v1.1.0: observable reliability contract around the model",
        ha="center",
        va="center",
        fontsize=14,
        weight="bold",
    )
    ax.text(
        0.5,
        0.08,
        "The model may propose actions; external runtime components remain authoritative for conformance and side effects.",
        ha="center",
        va="center",
        fontsize=9,
    )

    fig.savefig(path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def verification(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    stages = [
        (0.03, "Schema", "event/state\nshape"),
        (0.23, "Integrity", "sequence +\nhash chain"),
        (0.43, "Anchors", "role/objective/\npolicy invariance"),
        (0.63, "Semantics", "tool permits +\nSDV separation"),
        (0.83, "Lifecycle", "genesis +\nterminal state"),
    ]
    for x, title, subtitle in stages:
        box(ax, x, 0.60, 0.14, 0.20, title, subtitle)
    for i in range(len(stages) - 1):
        arrow(ax, (stages[i][0] + 0.14, 0.70), (stages[i + 1][0], 0.70))

    box(
        ax,
        0.08,
        0.18,
        0.84,
        0.22,
        "Adversarial conformance suite",
        "deletion · reordering · duplication · payload mutation · rehashed anchor drift · sequence gap · broken link · forged permit · unauthorized tool · self-approval · missing terminal",
    )
    arrow(ax, (0.50, 0.40), (0.50, 0.60), "fault injection")

    ax.text(
        0.5,
        0.93,
        "Verification stack and deterministic fault-injection coverage",
        ha="center",
        fontsize=14,
        weight="bold",
    )
    ax.text(
        0.5,
        0.08,
        "Rehashed semantic attacks are included so detection is not reducible to checksum failure.",
        ha="center",
        fontsize=9,
    )

    fig.savefig(path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    figures_dir = repo_root / "paper" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    architecture(figures_dir / "aarc_architecture.pdf")
    verification(figures_dir / "aarc_verification.pdf")


if __name__ == "__main__":
    main()
