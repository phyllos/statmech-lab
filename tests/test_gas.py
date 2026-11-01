"""Ideal-gas normalization, shell geometry and temperature interactions."""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from streamlit.testing.v1 import AppTest

from physics import ideal_gas_speeds

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("theta", [0.25, 1.0, 4.0])
def test_normalization_shell_geometry_and_kinetic_energy(theta):
    data = ideal_gas_speeds(theta)
    component, speed = data["component"], data["speed"]
    assert quad(component.pdf, -np.inf, np.inf)[0] == pytest.approx(1)
    assert quad(speed.pdf, 0, np.inf)[0] == pytest.approx(1)
    v = np.linspace(0, 8, 101)
    # The shell collects the isotropic joint density at (v, 0, 0).
    np.testing.assert_allclose(
        speed.pdf(v),
        4 * np.pi * v**2 * component.pdf(v) * component.pdf(0) ** 2,
        atol=1e-15,
    )
    assert component.mean() == 0
    assert component.var() == pytest.approx(theta)
    assert quad(lambda v: v**2 * speed.pdf(v), 0, np.inf)[0] == pytest.approx(3 * theta)
    assert quad(lambda v: v * speed.pdf(v), 0, np.inf)[0] == pytest.approx(data["mean_speed"])
    assert data["rms_speed"] ** 2 == pytest.approx(3 * theta)
    mode = data["most_probable_speed"]
    assert speed.pdf(mode) > speed.pdf(mode - 0.01)
    assert speed.pdf(mode) > speed.pdf(mode + 0.01)
    assert speed.pdf(0) == speed.pdf(-1) == 0
    assert component.pdf(0) > component.pdf(0.01)


def test_temperature_scaling_broadens_and_preserves_area():
    cold, hot = ideal_gas_speeds(1), ideal_gas_speeds(4)
    x = np.linspace(-8, 8, 201)
    for kind in ("component", "speed"):
        np.testing.assert_allclose(hot[kind].pdf(2 * x), cold[kind].pdf(x) / 2)
    for name in ("component_sd", "most_probable_speed", "mean_speed", "rms_speed"):
        assert hot[name] == pytest.approx(2 * cold[name])


@pytest.mark.parametrize("theta", [0, -1, np.nan, np.inf, -np.inf, True, [1], "1"])
def test_invalid_temperature(theta):
    with pytest.raises(ValueError, match="positive finite scalar"):
        ideal_gas_speeds(theta)


def _figures(app):
    return [json.loads(element.proto.spec) for element in app.get("plotly_chart")]


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_bilingual_temperature_control_exports_and_navigation(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "gas", "lang": lang}
    app.run()
    assert not app.exception
    assert len(app.slider) == 1
    assert len(_figures(app)) == len(app.get("download_button")) == 2
    app.slider(key="gas_temperature").set_value(0.25).run()
    cold = _figures(app)
    app.slider(key="gas_temperature").set_value(4.0).run()
    hot = _figures(app)
    for initial, changed in zip(cold, hot, strict=True):
        assert initial["data"][0]["y"] != changed["data"][0]["y"]
        assert initial["layout"]["xaxis"]["range"] == changed["layout"]["xaxis"]["range"]
        assert initial["layout"]["yaxis"]["range"] == changed["layout"]["yaxis"]["range"]
        assert "T/T₀ = 4" in changed["layout"]["title"]["subtitle"]["text"]
        assert "v₀ = √(k_B T₀ / m)" in changed["layout"]["title"]["subtitle"]["text"]
    assert hot[0]["data"][1]["x"] == [0.0]
    assert hot[1]["data"][1]["x"] == pytest.approx([np.sqrt(8)])
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    assert app.query_params["lab"] == "gas"
    assert app.slider(key="gas_temperature").value == 4.0
    assert _figures(app)[0]["data"][0]["y"] == hot[0]["data"][0]["y"]
    app.radio(key=f"nav_{other}").set_value("glossary").run()
    app.radio(key=f"nav_{other}").set_value("gas").run()
    assert app.slider(key="gas_temperature").value == 4.0
    app.toggle(key="panel_open_gas").set_value(False).run()
    assert len(_figures(app)) == 2
    assert not app.exception


def test_theoretical_figures_and_reference_terms(monkeypatch):
    from glossary import RELATED_IDS, search_terms
    from labs import gas
    from plot_theme import COLORS

    monkeypatch.setattr(gas, "tr", lambda en, zh: en)
    component, speed = gas._figures(ideal_gas_speeds(1))
    assert component.layout.xaxis.range == (-8, 8)
    assert speed.layout.xaxis.range == (0, 8)
    assert all(fig.data[0].line.color == COLORS["theory"] for fig in (component, speed))
    assert "maxwell_speed" in RELATED_IDS["gas"]
    assert "maxwell_speed" in {term["id"] for term in search_terms("球壳", "gas")}
    assert set(RELATED_IDS["gas"]) <= {term["id"] for term in search_terms(category="gas")}
