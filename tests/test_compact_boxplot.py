"""Responsive labels preserve the scientific data and fence controls."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from labs import distributions

APP = Path(__file__).resolve().parents[1] / "app.py"


def _figure(app):
    return json.loads(
        next(c.proto.spec for c in app.get("plotly_chart") if c.proto.id.endswith("-dist_box"))
    )


def _values(fig):
    fields = ("x", "y", "q1", "median", "q3", "lowerfence", "upperfence", "marker")
    return [{k: t[k] for k in fields if k in t} for t in fig["data"]]


@pytest.mark.parametrize("lang", ["en", "zh"])
@pytest.mark.parametrize("saved", [False, True])
def test_compact_labels_preserve_data_and_restore_desktop(monkeypatch, lang, saved):
    mode = {"compact": False}
    monkeypatch.setattr(distributions, "compact_chart", lambda key: mode["compact"])
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "distributions", "lang": lang}
    app.run()
    if saved:
        app.button(key="action_keep_distributions").click().run()
        app.button(key="dist_resample").click().run()
    desktop = _figure(app)
    mode["compact"] = True
    app.run()
    assert not app.exception
    mobile = _figure(app)
    assert _values(mobile) == _values(desktop)
    assert mobile["layout"]["xaxis"]["range"] == desktop["layout"]["xaxis"]["range"]
    assert mobile["layout"]["yaxis"]["ticktext"][-2:] == (
        ["Boxplot", "Pop."] if lang == "en" else ["箱型图", "总体"]
    )
    annotations = mobile["layout"]["annotations"]
    quartiles = {a["text"]: a for a in annotations if a["text"] in ("Q₁", "Q₂", "Q₃")}
    assert len(quartiles) == 3
    assert quartiles["Q₂"]["yshift"] > quartiles["Q₁"]["yshift"]
    assert quartiles["Q₁"]["xanchor"] == "right"
    assert quartiles["Q₃"]["xanchor"] == "left"
    population = mobile["data"][-1]
    assert "%{hovertext}" in population["hovertemplate"]
    assert ("Median Q₂" if lang == "en" else "中位数 Q₂") in population["hovertext"]
    fences = [a for a in annotations if a.get("yref") == "paper"]
    assert len(fences) == 2
    assert all("hovertext" in a for a in fences)
    app.toggle(key="dist_fences").set_value(False).run()
    assert {a["text"] for a in _figure(app)["layout"]["annotations"]} == {"Q₁", "Q₂", "Q₃"}
    app.toggle(key="dist_fences").set_value(True).run()
    mode["compact"] = False
    app.run()
    restored = _figure(app)
    assert restored == desktop
    assert not app.exception
