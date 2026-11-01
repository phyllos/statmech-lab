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


def ideal_gas_speeds(temperature_ratio: float) -> dict:
    """One-particle canonical velocities in a 3D classical ideal gas at rest.

    Mass m and reference temperature T_0 stay fixed. Velocity coordinates are
    u_i = v_i/v_0, with v_0 = sqrt(k_B T_0/m), and theta = T/T_0 > 0.
    A component is Gaussian; the vector magnitude is Maxwell distributed.
    Returned densities are normalized in these dimensionless coordinates and
    keep full support independently of the UI's finite plotting window.
    """
    if (
        isinstance(temperature_ratio, (bool, np.bool_))
        or not isinstance(temperature_ratio, (int, float, np.integer, np.floating))
        or not np.isfinite(temperature_ratio)
        or temperature_ratio <= 0
    ):
        raise ValueError("temperature_ratio must be a positive finite scalar")
    sigma = float(np.sqrt(temperature_ratio))
    return {
        "component": stats.norm(scale=sigma),
        "speed": stats.maxwell(scale=sigma),
        "component_sd": sigma,
        "most_probable_speed": np.sqrt(2.0) * sigma,
        "mean_speed": np.sqrt(8.0 / np.pi) * sigma,
        "rms_speed": np.sqrt(3.0) * sigma,
    }


def two_level_response(theta):
    """Canonical response of independent, nondegenerate 0/epsilon units.

    theta = k_B T / epsilon is a finite, nonnegative scalar or array.
    Zero denotes the T -> 0+ limit. Energy, heat capacity and energy variance
    are normalized by N*epsilon, N*k_B and N*epsilon**2 respectively.
    These canonical results are exact for any N; no Stirling approximation.
    """
    temperature = np.asarray(theta, dtype=float)
    if np.any(~np.isfinite(temperature)) or np.any(temperature < 0):
        raise ValueError("theta must be finite and nonnegative")
    # Only negative exponentials are evaluated. Reciprocal overflow at tiny
    # positive temperatures has the same zero-response limit as theta = 0.
    with np.errstate(over="ignore", divide="ignore", under="ignore"):
        beta = np.divide(1.0, temperature)
        weight = np.exp(-beta)
        log_z = np.log1p(weight)
        excited = weight / (1 + weight)
        variance = excited * (1 - excited)
        finite_beta = np.where(np.isfinite(beta), beta, 1.0)
        log_capacity = 2 * np.log(finite_beta) - finite_beta - 2 * log_z
        capacity = np.where(np.isfinite(beta), np.exp(log_capacity), 0.0)
    return {
        "excited": excited,
        "ground": 1 - excited,
        "energy": excited,
        "heat_capacity": capacity,
        "energy_variance": variance,
        "log_partition": log_z,
    }


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
    """Analytical moments: nan means undefined; inf means divergent.

    A symmetric distribution need not possess a moment-based skewness.  In
    particular, the Cauchy mean, variance, skewness, and kurtosis are undefined.
    Variance is undefined without a finite mean; standardized moments are
    undefined without finite variance. With these prerequisites satisfied, a
    divergent numerator is represented by infinity.
    The UI must not replace these values with zero or a sample estimate.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mean, variance, skewness, excess = rv.stats(moments="mvsk")
    # SciPy uses +inf for the undefined Student t mean, and some standardized
    # moments use nan even when the denominator exists and the numerator diverges.
    # A variance requires a finite mean; skewness/kurtosis require finite variance.
    if rv.dist.name == "t":
        nu = rv.args[0] if rv.args else rv.kwds["df"]
        if nu <= 1:
            mean = variance = skewness = excess = np.nan
        elif nu <= 2:
            variance, skewness, excess = np.inf, np.nan, np.nan
        elif nu <= 4:
            skewness = np.nan if nu <= 3 else 0.0
            excess = np.inf
    elif rv.dist.name == "pareto":
        alpha = rv.args[0] if rv.args else rv.kwds["b"]
        if alpha <= 1:
            mean, variance, skewness, excess = np.inf, np.nan, np.nan, np.nan
        elif alpha <= 2:
            variance, skewness, excess = np.inf, np.nan, np.nan
        elif alpha <= 4:
            if alpha <= 3:
                skewness = np.inf
            excess = np.inf
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
    receive a nonzero-width window. Explicit bounds must be finite and increasing.
    This convenience function uses uniform bins;
    use histogram_density directly for quantile-spaced or other nonuniform bins.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
        raise ValueError("Expected a nonempty, finite one-dimensional sample.")
    bins = _positive_integer(bins, "bins")
    if bounds is None:
        lo, hi = np.quantile(values, [0.005, 0.995])
        if hi <= lo:
            lo, hi = float(np.min(values)) - 0.5, float(np.max(values)) + 0.5
    else:
        window = np.asarray(bounds, dtype=float)
        if window.shape != (2,) or not np.all(np.isfinite(window)) or window[1] <= window[0]:
            raise ValueError("Bounds must contain two finite, strictly increasing values.")
        lo, hi = window
    edges = np.linspace(lo, hi, bins + 1)
    return (edges[:-1] + edges[1:]) / 2, histogram_density(values, edges), np.diff(edges), lo, hi


def gaussian_conditioning(rho: float, y0: float):
    """Return a standard bivariate Gaussian and its conditional law X | Y=y0.

    Both marginals are N(0, 1); |rho| < 1 excludes singular covariance matrices.
    Conditioning on an exact value uses densities, not a finite-width bin.
    Returned SciPy laws retain full support; plotting windows do not normalize them.
    """
    if not np.isfinite(rho) or abs(rho) >= 1:
        raise ValueError("Correlation must be finite and strictly between -1 and 1.")
    if not np.isfinite(y0):
        raise ValueError("The conditioning value must be finite.")
    return {
        "joint": stats.multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]]),
        "marginal": stats.norm(),
        "conditional": stats.norm(loc=rho * y0, scale=np.sqrt((1 - rho) * (1 + rho))),
    }


def thermal_contact(n_a: int, n_b: int, q_total: int) -> dict:
    """Exact equilibrium energy sharing between two weakly coupled two-level systems.

    Both systems have the same gap epsilon. All combined microstates at fixed
    q_total are equiprobable; interaction energy is neglected. This describes
    an equilibrium distribution, not a time evolution or an exchange rate.
    Entropy arrays refer to a *fixed split*, while log_total_multiplicity sums
    over all allowed splits. Log-space normalization avoids count overflow.
    """
    n_a = _positive_integer(n_a, "n_a")
    n_b = _positive_integer(n_b, "n_b")
    if (
        isinstance(q_total, (bool, np.bool_))
        or not isinstance(q_total, (int, np.integer))
        or not 0 <= q_total <= n_a + n_b
    ):
        raise ValueError("q_total must be an integer between 0 and n_a + n_b")
    q_total = int(q_total)
    q_a = np.arange(max(0, q_total - n_b), min(n_a, q_total) + 1, dtype=int)
    q_b = q_total - q_a
    log_a = two_level(n_a, 0)["log_multiplicity"][q_a]
    log_b = two_level(n_b, 0)["log_multiplicity"][q_b]
    entropy = log_a + log_b
    log_total = float(special.logsumexp(entropy))
    probabilities = np.exp(entropy - log_total)
    # Hypergeometric modes from integer arithmetic: preserve exact two-way ties.
    quotient, remainder = divmod((q_total + 1) * (n_a + 1), n_a + n_b + 2)
    candidates = [quotient] if remainder else [quotient - 1, quotient]
    modes = np.array([q for q in candidates if q_a[0] <= q <= q_a[-1]], dtype=int)
    mean = q_total * n_a / (n_a + n_b)
    variance = (
        q_total
        * (n_a / (n_a + n_b))
        * (n_b / (n_a + n_b))
        * (n_a + n_b - q_total)
        / (n_a + n_b - 1)
    )
    return {
        "q_a": q_a,
        "q_b": q_b,
        "log_omega_a": log_a,
        "log_omega_b": log_b,
        "split_entropy": entropy,
        "probabilities": probabilities,
        "log_total_multiplicity": log_total,
        "modes": modes,
        "mean": mean,
        "variance": variance,
    }


def canonical_comparison(n_a: int, n_b: int, q_total: int) -> dict:
    """Compare a finite two-level reservoir with a mean-matched canonical law.

    The exact marginal is hypergeometric, inherited from thermal_contact.
    p = q_total / (n_a + n_b) is the mean excited fraction in either subsystem,
    not a fixed instantaneous bath energy. The canonical law is binomial on
    ALL q_A = 0..n_a; do not truncate it to the finite reservoir's support.
    beta*epsilon = log((1-p)/p) is a thermodynamic temperature parameter,
    not an exact finite-difference derivative of the small reservoir entropy.
    """
    finite = thermal_contact(n_a, n_b, q_total)
    q_a = np.arange(n_a + 1, dtype=int)
    exact = np.zeros(n_a + 1)
    exact[finite["q_a"]] = finite["probabilities"]
    p = q_total / (n_a + n_b)
    canonical = stats.binom.pmf(q_a, n_a, p)
    if p == 0:
        beta_eps = np.inf
    elif p == 1:
        beta_eps = -np.inf
    else:
        beta_eps = float(np.log1p(-p) - np.log(p))
    return {
        "q_a": q_a,
        "exact": exact,
        "canonical": canonical,
        "fraction": p,
        "beta_eps": beta_eps,
        "mean": finite["mean"],
        "exact_variance": finite["variance"],
        "canonical_variance": n_a * p * (1 - p),
        "total_variation": float(0.5 * np.sum(np.abs(exact - canonical))),
    }
