"""Numerical and application regressions for Gaussian conditioning."""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from streamlit.testing.v1 import AppTest

from glossary import search_terms
from physics import gaussian_conditioning

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("rho,y0", [(0, 2), (0.6, 1.5), (-0.8, 2), (0.95, -3)])
def test_conditional_is_normalized_joint_slice(rho, y0):
    model = gaussian_conditioning(rho, y0)
    joint, marginal, conditional = (model[k] for k in ("joint", "marginal", "conditional"))
    # Independently integrate the joint slice, then verify the density ratio.
    mass = quad(lambda x: joint.pdf([x, y0]), -np.inf, np.inf)[0]
    assert mass == pytest.approx(marginal.pdf(y0), rel=1e-8)
    for x in [-2, 0, 1.2]:
        assert conditional.pdf(x) == pytest.approx(joint.pdf([x, y0]) / mass, rel=1e-8)
    assert quad(conditional.pdf, -np.inf, np.inf)[0] == pytest.approx(1)
    assert quad(lambda x: x * conditional.pdf(x), -np.inf, np.inf)[0] == pytest.approx(
        rho * y0, abs=1e-9
    )
    assert quad(lambda x: (x - rho * y0) ** 2 * conditional.pdf(x), -np.inf, np.inf)[
        0
    ] == pytest.approx(1 - rho**2)
    for x in [-1, 0.5]:
        integrated = quad(lambda y: joint.pdf([x, y]), -np.inf, np.inf)[0]
        assert integrated == pytest.approx(marginal.pdf(x))


def test_zero_correlation_and_sign_symmetry():
    x = np.linspace(-4, 4, 101)
    independent = gaussian_conditioning(0, 3)
    np.testing.assert_allclose(independent["conditional"].pdf(x), independent["marginal"].pdf(x))
    positive = gaussian_conditioning(0.7, 2)["conditional"]
    negative = gaussian_conditioning(-0.7, 2)["conditional"]
    np.testing.assert_allclose(positive.pdf(x), negative.pdf(-x))


@pytest.mark.parametrize(
    "rho,y0", [(1, 0), (-1, 0), (1.1, 0), (np.nan, 0), (np.inf, 0), (0, np.nan), (0, np.inf)]
)
def test_invalid_model_inputs(rho, y0):
    with pytest.raises(ValueError):
        gaussian_conditioning(rho, y0)


def _data(app):
    return [
        [{k: t[k] for k in ("x", "y", "z") if k in t} for t in json.loads(c.proto.spec)["data"]]
        for c in app.get("plotly_chart")
    ]


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_joint_controls_navigation_and_export(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "joint", "lang": lang}
    app.run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 2
    assert len(app.get("download_button")) == 1
    expected_label = (
        "Download conditional density comparison · HTML"
        if lang == "en"
        else "下载条件密度对照图 · HTML"
    )
    assert app.get("download_button")[0].proto.label == expected_label
    assert not app.button  # No random sampling action in this exact model.
    assert app.toggle(key="panel_open_joint").value
    before = _data(app)
    app.slider(key="joint_rho").set_value(-0.8).run()
    app.slider(key="joint_y0").set_value(2.0).run()
    changed = _data(app)
    assert before != changed
    # Marginal density stays fixed while the conditional density changes.
    assert before[1][1] == changed[1][1]
    assert before[1][0] != changed[1][0]
    app.toggle(key="panel_open_joint").set_value(False).run()
    assert _data(app) == changed
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    assert app.session_state["active_lab"] == "joint"
    assert app.query_params["lab"] == "joint"
    assert _data(app) == changed
    app.radio(key=f"nav_{other}").set_value("glossary").run()
    app.radio(key=f"nav_{other}").set_value("joint").run()
    assert _data(app) == changed
    assert app.slider(key="joint_rho").value == -0.8
    assert app.slider(key="joint_y0").value == 2.0
    assert not app.toggle(key="panel_open_joint").value
    app.slider(key="joint_rho").set_value(0.0).run()
    assert any("independent" in m.value or "独立" in m.value for m in app.markdown)
    assert not app.exception


def test_joint_glossary_search_in_both_languages():
    for query in ("Conditional density", "条件密度"):
        assert "conditional_density" in {t["id"] for t in search_terms(query, "joint")}
    assert len(search_terms(category="joint")) == 4
