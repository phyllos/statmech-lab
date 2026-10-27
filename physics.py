"""Numerical models for the PHYS 515 concept experiments.

All distributions use dimensionless coordinates.  ``kurtosis`` means Pearson
kurtosis (Gaussian = 3), and ``excess_kurtosis`` means Pearson minus 3.
Two-level energies are expressed in units of the positive gap epsilon.
This module has no plotting, file output, or random global-state side effects.
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy import special, stats

DISTRIBUTIONS = ("normal", "uniform", "exponential", "lognormal", "pareto", "student_t", "cauchy")


def make_distribution(name: str, shape: float = 3.0, align: bool = False):
    """Return a frozen SciPy distribution, optionally median/IQR aligned.

    ``shape`` is log-space sigma for lognormal, alpha for Pareto I, and degrees
    of freedom for Student t.  Pareto I has support x >= 1 before alignment.
    Alignment is the affine transformation Y=(X-median(X))/IQR(X), not a
    unit-variance standardization; it also works when moments do not exist.
    """
    if name not in DISTRIBUTIONS:
        raise ValueError(f"Unknown distribution: {name!r}")
    if name in {"lognormal", "pareto", "student_t"}:
        if not np.isfinite(shape) or shape <= 0:
            raise ValueError("The shape parameter must be positive and finite.")
    constructors = {
        "normal": lambda: stats.norm(loc=0.0, scale=1.0),
        "uniform": lambda: stats.uniform(loc=-np.sqrt(3.0), scale=2 * np.sqrt(3.0)),
        "exponential": lambda: stats.expon(loc=0.0, scale=1.0),
        "lognormal": lambda: stats.lognorm(shape, loc=0.0, scale=1.0),
        "pareto": lambda: stats.pareto(shape, loc=0.0, scale=1.0),
        "student_t": lambda: stats.t(shape, loc=0.0, scale=1.0),
        "cauchy": lambda: stats.cauchy(loc=0.0, scale=1.0),
    }
    rv = constructors[name]()
    if not align:
        return rv
    q1, median, q3 = rv.ppf([0.25, 0.5, 0.75])
    iqr = float(q3 - q1)
    if not np.isfinite(iqr) or iqr <= 0:
        raise ValueError("Cannot align a distribution with a nonfinite or zero IQR.")
    parameters = dict(rv.kwds)
    parameters["loc"] = (parameters.get("loc", 0.0) - median) / iqr
    parameters["scale"] = parameters.get("scale", 1.0) / iqr
    return rv.dist(*rv.args, **parameters)


def population_moments(rv) -> dict[str, float]:
    """Analytical population moments; preserve nan/inf for nonfinite moments.

    A symmetric distribution need not possess a moment-based skewness.  In
    particular, the Cauchy mean, variance, skewness, and kurtosis are undefined.
    The UI must not replace these values with zero or a sample estimate.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mean, variance, skewness, excess = rv.stats(moments="mvsk")
    return {
        "mean": float(mean),
        "variance": float(variance),
        "skewness": float(skewness),
        "kurtosis": float(excess + 3.0),
        "excess_kurtosis": float(excess),
    }


def sample_summary(sample) -> dict[str, float | int]:
    """Sample summaries and Tukey boxplot geometry, using the full sample.

    Quartiles use NumPy's linear interpolation convention. Whiskers are the
    most extreme observed values inside the inclusive 1.5 IQR fences.  Sample
    skewness and kurtosis use SciPy's bias-corrected estimators; these finite
    sample numbers do not establish the existence of corresponding population
    moments. Variance/std use the n-1 denominator.
    """
    values = np.asarray(sample, dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ValueError("sample must be a nonempty, finite, one-dimensional array")
    n = int(values.size)
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75], method="linear")
    iqr = q3 - q1
    lower_fence, upper_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    inliers = values[(values >= lower_fence) & (values <= upper_fence)]
    outlier_count = n - int(inliers.size)
    nonconstant = bool(np.any(values != values[0]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        skewness = stats.skew(values, bias=False) if n >= 3 and nonconstant else np.nan
        kurtosis = (
            stats.kurtosis(values, fisher=False, bias=False) if n >= 4 and nonconstant else np.nan
        )
    return {
        "n": n,
        "mean": float(np.mean(values)),
        "median": float(median),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_fence": float(lower_fence),
        "upper_fence": float(upper_fence),
        "lower_whisker": float(np.min(inliers)),
        "upper_whisker": float(np.max(inliers)),
        "outlier_count": outlier_count,
        "outlier_fraction": outlier_count / n,
        "std": float(np.std(values, ddof=1)) if n >= 2 else float("nan"),
        "skewness": float(skewness),
        "kurtosis": float(kurtosis),
    }


def _positive_integer(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer")
    if value < 1:
        raise ValueError(f"{name} must be positive")
    return int(value)


def clt_experiment(
    name: str,
    shape: float,
    n: int,
    repetitions: int,
    seed: int,
    *,
    include_first_group: bool = False,
) -> dict:
    """Draw independent groups and return their means and CLT coordinates.

    The usual iid finite-variance CLT coordinate is sqrt(n)*(Xbar-mu)/sigma.
    It is deliberately absent when the population variance is not finite and
    positive. Drawing is batched to bound temporary arrays to ~8 MB. Optionally
    retain the first group (an additional n values) to explain the same run.
    """
    n = _positive_integer(n, "n")
    repetitions = _positive_integer(repetitions, "repetitions")
    rv = make_distribution(name, shape)
    moments = population_moments(rv)
    rng = np.random.default_rng(seed)
    means = np.empty(repetitions, dtype=float)
    first_group = np.empty(n, dtype=float) if include_first_group else None
    batch_size = max(1, min(repetitions, 1_000_000 // min(n, 1_000_000)))
    for start in range(0, repetitions, batch_size):
        count = min(batch_size, repetitions - start)
        sums = np.zeros(count, dtype=float)
        # The inner block also bounds memory for unusually large n.
        width = max(1, 1_000_000 // count)
        for column in range(0, n, width):
            draw_count = min(width, n - column)
            draws = rv.rvs(size=(count, draw_count), random_state=rng)
            if first_group is not None and start == 0:
                first_group[column : column + draw_count] = draws[0]
            sums += np.sum(draws, axis=1)
        means[start : start + count] = sums / n
    mean, variance = moments["mean"], moments["variance"]
    finite_variance = bool(np.isfinite(mean) and np.isfinite(variance) and variance > 0)
    standardized = np.sqrt(n) * (means - mean) / np.sqrt(variance) if finite_variance else None
    return {
        "means": means,
        "standardized": standardized,
        "population_mean": mean,
        "population_variance": variance,
        "finite_variance": finite_variance,
        "first_group": first_group,
    }


def two_level(N: int, q: int) -> dict:
    """Microcanonical counting for N distinguishable, noninteracting sites.

    Each site has energy 0 or epsilon > 0, so E=q*epsilon.  At fixed q every
    compatible configuration is equiprobable and P(site excited)=q/N.
    ``beta_epsilon`` uses the thermodynamic-limit derivative of entropy, not
    an exact finite-difference temperature for finite N.  Its boundary values
    are limits at q=0,N. Entropy per particle is S/(N*k_B).
    """
    N = _positive_integer(N, "N")
    if isinstance(q, (bool, np.bool_)) or not isinstance(q, (int, np.integer)):
        raise ValueError("q must be an integer")
    q = int(q)
    if not 0 <= q <= N:
        raise ValueError("q must lie between 0 and N")
    q_grid = np.arange(N + 1, dtype=int)
    log_multiplicity = (
        special.gammaln(N + 1.0) - special.gammaln(q_grid + 1.0) - special.gammaln(N - q_grid + 1.0)
    )
    # Guarantee exact one-state endpoints and eliminate roundoff asymmetry.
    log_multiplicity = 0.5 * (log_multiplicity + log_multiplicity[::-1])
    log_multiplicity[[0, -1]] = 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        beta_epsilon = np.log((N - q_grid).astype(float)) - np.log(q_grid.astype(float))
    return {
        "q_grid": q_grid,
        "log_multiplicity": log_multiplicity,
        "entropy_per_particle": log_multiplicity / N,
        "beta_epsilon": beta_epsilon,
        "selected_log_multiplicity": float(log_multiplicity[q]),
        "selected_probability": q / N,
    }


def sample_microstate(N: int, q: int, seed: int) -> np.ndarray:
    """Uniformly sample one configuration with exactly q excited sites."""
    # Reuse validation without evaluating the full counting curve.
    N = _positive_integer(N, "N")
    if isinstance(q, (bool, np.bool_)) or not isinstance(q, (int, np.integer)) or not 0 <= q <= N:
        raise ValueError("q must be an integer between 0 and N")
    state = np.zeros(N, dtype=np.int8)
    state[np.random.default_rng(seed).choice(N, size=int(q), replace=False)] = 1
    return state


def histogram_density(values, edges):
    """Density on explicit, possibly nonuniform bins using the full sample count.

    Values outside the bins still contribute to the denominator. The integral
    over these bins is therefore the observed fraction inside the window.
    """
    values = np.asarray(values, dtype=float)
    edges = np.asarray(edges, dtype=float)
    if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
        raise ValueError("Expected a nonempty, finite one-dimensional sample.")
    if (
        edges.ndim != 1
        or len(edges) < 2
        or not np.all(np.isfinite(edges))
        or np.any(np.diff(edges) <= 0)
    ):
        raise ValueError("Bin edges must be finite and strictly increasing.")
    counts, _ = np.histogram(values, bins=edges)
    return counts / (len(values) * np.diff(edges))


def sample_histogram(values, bins=48, bounds=None):
    """Return centers, densities, widths and bounds for a sample's display window.

    The default window spans the central 99% of observations. Constant samples
    receive a nonzero-width window. This convenience function uses uniform bins;
    use histogram_density directly for quantile-spaced or other nonuniform bins.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
        raise ValueError("Expected a nonempty, finite one-dimensional sample.")
    lo, hi = np.quantile(values, [0.005, 0.995]) if bounds is None else bounds
    if not np.isfinite(lo + hi) or hi <= lo:
        lo, hi = float(np.min(values)) - 0.5, float(np.max(values)) + 0.5
    edges = np.linspace(lo, hi, bins + 1)
    return (edges[:-1] + edges[1:]) / 2, histogram_density(values, edges), np.diff(edges), lo, hi
