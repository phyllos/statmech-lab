"""Check the finite-reservoir limit and the bilingual exploration path."""

import json
import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from glossary import search_terms
from physics import canonical_comparison

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("n_a,n_b,q", [(2, 3, 1), (8, 4, 9), (20, 40, 15), (40, 20, 3)])
def test_exact_counting_and_canonical_microstate_weights(n_a, n_b, q):
    data = canonical_comparison(n_a, n_b, q)
    counts = [
        math.comb(n_a, a) * math.comb(n_b, q - a) if 0 <= q - a <= n_b else 0
        for a in range(n_a + 1)
    ]
    np.testing.assert_allclose(data["exact"], np.array(counts) / math.comb(n_a + n_b, q))
    # Independent Boltzmann calculation includes degeneracy, not just exp(-beta E).
    weights = np.array(
        [math.comb(n_a, a) * math.exp(-data["beta_eps"] * a) for a in range(n_a + 1)]
    )
    np.testing.assert_allclose(data["canonical"], weights / weights.sum(), rtol=1e-12)
    for key, variance in [("exact", "exact_variance"), ("canonical", "canonical_variance")]:
        probability = data[key]
        assert probability.sum() == pytest.approx(1)
        assert np.dot(data["q_a"], probability) == pytest.approx(data["mean"])
        assert np.dot((data["q_a"] - data["mean"]) ** 2, probability) == pytest.approx(
            data[variance]
        )
    assert data["exact_variance"] < data["canonical_variance"]
    # TV also equals the maximum event-probability difference (positive part).
    assert data["total_variation"] == pytest.approx(
        np.maximum(data["exact"] - data["canonical"], 0).sum()
    )


def test_canonical_tail_is_not_truncated_to_finite_support():
    data = canonical_comparison(20, 20, 2)
    assert not np.any(data["exact"][3:])
    assert data["canonical"][3:].sum() > 0.05
    assert data["canonical"].sum() == pytest.approx(1)


def test_reservoir_limit_and_single_unit():
    distances = []
    for n_b in (20, 80, 320, 2560):
        data = canonical_comparison(20, n_b, (20 + n_b) // 4)
        assert data["fraction"] == 0.25
        distances.append(data["total_variation"])
    assert all(a > b for a, b in zip(distances, distances[1:]))
    assert distances[-1] < 0.003
    single = canonical_comparison(1, 19, 5)
    np.testing.assert_allclose(single["exact"], single["canonical"])


@pytest.mark.parametrize("q,beta", [(0, np.inf), (6, 0), (12, -np.inf)])
def test_temperature_and_excitation_boundaries(q, beta):
    data = canonical_comparison(4, 8, q)
    assert data["beta_eps"] == beta
    assert np.all(np.isfinite(data["canonical"]))
    assert data["canonical"].sum() == pytest.approx(1)
    if q in (0, 12):
        np.testing.assert_array_equal(data["exact"], data["canonical"])
        assert data["exact_variance"] == data["canonical_variance"] == 0
        assert data["total_variation"] == 0


@pytest.mark.parametrize("args", [(0, 20, 2), (4, True, 1), (4, 8, -1), (4, 8, 13), (4, 8, 1.5)])
def test_invalid_inputs(args):
    with pytest.raises(ValueError):
        canonical_comparison(*args)


def test_slider_rounding_matches_decimal_half_up():
    from labs.canonical import BATH_SIZES, _excitation_count

    for n_a in range(2, 41, 2):
        for n_b in BATH_SIZES:
            for step in range(1, 11):
                fraction = Decimal(step) / 20
                expected = int((fraction * (n_a + n_b)).to_integral_value(rounding=ROUND_HALF_UP))
                target = float(fraction)
                # Equivalent browser float encodings must produce the same q.
                for value in (target, np.nextafter(target, 0), np.nextafter(target, 1)):
                    assert _excitation_count(n_a + n_b, value) == expected


def _figure(app):
    return json.loads(app.get("plotly_chart")[0].proto.spec)


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_controls_language_navigation_and_export_context(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "canonical", "lang": lang}
    app.run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == len(app.get("download_button")) == 1
    assert not app.button
    initial = _figure(app)
    app.select_slider(key="canon_n_b").set_value(2560).run()
    changed = _figure(app)
    assert initial["data"][0]["y"] != changed["data"][0]["y"]
    assert initial["data"][1]["y"] == changed["data"][1]["y"]
    subtitle = changed["layout"]["title"]["subtitle"]["text"].replace("<br>", " ")
    assert "N_B = 2560" in subtitle and "q = 645" in subtitle
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    assert app.query_params["lab"] == "canonical"
    assert [t["y"] for t in _figure(app)["data"]] == [t["y"] for t in changed["data"]]
    app.radio(key=f"nav_{other}").set_value("glossary").run()
    app.radio(key=f"nav_{other}").set_value("canonical").run()
    assert app.select_slider(key="canon_n_b").value == 2560
    # Test small-bath integer rounding and the infinite-temperature endpoint.
    app.select_slider(key="canon_n_b").set_value(20).run()
    app.slider(key="canon_n_a").set_value(2).run()
    app.slider(key="canon_fraction").set_value(0.05).run()
    assert any("q = 1" in e.value and "0.0455" in e.value for e in app.caption)
    app.slider(key="canon_fraction").set_value(0.5).run()
    assert not app.exception
    assert "βε = 0" in _figure(app)["layout"]["title"]["subtitle"]["text"]
    app.slider(key="canon_n_a").set_value(10).run()
    app.select_slider(key="canon_n_b").set_value(80).run()
    app.slider(key="canon_fraction").set_value(0.35).run()
    assert any("q = 32" in e.value and "0.356" in e.value for e in app.caption)
    assert "q = 32" in _figure(app)["layout"]["title"]["subtitle"]["text"]
    app.toggle(key="panel_open_canon").set_value(False).run()
    assert len(app.get("plotly_chart")) == 1
    assert not app.exception


def test_reference_and_theoretical_visual_semantics(monkeypatch):
    from labs import canonical
    from plot_theme import COLORS

    monkeypatch.setattr(canonical, "tr", lambda en, zh: en)
    figure = canonical._figure(canonical_comparison(20, 40, 15))
    assert [t.line.dash for t in figure.data] == ["solid", "dash"]
    assert all(t.line.color != COLORS["sample"] for t in figure.data)
    for query, term_id in [
        ("正则", "canonical_ensemble"),
        ("heat bath", "thermal_reservoir"),
        ("玻尔兹曼因子", "boltzmann_factor"),
    ]:
        assert term_id in {t["id"] for t in search_terms(query, "canonical")}
