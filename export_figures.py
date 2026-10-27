"""Export four reproducible scientific figures, sharing the interactive models.

Run ``uv run python export_figures.py --output figs``. Uses a noninteractive
backend and creates files only from main(). Labels are English for portability.
"""

from argparse import ArgumentParser
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

from physics import clt_experiment, make_distribution, population_moments, two_level

TEAL, AMBER, VIOLET = "#087E8B", "#E89B3F", "#7868B0"


def build_figures():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": "#182B3A",
            "text.color": "#182B3A",
            "axes.titleweight": "bold",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.grid": True,
            "grid.color": "#e8edf1",
            "grid.alpha": 0.8,
        }
    )
    figures = {}
    rv = make_distribution("normal")
    x = np.linspace(-3.5, 3.5, 600)
    lo, hi = rv.ppf([0.25, 0.75])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    ax[0].plot(x, rv.pdf(x), color=TEAL, lw=2)
    ax[0].fill_between(x, 0, rv.pdf(x), where=(x >= lo) & (x <= hi), color=TEAL, alpha=0.18)
    ax[0].set(title="Probability is area", xlabel="$x$", ylabel="$f(x)$")
    ax[1].plot(x, rv.cdf(x), color=TEAL, lw=2)
    ax[1].scatter([lo, hi], [0.25, 0.75], color=AMBER, zorder=3)
    ax[1].set(title="The same interval in the CDF", xlabel="$x$", ylabel="$F(x)$")
    fig.suptitle("01  Distribution and cumulative probability", fontsize=15)
    figures["01_probability"] = fig

    fig, ax = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    grid = np.geomspace(1, 100, 600)
    for alpha, color in [(1.5, AMBER), (3, TEAL), (5, VIOLET)]:
        p = make_distribution("pareto", alpha)
        ax[0].loglog(grid, p.sf(grid), label=rf"$\alpha={alpha}$", color=color, lw=2)
    ax[0].set(title="Tail probability", xlabel="$x$", ylabel="$P(X>x)$")
    ax[0].legend(frameon=False)
    alphas = np.linspace(4.1, 10, 400)
    kurt = [population_moments(make_distribution("pareto", a))["kurtosis"] for a in alphas]
    ax[1].plot(alphas, kurt, color=TEAL, lw=2)
    ax[1].axhline(3, color=VIOLET, ls="--", label="Normal: 3")
    ax[1].set(
        title="Finite kurtosis requires alpha > 4", xlabel=r"$\alpha$", ylabel="Pearson kurtosis"
    )
    ax[1].legend(frameon=False)
    fig.suptitle("02  Pareto tails and the fourth moment", fontsize=15)
    figures["02_tail_moments"] = fig

    fig, ax = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    z = np.linspace(-4, 6, 600)
    for axis, n in zip(ax, [1, 64]):
        results = clt_experiment("exponential", 3, n, 5000, 515)
        counts, edges = np.histogram(results["standardized"], bins=np.linspace(-4, 6, 71))
        axis.stairs(
            counts / (5000 * np.diff(edges)),
            edges,
            fill=True,
            color=AMBER,
            alpha=0.55,
            label="Sample means",
        )
        axis.plot(z, norm.pdf(z), color=TEAL, lw=2, label="Standard normal")
        axis.set(
            title=f"Exponential parent, n = {n}",
            xlabel=r"$\sqrt{n}(\bar X-\mu)/\sigma$",
            ylabel="Density",
        )
        axis.legend(frameon=False)
    fig.suptitle("03  The central limit theorem", fontsize=15)
    figures["03_clt"] = fig

    fig, ax = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    for N, color in [(8, AMBER), (32, VIOLET), (200, TEAL)]:
        d = two_level(N, N // 2)
        ax[0].plot(d["q_grid"] / N, d["entropy_per_particle"], label=f"N = {N}", color=color, lw=2)
    x = np.linspace(0.001, 0.999, 600)
    ax[0].plot(
        x, -x * np.log(x) - (1 - x) * np.log1p(-x), color="#718493", ls="--", label="Large N"
    )
    ax[0].set(title="Counting microstates", xlabel="$q/N$", ylabel=r"$S/(Nk_B)$")
    ax[0].legend(frameon=False)
    ax[1].plot(x, np.log((1 - x) / x), color=TEAL, lw=2)
    ax[1].axhline(0, color="#718493", lw=1)
    ax[1].axvspan(0.5, 1, color=VIOLET, alpha=0.08)
    ax[1].set(
        title="Inverse temperature (large-N approximation)",
        xlabel="$q/N$",
        ylabel=r"$\beta\epsilon$",
    )
    fig.suptitle("04  Two-level systems and entropy", fontsize=15)
    figures["04_entropy"] = fig
    return figures


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "figs")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, figure in build_figures().items():
        for extension in ("png", "svg"):
            figure.savefig(args.output / f"{name}.{extension}", dpi=180)
        plt.close(figure)
    print(f"Saved 4 figures (PNG + SVG) to {args.output.resolve()}")


if __name__ == "__main__":
    main()
