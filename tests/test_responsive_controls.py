"""State and data guarantees behind the responsive control toolbar.

Actual CSS visibility, sticky positioning and stale frontend labels require the
manual UI checks in docs/architecture.md; AppTest cannot exercise those behaviors.
"""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def plot_values(app):
    fields = ("x", "y", "q1", "q3", "median", "customdata")
    return [
        [{k: trace[k] for k in fields if k in trace} for trace in json.loads(c.proto.spec)["data"]]
        for c in app.get("plotly_chart")
    ]


@pytest.mark.parametrize(
    "lab,seed_key,initial,full_action",
    [
        ("distributions", "dist_seed", 515, "dist_resample"),
        ("tails", "tail_seed", 1515, "tail_resample"),
        ("clt", "clt_draw", 0, "clt_resample"),
        ("entropy", "ent_draw", 0, "ent_shuffle"),
    ],
)
def test_panel_starts_open_and_visibility_preserves_data(lab, seed_key, initial, full_action):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": lab, "lang": "en"}
    app.run()
    before = plot_values(app)
    assert app.toggle(key=f"panel_open_{lab}").value
    app.toggle(key=f"panel_open_{lab}").set_value(False).run()
    assert plot_values(app) == before
    app.button(key=full_action).click().run()
    assert app.session_state[seed_key] == initial + 1
    assert plot_values(app) != before
    sampled = plot_values(app)
    app.toggle(key=f"panel_open_{lab}").set_value(True).run()
    assert plot_values(app) == sampled
    app.button(key=full_action).click().run()
    assert app.session_state[seed_key] == initial + 2
    assert not app.exception


@pytest.mark.parametrize(
    "lab,action",
    [
        ("distributions", "dist_resample"),
        ("tails", "tail_resample"),
        ("clt", "clt_resample"),
        ("entropy", "ent_shuffle"),
    ],
)
@pytest.mark.parametrize("opened", [True, False])
def test_panel_keeps_navigation_and_visibility_across_languages(lab, action, opened):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": lab, "lang": "en"}
    app.run()
    app.toggle(key=f"panel_open_{lab}").set_value(opened).run()
    for lang in ("zh", "en", "zh"):
        app.button_group(key="language").set_value(lang).run()
        app.button(key=action).click().run()
        assert app.session_state["active_lab"] == lab
        assert app.query_params["lab"] == lab
        assert app.query_params["lang"] == lang
        assert app.toggle(key=f"panel_open_{lab}").value == opened
        assert app.button_group(key="language").proto.required
    app.radio(key="nav_zh").set_value("glossary").run()
    app.radio(key="nav_zh").set_value(lab).run()
    assert app.toggle(key=f"panel_open_{lab}").value == opened
    assert not app.exception


def test_english_kurtosis_retains_proper_name():
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "tails", "lang": "en"}
    app.run()
    copy = "\n".join(e.value for e in app.markdown)
    assert "Population Pearson kurtosis" in copy
    assert "pearson" not in copy
    assert "Pearson kurtosis" in app.metric[0].label


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_fixed_parameters_remain_visible_and_alignment_is_explicit(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "distributions", "lang": lang}
    app.run()
    choices = app.selectbox(key="dist_name").options
    assert "μ = 0, σ = 1" in choices[0]
    assert "[−√3, √3]" in choices[1]
    assert "λ = 1" in choices[2]
    assert "x₀ = 0, γ = 1" in choices[-1]
    app.selectbox(key="dist_name").set_value("exponential").run()
    app.toggle(key="dist_align").set_value(True).run()
    caption = "\n".join(e.value for e in app.caption)
    assert ("Aligned axes" if lang == "en" else "坐标已对齐") in caption
    assert ("base-distribution parameters" if lang == "en" else "原始分布参数") in caption
    other = "zh" if lang == "en" else "en"
    app.button_group(key="language").set_value(other).run()
    app.button(key="dist_resample").click().run()
    assert app.selectbox(key="dist_name").value == "exponential"
    assert app.toggle(key="dist_align").value
    app.toggle(key="dist_align").set_value(False).run()
    caption = "\n".join(e.value for e in app.caption)
    assert "Aligned axes" not in caption and "坐标已对齐" not in caption
    assert not app.exception
