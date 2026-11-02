"""Probability pages keep exports current and display options independent of sampling."""

import importlib
import json
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def _figure(app, key):
    assert not app.exception
    return json.loads(
        next(c.proto.spec for c in app.get("plotly_chart") if c.proto.id.endswith("-" + key))
    )


@pytest.mark.parametrize("lang", ["en", "zh"])
@pytest.mark.parametrize(
    "lab,chart_key,export_name,resample_key",
    [
        ("distributions", "dist_box", "distribution_boxplot", "dist_resample"),
        ("tails", "tail_sample_kurtosis", "sample_kurtosis", "tail_resample"),
        ("clt", "clt_means_chart", "clt_sample_means", "clt_resample"),
    ],
)
def test_export_tracks_resampling_and_display_changes(
    lang, lab, chart_key, export_name, resample_key, monkeypatch
):
    module = importlib.import_module(f"labs.{lab}")
    exports = []
    original_download = module.download_figure

    def capture_download(figure, name):
        exports.append((name, json.loads(figure.to_json())))
        return original_download(figure, name)

    monkeypatch.setattr(module, "download_figure", capture_download)
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": lab, "lang": lang}
    app.run()

    def check_export():
        displayed = _figure(app, chart_key)
        name, exported = exports[-1]
        assert name == export_name
        assert exported["data"] == displayed["data"]
        for key in ("text", "subtitle"):
            assert exported["layout"]["title"].get(key) == displayed["layout"]["title"].get(key)
        for axis in ("xaxis", "yaxis"):
            actual_axis, displayed_axis = exported["layout"][axis], displayed["layout"][axis]
            assert actual_axis.get("title", {}).get("text") == displayed_axis.get("title", {}).get(
                "text"
            )
            for key in ("range", "type"):
                assert actual_axis.get(key) == displayed_axis.get(key)
        return exported

    before = check_export()
    if lab in ("distributions", "clt"):
        app.button(key=f"action_keep_{lab}").click().run()
    app.button(key=resample_key).click().run()
    assert check_export()["data"] != before["data"]

    if lab == "distributions":
        app.slider(key="dist_interval").set_value((0.1, 0.8)).run()
        app.toggle(key="dist_fences").set_value(False).run()
    elif lab == "tails":
        app.toggle(key="tail_excess").set_value(True).run()
    else:
        app.slider(key="clt_n").set_value(80).run()
        app.button_group(key="clt_view").set_value("standardized").run()
    current = check_export()
    app.toggle(key=f"panel_open_{lab}").set_value(False).run()
    assert check_export() == current


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_tail_display_options_preserve_the_sample(lang):
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lab": "tails", "lang": lang}
    app.run()
    app.selectbox(key="tail_name").set_value("normal").run()
    app.button(key="tail_resample").click().run()
    seed = app.session_state["tail_seed"]
    shape = _figure(app, "tail_pdf")
    survival = _figure(app, "tail_sf")
    kurtosis = _figure(app, "tail_sample_kurtosis")

    app.toggle(key="tail_logx").set_value(False).run()
    assert _figure(app, "tail_sf")["data"] == survival["data"]
    assert _figure(app, "tail_sf")["layout"]["xaxis"]["type"] == "linear"
    assert _figure(app, "tail_sample_kurtosis") == kurtosis

    app.toggle(key="tail_excess").set_value(True).run()
    assert app.session_state["tail_seed"] == seed
    assert _figure(app, "tail_pdf") == shape
    assert _figure(app, "tail_sf")["data"] == survival["data"]
    # The population reference shifts by three with the kurtosis convention.
    np.testing.assert_allclose(kurtosis["data"][1]["y"], [3, 3])
    np.testing.assert_allclose(_figure(app, "tail_sample_kurtosis")["data"][1]["y"], [0, 0])
    app.toggle(key="tail_excess").set_value(False).run()
    assert _figure(app, "tail_sample_kurtosis") == kurtosis
