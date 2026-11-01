"""Thermodynamic identities, limiting values and the temperature-control path."""

import itertools
import json
import warnings
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from physics import two_level_response

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("theta", [0.05, 0.4, 1.0, 4.0])
def test_response_matches_enumerated_canonical_microstates(theta):
    n = 5
    energies = np.array([sum(bits) for bits in itertools.product((0, 1), repeat=n)])
    weights = np.exp(-energies / theta)
    probabilities = weights / weights.sum()
    energy = np.dot(energies, probabilities)
    variance = np.dot((energies - energy) ** 2, probabilities)
    data = two_level_response(theta)
    assert data["energy"] == pytest.approx(energy / n)
    assert data["energy_variance"] == pytest.approx(variance / n)
    assert data["heat_capacity"] == pytest.approx(variance / n / theta**2)
    assert data["log_partition"] == pytest.approx(np.log(weights.sum()) / n)
    assert data["ground"] + data["excited"] == pytest.approx(1)


def test_heat_capacity_is_energy_slope_and_energy_is_log_partition_derivative():
    theta = np.geomspace(0.05, 100, 50)
    h = theta * 1e-5
    slope = (two_level_response(theta + h)["energy"] - two_level_response(theta - h)["energy"]) / (
        2 * h
    )
    np.testing.assert_allclose(slope, two_level_response(theta)["heat_capacity"], rtol=1e-7)
    beta = 1 / theta
    delta = beta * 1e-5
    energy = -(
        two_level_response(1 / (beta + delta))["log_partition"]
        - two_level_response(1 / (beta - delta))["log_partition"]
    ) / (2 * delta)
    np.testing.assert_allclose(energy, two_level_response(theta)["energy"], rtol=1e-7)


def test_limits_and_extreme_temperatures_are_finite_without_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        data = two_level_response([0, np.nextafter(0.0, 1.0), 1e-10, 1e8, 1e308])
    for values in data.values():
        assert np.all(np.isfinite(values))
    np.testing.assert_array_equal(data["energy"][:3], 0)
    np.testing.assert_array_equal(data["heat_capacity"][:3], 0)
    assert data["energy"][-1] == pytest.approx(0.5)
    assert data["energy_variance"][-1] == pytest.approx(0.25)
    assert data["heat_capacity"][-2] == pytest.approx(0.25e-16, rel=1e-7, abs=0)
    assert data["log_partition"][-1] == pytest.approx(np.log(2))


def test_single_smooth_peak_and_monotonic_energy():
    theta = np.linspace(0, 4, 4001)
    data = two_level_response(theta)
    peak = np.argmax(data["heat_capacity"])
    assert theta[peak] == pytest.approx(0.417, abs=0.001)
    assert np.all(np.diff(data["energy"]) >= 0)
    assert np.all(np.diff(data["heat_capacity"][: peak + 1]) >= 0)
    assert np.all(np.diff(data["heat_capacity"][peak:]) <= 0)


@pytest.mark.parametrize("theta", [-1, np.nan, np.inf, -np.inf, [0.5, -0.1]])
def test_invalid_temperature(theta):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        two_level_response(theta)


def _figures(app):
    return [json.loads(element.proto.spec) for element in app.get("plotly_chart")]


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_bilingual_temperature_navigation_and_zero_limit(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "response", "lang": lang}
    app.run()
    assert not app.exception
    assert len(app.slider) == 1
    assert len(_figures(app)) == len(app.get("download_button")) == 2
    initial = _figures(app)
    app.slider(key="response_theta").set_value(4.0).run()
    changed = _figures(app)
    assert changed[0]["data"][0]["y"] != initial[0]["data"][0]["y"]
    assert changed[1]["data"][1]["x"] == changed[1]["data"][3]["x"] == [4.0]
    for fig in changed:
        assert "k_B T / ε = 4" in fig["layout"]["title"]["subtitle"]["text"]
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    assert app.query_params["lab"] == "response"
    assert app.slider(key="response_theta").value == 4.0
    app.radio(key=f"nav_{other}").set_value("glossary").run()
    app.radio(key=f"nav_{other}").set_value("response").run()
    assert app.slider(key="response_theta").value == 4.0
    app.slider(key="response_theta").set_value(0.0).run()
    figures = _figures(app)
    assert figures[0]["data"][0]["y"] == [1.0, 0.0]
    assert figures[1]["data"][1]["y"] == figures[1]["data"][3]["y"] == [0.0]
    assert figures[0]["layout"]["title"]["subtitle"]["text"] == "T → 0⁺"
    app.toggle(key="panel_open_response").set_value(False).run()
    assert len(_figures(app)) == 2
    assert not app.exception


def test_related_terms_and_subplot_linking(monkeypatch):
    from glossary import RELATED_IDS, search_terms
    from labs import response
    from plot_theme import COLORS

    monkeypatch.setattr(response, "tr", lambda en, zh: en)
    fig = response._response_figure(0.4, two_level_response(0.4))
    assert fig.layout.xaxis.matches == "x2"
    assert all(trace.line.color != COLORS["sample"] for trace in fig.data)
    assert "heat_capacity" in RELATED_IDS["response"]
    assert "energy_fluctuation" in {t["id"] for t in search_terms("涨落", "response")}
