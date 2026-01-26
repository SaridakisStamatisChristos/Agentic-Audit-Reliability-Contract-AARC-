#!/usr/bin/env python3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def make_simple_pdf(path: Path, title: str) -> None:
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(0.1, 0.9, title, fontsize=24)
    fig.savefig(path, format="pdf")
    plt.close(fig)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    figures_dir = repo_root / "paper" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    make_simple_pdf(figures_dir / "arf_architecture.pdf", "ARF Architecture")
    make_simple_pdf(figures_dir / "arf_lifecycle.pdf", "ARF Lifecycle")


if __name__ == "__main__":
    main()
