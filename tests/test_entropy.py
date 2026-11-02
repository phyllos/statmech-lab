"""Rearranging a microstate preserves thermodynamics and the exported entropy plot."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from labs import entropy

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_rearrangement_changes_only_microstate_and_exports_current_entropy(lang, monkeypatch):
    exports = []
    original_download = entropy.download_figure

    def capture_download(figure, name):
        exports.append((name, json.loads(figure.to_json())))
        return original_download(figure, name)

    monkeypatch.setattr(entropy, "download_figure", capture_download)
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "entropy", "lang": lang}
    app.run()

    def figures():
        assert not app.exception
        return [json.loads(c.proto.spec) for c in app.get("plotly_chart")]

    def check_export():
        displayed = figures()[1]
        name, exported = exports[-1]
        assert name == "two_level_entropy"
        assert exported["data"] == displayed["data"]
        assert exported["layout"]["title"]["text"] == displayed["layout"]["title"]["text"]
        assert exported["layout"]["title"]["subtitle"] == displayed["layout"]["title"]["subtitle"]

    before = figures()
    check_export()
    app.button(key="ent_shuffle").click().run()
    after = figures()
    assert app.session_state["ent_draw"] == 1
    assert app.slider(key="ent_n").value == 40
    assert app.slider(key="ent_q").value == 10
    assert before[0]["data"] != after[0]["data"]
    assert before[1:] == after[1:]
    check_export()

    app.slider(key="ent_q").set_value(30).run()
    assert app.session_state["ent_draw"] == 1
    assert figures()[1]["data"][-1]["x"] == [0.75]
    assert figures()[2]["data"][-1]["y"][0] < 0
    check_export()

    app.toggle(key="panel_open_entropy").set_value(False).run()
    assert app.session_state["ent_draw"] == 1
    check_export()
