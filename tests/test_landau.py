"""Landau extrema, degeneracies and the bilingual equilibrium interaction."""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import minimize_scalar
from streamlit.testing.v1 import AppTest

from physics import landau_free_energy, landau_stationary

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_zero_field_minima_critical_point_and_barrier():
    for t in (0.5, 0.75, 0.99):
        data = landau_stationary(t)
        np.testing.assert_allclose(data["m"], [-np.sqrt(1 - t), 0, np.sqrt(1 - t)])
        assert data["kind"] == ("stable", "unstable", "stable")
        np.testing.assert_allclose(data["free_energy"][[0, 2]], -((1 - t) ** 2) / 4)
        np.testing.assert_allclose(data["curvature"], [2 * (1 - t), t - 1, 2 * (1 - t)])
    critical = landau_stationary(1)
    assert critical["kind"] == ("critical",)
    assert critical["curvature"][0] == 0
    assert critical["equilibrium"].tolist() == [0]
    assert landau_free_energy(0.01, 1) > landau_free_energy(0, 1)
    assert landau_stationary(1.5)["kind"] == ("stable",)


@pytest.mark.parametrize("sign", [-1, 1])
def test_spinodal_is_distinct_from_critical_minimum(sign):
    t = 0.75
    a = np.sqrt((1 - t) / 3)
    h = sign * 2 * a**3
    data = landau_stationary(t, h)
    assert len(data["m"]) == 2
    assert set(data["kind"]) == {"stable", "spinodal"}
    np.testing.assert_allclose(data["equilibrium"], [sign * 2 * a])
    inflection = data["m"][data["kind"].index("spinodal")]
    assert inflection == pytest.approx(-sign * a)
    assert len(landau_stationary(t, h * (1 - 1e-7))["m"]) == 3
    assert len(landau_stationary(t, h * (1 + 1e-7))["m"]) == 1


@pytest.mark.parametrize("t,h", [(0.5, 0.02), (0.75, -0.02), (1, 0.2), (1.5, -0.2), (1.5, 1e-20)])
def test_global_equilibrium_matches_independent_minimization(t, h):
    data = landau_stationary(t, h)
    assert len(data["equilibrium"]) == 1
    m = data["equilibrium"][0]
    minima = [
        minimize_scalar(lambda x: landau_free_energy(x, t, h), bounds=bounds, method="bounded")
        for bounds in [(-2, 0), (0, 2)]
    ]
    assert landau_free_energy(m, t, h) == pytest.approx(
        min(result.fun for result in minima), abs=1e-10
    )
    np.testing.assert_allclose(data["m"] ** 3 + (t - 1) * data["m"] - h, 0, atol=1e-12)
    reflected = landau_stationary(t, -h)
    np.testing.assert_allclose(reflected["m"], -data["m"][::-1], atol=1e-12)
    assert reflected["kind"] == data["kind"][::-1]


def test_all_slider_settings_have_visible_equilibria_and_finite_energies():
    for t in np.linspace(0.5, 1.5, 101):
        for h in np.linspace(-0.2, 0.2, 41):
            data = landau_stationary(t, h)
            assert len(data["equilibrium"]) >= 1
            assert np.all(np.abs(data["m"]) < 1.15)
            assert np.all(np.isfinite(data["free_energy"]))
            np.testing.assert_allclose(data["m"] ** 3 + (t - 1) * data["m"] - h, 0, atol=1e-12)


@pytest.mark.parametrize("t,h", [(0, 0), (-1, 0), (np.nan, 0), (1, np.inf), (True, 0), (1, [0])])
def test_invalid_parameters(t, h):
    with pytest.raises(ValueError):
        landau_stationary(t, h)


def _figures(app):
    return [json.loads(element.proto.spec) for element in app.get("plotly_chart")]


def test_equilibrium_branches_share_legend_and_reference_category(monkeypatch):
    from glossary import RELATED_IDS, search_terms
    from labs import landau

    monkeypatch.setattr(landau, "tr", lambda en, zh: en)
    figure = landau._equilibrium(0.5, 0, landau_stationary(0.5))
    assert {trace.legendgroup for trace in figure.data[:-1]} == {"equilibrium"}
    assert figure.layout.legend.groupclick == "togglegroup"
    assert figure.data[-1].cliponaxis is False
    np.testing.assert_allclose(figure.data[-1].y, [-np.sqrt(0.5), np.sqrt(0.5)])
    assert set(RELATED_IDS["landau"]) <= {term["id"] for term in search_terms(category="landau")}


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_temperature_field_navigation_and_exports(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "landau", "lang": lang}
    app.run()
    assert not app.exception
    assert len(_figures(app)) == len(app.get("download_button")) == 2
    assert app.slider(key="landau_field").value == 0
    app.slider(key="landau_temperature").set_value(1.0).run()
    assert len(_figures(app)[0]["data"]) == 2
    app.slider(key="landau_temperature").set_value(0.5).run()
    app.slider(key="landau_field").set_value(0.02).run()
    assert len(_figures(app)[0]["data"]) == 4
    for figure in _figures(app):
        subtitle = figure["layout"]["title"]["subtitle"]["text"]
        assert "h = 0.02" in subtitle
        assert "m⁴/4" in subtitle
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    assert app.query_params["lab"] == "landau"
    app.radio(key=f"nav_{other}").set_value("glossary").run()
    app.radio(key=f"nav_{other}").set_value("landau").run()
    assert app.slider(key="landau_temperature").value == 0.5
    assert app.slider(key="landau_field").value == 0.02
    app.button[0].click().run()
    assert app.slider(key="landau_field").value == 0
    app.toggle(key="panel_open_landau").set_value(False).run()
    assert len(_figures(app)) == 2
    assert not app.exception
