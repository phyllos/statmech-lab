"""Checks anchored in normalization, known laws, and exact small systems."""

import itertools
import math

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import logsumexp

from physics import (
    DISTRIBUTIONS,
    clt_experiment,
    make_distribution,
    population_moments,
    sample_microstate,
    sample_summary,
    two_level,
)


@pytest.mark.parametrize("name", DISTRIBUTIONS)
@pytest.mark.parametrize("align", [False, True])
def test_probability_normalizes_and_cdf_inverts(name, align):
    rv = make_distribution(name, shape=2.5, align=align)
    lower, upper = rv.support()
    mass, _ = quad(rv.pdf, lower, upper, epsabs=1e-8, limit=250)
    assert mass == pytest.approx(1.0, abs=3e-7)
    probabilities = np.array([0.01, 0.25, 0.5, 0.75, 0.99])
    np.testing.assert_allclose(rv.cdf(rv.ppf(probabilities)), probabilities, atol=1e-11)


@pytest.mark.parametrize("name", DISTRIBUTIONS)
def test_robust_alignment_preserves_probability_and_jacobian(name):
    raw = make_distribution(name, shape=2.5)
    aligned = make_distribution(name, shape=2.5, align=True)
    q1, median, q3 = raw.ppf([0.25, 0.5, 0.75])
    width = q3 - q1
    assert aligned.median() == pytest.approx(0.0, abs=1e-12)
    assert aligned.ppf(0.75) - aligned.ppf(0.25) == pytest.approx(1.0)
    x = raw.ppf(np.linspace(0.02, 0.98, 40))
    y = (x - median) / width
    np.testing.assert_allclose(aligned.pdf(y), width * raw.pdf(x), rtol=1e-10, atol=1e-12)


def test_known_normal_moments_and_symmetric_cauchy_undefined_moments():
    normal = population_moments(make_distribution("normal"))
    assert normal == pytest.approx(
        {"mean": 0, "variance": 1, "skewness": 0, "kurtosis": 3, "excess_kurtosis": 0}
    )
    cauchy = population_moments(make_distribution("cauchy"))
    assert all(not np.isfinite(value) for value in cauchy.values())


@pytest.mark.parametrize("alpha", [0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
def test_pareto_moment_thresholds(alpha):
    moments = population_moments(make_distribution("pareto", alpha))
    for key, threshold in [("mean", 1), ("variance", 2), ("skewness", 3), ("kurtosis", 4)]:
        assert np.isfinite(moments[key]) == (alpha > threshold)
    if alpha > 2:
        assert moments["mean"] == pytest.approx(alpha / (alpha - 1))
        assert moments["variance"] == pytest.approx(alpha / ((alpha - 1) ** 2 * (alpha - 2)))


def test_boxplot_fences_are_not_whiskers():
    values = np.array([0, 1, 2, 3, 4, 5, 100], dtype=float)
    result = sample_summary(values)
    assert result["q1"] == 1.5
    assert result["q3"] == 4.5
    assert result["lower_fence"] == -3
    assert result["upper_fence"] == 9
    assert result["lower_whisker"] == 0
    assert result["upper_whisker"] == 5
    assert result["outlier_count"] == 1
    assert result["outlier_fraction"] == pytest.approx(1 / 7)
    assert result["std"] == pytest.approx(math.sqrt(sum((values - values.mean()) ** 2) / 6))


def test_small_and_constant_samples_do_not_invent_shape_statistics():
    result = sample_summary([3, 3, 3, 3])
    assert result["iqr"] == 0
    assert result["lower_whisker"] == result["upper_whisker"] == 3
    assert np.isnan(result["skewness"])
    assert np.isnan(result["kurtosis"])
    assert np.isnan(sample_summary([1])["std"])
    with pytest.raises(ValueError):
        sample_summary([1, np.nan])


def test_clt_has_correct_scaling_and_reproducible_samples():
    n, repetitions = 64, 12000
    result = clt_experiment("exponential", 3, n, repetitions, 42)
    assert result["finite_variance"]
    assert np.mean(result["means"]) == pytest.approx(1.0, abs=0.005)
    assert np.std(result["means"], ddof=1) == pytest.approx(1 / np.sqrt(n), rel=0.04)
    assert np.mean(result["standardized"]) == pytest.approx(0, abs=0.04)
    assert np.std(result["standardized"]) == pytest.approx(1, rel=0.04)
    replay = clt_experiment("exponential", 3, n, repetitions, 42)
    np.testing.assert_array_equal(result["means"], replay["means"])


@pytest.mark.parametrize("name,shape", [("cauchy", 3), ("pareto", 2.0), ("student_t", 1.5)])
def test_infinite_variance_never_gets_a_finite_variance_clt_coordinate(name, shape):
    result = clt_experiment(name, shape, n=32, repetitions=200, seed=9)
    assert not result["finite_variance"]
    assert result["standardized"] is None


def test_cauchy_sample_means_remain_cauchy_in_scale():
    result = clt_experiment("cauchy", 3, n=32, repetitions=12000, seed=42)
    q1, q3 = np.quantile(result["means"], [0.25, 0.75])
    assert q3 - q1 == pytest.approx(2.0, rel=0.08)


def test_two_level_counting_agrees_with_enumeration():
    N = 8
    exact = np.bincount([sum(s) for s in itertools.product((0, 1), repeat=N)], minlength=N + 1)
    result = two_level(N, 3)
    np.testing.assert_allclose(result["log_multiplicity"], np.log(exact), atol=1e-12)
    assert result["selected_log_multiplicity"] == pytest.approx(math.log(math.comb(8, 3)))
    assert result["selected_probability"] == 3 / 8


def test_two_level_symmetry_endpoints_and_total_states():
    result = two_level(1000, 500)
    np.testing.assert_array_equal(result["log_multiplicity"], result["log_multiplicity"][::-1])
    assert result["log_multiplicity"][0] == result["log_multiplicity"][-1] == 0
    assert logsumexp(result["log_multiplicity"]) == pytest.approx(1000 * math.log(2), abs=1e-9)
    assert result["beta_epsilon"][500] == 0
    assert result["beta_epsilon"][0] == np.inf
    assert result["beta_epsilon"][-1] == -np.inf
    assert np.all(result["beta_epsilon"][1:500] > 0)
    assert np.all(result["beta_epsilon"][501:-1] < 0)


@pytest.mark.parametrize("q", [0, 1, 37, 64])
def test_microstates_obey_the_fixed_energy_constraint(q):
    state = sample_microstate(64, q, 15)
    assert state.shape == (64,)
    assert state.sum() == q
    assert set(state).issubset({0, 1})
    np.testing.assert_array_equal(state, sample_microstate(64, q, 15))


def test_invalid_inputs_fail_explicitly():
    with pytest.raises(ValueError):
        make_distribution("pareto", 0)
    with pytest.raises(ValueError):
        two_level(10, 11)
    with pytest.raises(ValueError):
        two_level(0, 0)
    with pytest.raises(ValueError):
        clt_experiment("normal", 3, n=0, repetitions=100, seed=1)


def test_histogram_density_preserves_total_count_outside_nonuniform_bins():
    from physics import histogram_density

    values = np.array([-10.0, 0.0, 0.5, 1.5, 2.0, 3.0, 10.0])
    edges = np.array([0.0, 1.0, 3.0])
    density = histogram_density(values, edges)
    np.testing.assert_allclose(density, [2 / 7, 3 / 14])
    assert np.sum(density * np.diff(edges)) == pytest.approx(5 / 7)


def test_sample_histogram_shared_bins_and_constant_samples():
    from physics import sample_histogram

    x, density, widths, lo, hi = sample_histogram([2.0, 2.0, 2.0], bins=4)
    assert (lo, hi) == (1.5, 2.5)
    assert np.sum(density * widths) == pytest.approx(1.0)
    current = sample_histogram([0.0, 1.0, 2.0, 3.0], bins=3, bounds=(0.0, 3.0))
    saved = sample_histogram([-100.0, 0.0, 1.0, 2.0, 3.0, 100.0], bins=3, bounds=(0.0, 3.0))
    np.testing.assert_array_equal(current[0], saved[0])
    np.testing.assert_array_equal(current[2], saved[2])
    assert np.sum(saved[1] * saved[2]) == pytest.approx(4 / 6)


@pytest.mark.parametrize(
    "sample,edges", [([], [0, 1]), ([np.nan], [0, 1]), ([1], [1, 1]), ([1], [1, 0])]
)
def test_histogram_density_rejects_invalid_input(sample, edges):
    from physics import histogram_density

    with pytest.raises(ValueError):
        histogram_density(sample, edges)


@pytest.mark.parametrize("align", [False, True])
@pytest.mark.parametrize("nu", [0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
def test_student_t_moments_distinguish_undefined_and_divergent(nu, align):
    moments = population_moments(make_distribution("student_t", nu, align=align))
    if nu <= 1:
        assert all(np.isnan(v) for v in moments.values())
    else:
        assert moments["mean"] == pytest.approx(0, abs=1e-12)
        if nu <= 2:
            assert moments["variance"] == np.inf
            assert np.isnan(moments["kurtosis"])
        elif nu <= 4:
            assert moments["kurtosis"] == np.inf
        if nu <= 3:
            assert np.isnan(moments["skewness"])
        else:
            assert moments["skewness"] == 0


@pytest.mark.parametrize("alpha", [0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
def test_pareto_divergence_requires_defined_lower_moments(alpha):
    moments = population_moments(make_distribution("pareto", alpha))
    if alpha <= 1:
        assert moments["mean"] == np.inf
        assert np.isnan(moments["variance"])
    elif alpha <= 2:
        assert moments["variance"] == np.inf
    if alpha <= 2:
        assert np.isnan(moments["skewness"])
        assert np.isnan(moments["kurtosis"])
    else:
        assert moments["kurtosis"] == np.inf
        if alpha <= 3:
            assert moments["skewness"] == np.inf


@pytest.mark.parametrize("bounds", [(2, 1), (1, 1), (0, np.inf), (np.nan, 1), (0,), (0, 1, 2)])
def test_histogram_rejects_invalid_explicit_bounds(bounds):
    from physics import sample_histogram

    with pytest.raises(ValueError, match="Bounds"):
        sample_histogram([0, 1, 2], bounds=bounds)
