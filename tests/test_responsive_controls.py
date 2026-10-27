"""State and data guarantees behind the responsive control toolbar.

Actual CSS visibility, sticky positioning and stale frontend labels require the
separate browser checks; AppTest cannot exercise those behaviors.
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
def test_panel_visibility_preserves_data_and_actions_share_one_counter(
    lab, seed_key, initial, full_action
):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": lab, "lang": "en"}
    app.run()
    before = plot_values(app)
    assert not app.toggle(key=f"panel_open_{lab}").value
    app.toggle(key=f"panel_open_{lab}").set_value(True).run()
    assert plot_values(app) == before
    app.toggle(key=f"panel_open_{lab}").set_value(False).run()
    assert plot_values(app) == before
    app.button(key=f"action_compact_draw_{lab}").click().run()
    assert app.session_state[seed_key] == initial + 1
    assert plot_values(app) != before
    app.button(key=full_action).click().run()
    assert app.session_state[seed_key] == initial + 2
    assert not app.exception


@pytest.mark.parametrize("lab", ["distributions", "tails", "clt", "entropy"])
def test_compact_panel_keeps_navigation_and_open_state_across_languages(lab):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": lab, "lang": "en"}
    app.run()
    app.toggle(key=f"panel_open_{lab}").set_value(True).run()
    for lang in ("zh", "en", "zh"):
        app.button_group(key="language").set_value(lang).run()
        app.button(key=f"action_compact_draw_{lab}").click().run()
        assert app.session_state["active_lab"] == lab
        assert app.query_params["lab"] == lab
        assert app.query_params["lang"] == lang
        assert app.toggle(key=f"panel_open_{lab}").value
        assert app.button_group(key="language").proto.required
    app.radio(key="nav_zh").set_value("glossary").run()
    app.radio(key="nav_zh").set_value(lab).run()
    assert app.toggle(key=f"panel_open_{lab}").value
    assert not app.exception


def test_english_kurtosis_retains_proper_name():
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "tails", "lang": "en"}
    app.run()
    copy = "\n".join(e.value for e in app.markdown)
    assert "Population Pearson kurtosis" in copy
    assert "pearson" not in copy
    assert "Pearson kurtosis" in app.metric[0].label
