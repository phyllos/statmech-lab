"""Check that learning interactions preserve data and compare compatible quantities."""

import base64
import json
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from physics import clt_experiment, make_distribution, sample_summary

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture(params=["en", "zh"])
def app(request):
    instance = AppTest.from_file(str(APP), default_timeout=20).run()
    if request.param == "zh":
        instance.button_group(key="language").set_value("zh").run()
    assert not instance.exception
    return instance


def figure(app, key):
    return json.loads(
        next(c.proto.spec for c in app.get("plotly_chart") if c.proto.id.endswith("-" + key))
    )


def array(value):
    if isinstance(value, dict) and "bdata" in value:
        return np.frombuffer(base64.b64decode(value["bdata"]), dtype=value["dtype"])
    return np.asarray(value)


def nav(app):
    return app.radio(key=f"nav_{app.session_state['language']}")


def open_lab(app, lab):
    nav(app).set_value(lab).run()
    assert not app.exception


def test_linked_interval_preserves_observations_and_links_plot_bands(app):
    original = figure(app, "dist_box")["data"][:2]
    app.slider(key="dist_interval").set_value((0.1, 0.8)).run()
    assert not app.exception
    cdf = figure(app, "dist_cdf")
    left, right = make_distribution("normal").ppf([0.1, 0.8])
    np.testing.assert_allclose(array(cdf["data"][2]["x"]), [left, right])
    np.testing.assert_allclose(array(cdf["data"][2]["y"]), [0.1, 0.8])
    pdf_area = figure(app, "dist_pdf")["data"][1]
    np.testing.assert_allclose(array(pdf_area["x"])[[0, -1]], [left, right])
    box = figure(app, "dist_box")
    interval_band = next(s for s in box["layout"]["shapes"] if s["type"] == "rect")
    assert interval_band["x0"] == pytest.approx(left)
    assert interval_band["x1"] == pytest.approx(right)
    for before, after in zip(original, box["data"][:2]):
        np.testing.assert_array_equal(array(before["x"]), array(after["x"]))
        assert after["marker"] == before["marker"]
        assert after["marker"]["opacity"] == 0.6
        assert "selectedpoints" not in after
    app.slider(key="dist_interval").set_value((0.25, 0.75)).run()
    assert all(widget.key != "dist_focus" for widget in app.radio)
    np.testing.assert_allclose(array(figure(app, "dist_cdf")["data"][2]["y"]), [0.25, 0.75])
    app.slider(key="dist_interval").set_value((0.2, 0.9)).run()
    assert app.slider(key="dist_interval").value == (0.2, 0.9)
    assert not app.exception


def test_distribution_reference_survives_resampling_and_navigation(app):
    original_cdf = figure(app, "dist_cdf")["data"][1]
    app.button(key="action_keep_distributions").click().run()
    saved = dict(app.session_state["_reference_distributions"])
    app.button(key="dist_resample").click().run()
    assert app.session_state["dist_seed"] == saved["seed"] + 1
    current = figure(app, "dist_cdf")["data"]
    assert current[1]["x"] != original_cdf["x"]
    assert current[-1]["x"] == original_cdf["x"]
    assert current[-1]["y"] == original_cdf["y"]
    app.toggle(key="dist_align").set_value(True).run()
    assert len(figure(app, "dist_cdf")["data"]) == 3
    assert dict(app.session_state["_reference_distributions"]) == saved
    app.toggle(key="dist_align").set_value(False).run()
    app.button_group(key="language").set_value(
        "en" if app.button_group(key="language").value == "zh" else "zh"
    ).run()
    open_lab(app, "glossary")
    app.text_input(key="glossary_search").set_value("IQR").run()
    open_lab(app, "distributions")
    assert figure(app, "dist_cdf")["data"][-1]["y"] == original_cdf["y"]
    app.button(key="action_keep_distributions").click().run()
    assert app.session_state["_reference_distributions"]["seed"] == saved["seed"] + 1
    current_cdf = figure(app, "dist_cdf")["data"][1]
    app.button(key="action_clear_distributions").click().run()
    assert len(figure(app, "dist_cdf")["data"]) == 3
    assert figure(app, "dist_cdf")["data"][1] == current_cdf
    open_lab(app, "glossary")
    open_lab(app, "distributions")
    assert len(figure(app, "dist_cdf")["data"]) == 3
    assert not app.exception


def test_clt_reference_uses_its_own_standardization_and_shared_bins(app):
    open_lab(app, "clt")
    app.slider(key="clt_n").set_value(8).run()
    app.select_slider(key="clt_repetitions").set_value(500).run()
    app.button(key="action_keep_clt").click().run()
    saved = dict(app.session_state["_reference_clt"])
    app.slider(key="clt_n").set_value(80).run()
    app.button_group(key="clt_view").set_value("standardized").run()
    data = figure(app, "clt_means_chart")["data"]
    centers, widths = array(data[0]["x"]), array(data[0]["width"])
    edges = np.r_[centers - widths / 2, centers[-1] + widths[-1] / 2]
    previous = clt_experiment("exponential", 3.0, 8, 500, 51503)["standardized"]
    counts, _ = np.histogram(previous, bins=edges)
    np.testing.assert_allclose(array(data[1]["y"]), counts / (500 * widths))
    assert dict(app.session_state["_reference_clt"]) == saved
    app.selectbox(key="clt_distribution").set_value("cauchy").run()
    assert app.button_group(key="clt_view").value == "means"
    assert len(figure(app, "clt_means_chart")["data"]) == 2
    assert not app.exception


def test_walkthrough_replays_run_and_keeps_progress_in_both_languages(app):
    open_lab(app, "clt")
    app.slider(key="clt_n").set_value(7).run()
    app.select_slider(key="clt_repetitions").set_value(500).run()
    main_before = figure(app, "clt_means_chart")["data"]
    walkthrough = next(
        e for e in app.expander if e.label in ("Understand sampling", "理解抽样过程")
    )
    assert walkthrough.proto.expanded is False
    expected = clt_experiment("exponential", 3.0, 7, 500, 51503, include_first_group=True)
    np.testing.assert_array_equal(
        array(figure(app, "demo_observations")["data"][0]["y"]), expected["first_group"]
    )
    assert len(figure(app, "demo_observations")["data"]) == 1
    app.button_group(key="clt_demo_stage").set_value("mean").run()
    np.testing.assert_allclose(
        array(figure(app, "demo_observations")["data"][1]["y"]), [expected["means"][0]] * 2
    )
    app.button_group(key="clt_demo_stage").set_value("repeat").run()
    app.select_slider(key="clt_demo_count").set_value(100).run()
    histogram = figure(app, "demo_histogram")["data"][0]
    assert array(histogram["y"]).sum() == 100
    centers, widths = array(histogram["x"]), array(histogram["width"])
    edges = np.linspace(expected["means"].min(), expected["means"].max(), 41)
    np.testing.assert_allclose(centers, (edges[:-1] + edges[1:]) / 2)
    np.testing.assert_allclose(widths, np.diff(edges))
    np.testing.assert_array_equal(
        array(histogram["y"]), np.histogram(expected["means"][:100], bins=edges)[0]
    )
    assert figure(app, "clt_means_chart")["data"] == main_before
    app.button_group(key="clt_demo_stage").set_value("mean").run()
    app.button_group(key="clt_demo_stage").set_value("repeat").run()
    assert app.select_slider(key="clt_demo_count").value == 100
    app.button_group(key="language").set_value(
        "en" if app.button_group(key="language").value == "zh" else "zh"
    ).run()
    open_lab(app, "glossary")
    open_lab(app, "clt")
    assert app.button_group(key="clt_demo_stage").value == "repeat"
    assert app.select_slider(key="clt_demo_count").value == 100
    assert array(figure(app, "demo_histogram")["data"][0]["y"]).sum() == 100
    app.button(key="clt_resample").click().run()
    assert app.button_group(key="clt_demo_stage").value == "draw"
    assert app.session_state["clt_draw"] == 1
    app.selectbox(key="clt_distribution").set_value("cauchy").run()
    app.button_group(key="clt_demo_stage").set_value("repeat").run()
    app.select_slider(key="clt_demo_count").set_value(500).run()
    assert array(figure(app, "demo_histogram")["data"][0]["y"]).sum() == 500
    assert len(app.warning) >= 2
    app.button(key="action_restart_walkthrough").click().run()
    assert app.button_group(key="clt_demo_stage").value == "draw"
    assert app.session_state["clt_draw"] == 1
    assert not app.exception


@pytest.mark.parametrize(
    "name,shape,n,repetitions",
    [
        ("normal", 3.0, 17, 100),
        ("uniform", 3.0, 17, 100),
        ("exponential", 3.0, 17, 100),
        ("lognormal", 0.8, 17, 100),
        ("pareto", 1.5, 17, 100),
        ("student_t", 2.0, 17, 100),
        ("cauchy", 3.0, 17, 100),
        ("normal", 3.0, 500, 5000),
    ],
)
def test_retaining_first_group_never_changes_the_experiment(name, shape, n, repetitions):
    ordinary = clt_experiment(name, shape, n, repetitions, 1871)
    explained = clt_experiment(name, shape, n, repetitions, 1871, include_first_group=True)
    np.testing.assert_array_equal(ordinary["means"], explained["means"])
    assert explained["first_group"].shape == (n,)
    assert explained["first_group"].mean() == pytest.approx(explained["means"][0])
    if ordinary["finite_variance"]:
        np.testing.assert_array_equal(ordinary["standardized"], explained["standardized"])
    else:
        assert explained["standardized"] is None


def test_secondary_controls_are_hidden_without_losing_functionality(app):
    options = next(e for e in app.get("popover") if e.proto.id.endswith("-display_distributions"))
    assert not options.proto.popover.open
    assert options.toggle(key="dist_align").value is False
    assert options.toggle(key="dist_fences").value is True
    assert options.button_group(key="dist_view").value == "body"
    comparison = next(
        e for e in app.get("popover") if e.proto.id.endswith("-comparison_distributions")
    )
    assert not comparison.proto.popover.open
    assert comparison.button(key="action_keep_distributions")
    app.toggle(key="dist_fences").set_value(False).run()
    assert all(shape["type"] != "line" for shape in figure(app, "dist_box")["layout"]["shapes"])
    open_lab(app, "tails")
    options = next(e for e in app.get("popover") if e.proto.id.endswith("-display_tails"))
    assert options.toggle(key="tail_logx").value is True
    options.toggle(key="tail_logx").set_value(False).run()
    assert figure(app, "tail_sf")["layout"]["xaxis"]["type"] == "linear"
    open_lab(app, "clt")
    options = next(e for e in app.get("popover") if e.proto.id.endswith("-display_clt"))
    assert options.button_group(key="clt_view").value == "means"
    assert not app.exception


def test_endpoint_and_box_hover_readouts_follow_the_actual_statistics(app):
    # Check asymmetric and heavy-tailed models as well as the default, so that
    # quantile positions and whiskers cannot accidentally be hard-coded.
    for name, probabilities in [
        ("normal", (0.1, 0.8)),
        ("exponential", (0.2, 0.95)),
        ("pareto", (0.01, 0.99)),
    ]:
        app.selectbox(key="dist_name").set_value(name).run()
        app.slider(key="dist_interval").set_value(probabilities).run()
        assert not app.exception
        cdf = figure(app, "dist_cdf")
        endpoints = cdf["data"][2]
        assert endpoints["mode"] == "markers"
        np.testing.assert_allclose(
            array(endpoints["x"]), make_distribution(name).ppf(probabilities)
        )
        np.testing.assert_allclose(array(endpoints["y"]), probabilities)
        # Hiding the endpoint trace must not leave behind an unrelated purple bar.
        assert all(shape["type"] != "line" for shape in cdf["layout"]["shapes"])

        box = figure(app, "dist_box")
        points = box["data"][:2]
        values = np.concatenate([array(trace["x"]) for trace in points])
        summary = sample_summary(values)
        for trace in points:
            assert trace["marker"]["size"] == 5
            assert trace["marker"]["opacity"] == 0.6
            assert trace["marker"].get("symbol", "circle") == "circle"
            assert "selected" not in trace and "unselected" not in trace
        native_box = next(t for t in box["data"] if t["type"] == "box")
        assert native_box["hoverinfo"] == "skip"
        hover = next(
            t
            for t in box["data"]
            if t.get("legendgroup") == "sample_summary" and t["type"] == "scatter"
        )
        assert hover["legendgroup"] == native_box["legendgroup"]
        assert hover["showlegend"] is False
        assert hover["hovertemplate"] == "%{text}: %{x:.3g}<extra></extra>"
        assert box["layout"]["hovermode"] == "closest"
        np.testing.assert_allclose(
            array(hover["x"]),
            [summary[k] for k in ("lower_whisker", "q1", "median", "q3", "upper_whisker")],
        )
        assert summary["outlier_count"] > 0
        assert summary["lower_whisker"] > values.min() or summary["upper_whisker"] < values.max()


def test_readout_formats_preserve_counts_and_microstate_heading(app):
    open_lab(app, "tails")
    tail = figure(app, "tail_sample_kurtosis")
    assert tail["layout"]["xaxis"]["hoverformat"] == ",d"
    assert tail["layout"]["yaxis"]["hoverformat"] == ".3g"
    open_lab(app, "clt")
    assert figure(app, "clt_running_chart")["layout"]["xaxis"]["hoverformat"] == ",d"
    assert figure(app, "clt_means_chart")["layout"]["yaxis"]["hoverformat"] == ".3g"
    app.button_group(key="clt_demo_stage").set_value("repeat").run()
    assert figure(app, "demo_histogram")["layout"]["yaxis"]["hoverformat"] == ",d"
    assert figure(app, "demo_observations")["layout"]["xaxis"]["hoverformat"] == ",d"
    open_lab(app, "entropy")
    assert any(
        "figure-title" in m.value
        and ("01 / One possible microstate" in m.value or "01 / 一个可能的微观态" in m.value)
        for m in app.markdown
    )
    assert not any("#### ①" in m.value for m in app.markdown)
    # Unit IDs remain exact; formatting does not affect the microstate.
    state = figure(app, "ent_state_chart")
    ids = np.concatenate([array(t["customdata"]) for t in state["data"]])
    np.testing.assert_array_equal(np.sort(ids), np.arange(1, 41))


def test_hover_precision_does_not_round_scientific_data():
    import plotly.graph_objects as go

    from shared import style_figure

    x, y = [1.23456789, 12345.6789], [1.23456789e-12, 9.87654321e12]
    fig = go.Figure(go.Scatter(x=x, y=y))
    style_figure(fig)
    np.testing.assert_array_equal(fig.data[0].x, x)
    np.testing.assert_array_equal(fig.data[0].y, y)
    assert fig.layout.xaxis.hoverformat == fig.layout.yaxis.hoverformat == ".3g"
    fig.update_xaxes(hoverformat=",d")
    style_figure(fig)
    assert fig.layout.xaxis.hoverformat == ",d"
