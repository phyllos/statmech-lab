"""Exact combinatorial checks and complete thermal-contact learning paths."""

import json
import math
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from glossary import search_terms
from physics import thermal_contact

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize(
    "n_a,n_b,q", [(1, 1, 0), (1, 1, 1), (2, 3, 4), (20, 60, 20), (120, 120, 120), (4, 7, 11)]
)
def test_probability_matches_exact_integer_counts(n_a, n_b, q):
    data = thermal_contact(n_a, n_b, q)
    counts = [
        math.comb(n_a, int(a)) * math.comb(n_b, int(b))
        for a, b in zip(data["q_a"], data["q_b"], strict=True)
    ]
    total = math.comb(n_a + n_b, q)
    assert sum(counts) == total
    np.testing.assert_allclose(data["probabilities"], [c / total for c in counts], rtol=1e-11)
    assert data["probabilities"].sum() == pytest.approx(1)
    assert data["log_total_multiplicity"] == pytest.approx(math.log(total))
    np.testing.assert_allclose(data["split_entropy"], [math.log(c) for c in counts], atol=1e-11)
    np.testing.assert_array_equal(data["q_a"] + data["q_b"], q)
    expected_modes = [int(a) for a, c in zip(data["q_a"], counts, strict=True) if c == max(counts)]
    assert data["modes"].tolist() == expected_modes
    mean = np.dot(data["q_a"], data["probabilities"])
    variance = np.dot((data["q_a"] - mean) ** 2, data["probabilities"])
    assert data["mean"] == pytest.approx(mean)
    assert data["variance"] == pytest.approx(variance)


def test_exchange_symmetry_and_large_counts():
    a = thermal_contact(17, 39, 43)
    b = thermal_contact(39, 17, 43)
    np.testing.assert_array_equal(a["q_a"], b["q_b"][::-1])
    np.testing.assert_allclose(a["probabilities"], b["probabilities"][::-1])
    large = thermal_contact(1000, 1000, 1000)
    assert np.all(np.isfinite(large["probabilities"]))
    assert np.all(np.isfinite(large["split_entropy"]))
    assert large["probabilities"].sum() == pytest.approx(1)
    assert large["log_total_multiplicity"] > math.log(np.finfo(float).max)


def test_two_modes_and_non_equal_energy_sharing():
    assert thermal_contact(4, 4, 3)["modes"].tolist() == [1, 2]
    unequal = thermal_contact(20, 60, 20)
    assert unequal["mean"] == 5
    assert unequal["modes"].tolist() == [5]


@pytest.mark.parametrize(
    "args",
    [
        (0, 4, 2),
        (4, -1, 2),
        (True, 4, 2),
        (4.5, 4, 2),
        (4, 4, -1),
        (4, 4, 9),
        (4, 4, 2.5),
        (4, 4, True),
    ],
)
def test_invalid_inputs(args):
    with pytest.raises(ValueError):
        thermal_contact(*args)


def _figures(app):
    return [json.loads(c.proto.spec) for c in app.get("plotly_chart")]


def _values(app):
    return [
        [{k: t[k] for k in ("x", "y", "customdata") if k in t} for t in f["data"]]
        for f in _figures(app)
    ]


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_selection_language_navigation_and_boundaries(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "thermal", "lang": lang}
    app.run()
    assert not app.exception
    assert len(_figures(app)) == 2
    assert len(app.get("download_button")) == 1
    assert not app.button
    for figure in _figures(app):
        subtitle = figure["layout"]["title"]["subtitle"]["text"]
        assert "N_A = 20 · N_B = 60 · q = 20" in subtitle
    assert any("Ω_A(q_A = 5)" in e.value for e in app.markdown)
    initial = _values(app)
    app.slider(key="thermal_q_a").set_value(12).run()
    changed = _values(app)
    # Inspecting a split moves highlights but leaves the underlying law unchanged.
    assert initial[0][0] == changed[0][0]
    assert initial[0][1] != changed[0][1]
    assert initial[1][:3] == changed[1][:3]
    assert changed[0][1]["x"] == changed[1][-1]["x"] == [12]
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    assert app.query_params["lab"] == "thermal"
    assert _values(app) == changed
    app.radio(key=f"nav_{other}").set_value("glossary").run()
    app.radio(key=f"nav_{other}").set_value("thermal").run()
    assert _values(app) == changed
    for q in (0, 80):
        app.slider(key="thermal_q_total").set_value(q).run()
        assert not app.exception
        assert not any(s.key == "thermal_q_a" for s in app.slider)
        assert app.session_state["thermal_q_a"] == (0 if q == 0 else 20)
        probability, entropy = _figures(app)
        assert probability["data"][0]["width"] == 0.35
        assert probability["data"][-1]["y"] == [1.0]
        assert entropy["data"][-1]["y"] == [0.0]
        assert entropy["layout"]["yaxis"]["range"][0] < 0
        annotation = entropy["layout"]["annotations"][0]["text"]
        assert ("唯一微观态" if other == "zh" else "One microstate") in annotation
        assert "S_A = S_B = 0" in annotation
        for figure in (probability, entropy):
            assert f"q = {q}" in figure["layout"]["title"]["subtitle"]["text"]
    # Returning from a boundary restores regular plots without the singleton note.
    app.slider(key="thermal_q_total").set_value(79).run()
    probability, entropy = _figures(app)
    assert not entropy["layout"].get("annotations")
    assert "width" not in probability["data"][0]
    assert app.slider(key="thermal_q_a").min == 19
    app.slider(key="thermal_q_total").set_value(80).run()
    # Shrinking both systems clamps total excitation and the selected split.
    app.slider(key="thermal_n_a").set_value(4).run()
    app.slider(key="thermal_n_b").set_value(4).run()
    assert app.slider(key="thermal_q_total").value == 8
    assert app.session_state["thermal_q_a"] == 4
    app.slider(key="thermal_q_total").set_value(3).run()
    assert app.slider(key="thermal_q_a").value == 3
    assert any("1, 2" in e.value for e in app.markdown)
    assert not app.exception


def test_reference_terms_are_searchable():
    assert "energy_sharing" in {t["id"] for t in search_terms("超几何", "thermal")}
    assert "thermal_contact" in {t["id"] for t in search_terms("Thermal contact", "thermal")}
