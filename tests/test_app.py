"""Exercise complete learning paths and controls that change model validity."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture(params=["en", "zh"])
def app(request):
    instance = AppTest.from_file(str(APP), default_timeout=20).run()
    if request.param == "zh":
        instance.button_group(key="language").set_value("zh").run()
    assert not instance.exception
    return instance


def _nav(app):
    """The navigation radio is keyed per language (see app.py)."""
    return app.radio(key=f"nav_{app.session_state['language']}")


def _open(app, lab):
    _nav(app).set_value(lab).run()
    assert not app.exception
    return app


def test_navigation_and_export_controls(app):
    for lab in ("distributions", "tails", "clt", "entropy"):
        _open(app, lab)
        assert len(app.get("plotly_chart")) >= 3
        assert len(app.get("download_button")) == 1


def test_distribution_display_change_preserves_seed_and_resample_changes_it(app):
    app.selectbox(key="dist_name").set_value("pareto").run()
    app.slider(key="dist_shape_pareto").set_value(0.5).run()
    assert not app.exception
    app.toggle(key="dist_align").set_value(True).run()
    assert not app.exception
    app.button(key="dist_resample").click().run()
    assert app.session_state["dist_seed"] == 516
    app.slider(key="dist_interval").set_value((0.1, 0.9)).run()
    assert app.session_state["dist_seed"] == 516
    assert not app.exception


def test_nonfinite_kurtosis_and_normal_convention(app):
    _open(app, "tails")
    app.slider(key="tail_alpha").set_value(2.0).run()
    assert not app.exception
    assert any(
        "没有有限的总体峰度" in element.value or "no finite population kurtosis" in element.value
        for element in app.markdown
    )
    app.selectbox(key="tail_name").set_value("normal").run()
    app.toggle(key="tail_excess").set_value(True).run()
    assert not app.exception
    assert any(
        "超额峰度为 0" in element.value or "excess kurtosis is 0" in element.value
        for element in app.markdown
    )


def test_clt_invalid_variance_resets_standardized_view(app):
    _open(app, "clt")
    app.button_group(key="clt_view").set_value("standardized").run()
    app.selectbox(key="clt_distribution").set_value("cauchy").run()
    assert not app.exception
    assert app.button_group(key="clt_view").value == "means"
    assert app.button_group(key="clt_view").disabled
    app.selectbox(key="clt_distribution").set_value("pareto").run()
    app.slider(key="clt_alpha").set_value(1.5).run()
    assert (
        "大数定律仍可适用" in app.warning[0].value
        or "law of large numbers applies" in app.warning[0].value
    )
    app.slider(key="clt_alpha").set_value(3.0).run()
    assert not app.button_group(key="clt_view").disabled
    assert not app.exception


def test_entropy_boundaries_and_decreasing_system_size(app):
    _open(app, "entropy")
    app.slider(key="ent_q").set_value(40).run()
    assert any(
        "只有一种排列" in element.value or "Only one arrangement" in element.value
        for element in app.markdown
    )
    app.slider(key="ent_n").set_value(8).run()
    assert app.slider(key="ent_q").value == 8
    app.slider(key="ent_q").set_value(4).run()
    assert any(
        "无限温极限" in element.value or "infinite-temperature limit" in element.value
        for element in app.markdown
    )
    app.button(key="ent_shuffle").click().run()
    assert app.slider(key="ent_q").value == 4
    assert not app.exception


def _plot_data(app):
    """Compare every plotted numeric array, without translated labels or hover text."""
    fields = (
        "x",
        "y",
        "z",
        "width",
        "q1",
        "median",
        "q3",
        "lowerfence",
        "upperfence",
        "customdata",
    )
    return [
        [
            {key: trace[key] for key in fields if key in trace}
            for trace in json.loads(chart.proto.spec)["data"]
        ]
        for chart in app.get("plotly_chart")
    ]


def test_fresh_session_defaults_to_english():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    assert app.button_group(key="language").value == "en"
    assert _nav(app).options[0] == "01  Distributions & boxplots"
    assert "Population PDF" in app.get("plotly_chart")[0].proto.spec


@pytest.mark.parametrize("lab", ["distributions", "tails", "clt", "entropy"])
def test_language_and_reference_navigation_preserve_experiment(lab):
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    _open(app, lab)
    if lab == "distributions":
        app.selectbox(key="dist_name").set_value("pareto").run()
        app.slider(key="dist_shape_pareto").set_value(1.5).run()
        app.button_group(key="dist_view").set_value("central99").run()
        app.toggle(key="dist_align").set_value(True).run()
        app.button(key="dist_resample").click().run()
        expected = {
            "dist_name": "pareto",
            "dist_shape_pareto": 1.5,
            "dist_view": "central99",
            "dist_align": True,
            "dist_seed": 516,
        }
    elif lab == "tails":
        app.selectbox(key="tail_name").set_value("student_t").run()
        app.slider(key="tail_nu").set_value(7.0).run()
        app.toggle(key="tail_excess").set_value(True).run()
        app.button(key="tail_resample").click().run()
        expected = {
            "tail_name": "student_t",
            "tail_nu": 7.0,
            "tail_excess": True,
            "tail_seed": 1516,
        }
    elif lab == "clt":
        app.selectbox(key="clt_distribution").set_value("pareto").run()
        app.slider(key="clt_alpha").set_value(4.5).run()
        app.slider(key="clt_n").set_value(51).run()
        app.button_group(key="clt_view").set_value("standardized").run()
        app.button(key="clt_resample").click().run()
        expected = {
            "clt_distribution": "pareto",
            "clt_alpha": 4.5,
            "clt_n": 51,
            "clt_view": "standardized",
            "clt_draw": 1,
        }
    else:
        app.slider(key="ent_n").set_value(64).run()
        app.slider(key="ent_q").set_value(42).run()
        app.button(key="ent_shuffle").click().run()
        expected = {"ent_n": 64, "ent_q": 42, "ent_draw": 1}
    assert not app.exception
    before = _plot_data(app)
    app.button_group(key="language").set_value("zh").run()
    assert not app.exception
    assert app.query_params["lang"] == "zh"
    assert app.query_params["lab"] == lab
    assert all(app.session_state[key] == value for key, value in expected.items())
    assert _plot_data(app) == before
    assert all(
        json.loads(chart.proto.config)["locale"] == "zh-cn" for chart in app.get("plotly_chart")
    )
    _open(app, "glossary")
    app.text_input(key="glossary_search").set_value("CLT").run()
    app.button_group(key="language").set_value("en").run()
    assert not app.exception
    assert app.text_input(key="glossary_search").value == "CLT"
    _open(app, lab)
    assert all(app.session_state[key] == value for key, value in expected.items())
    assert _plot_data(app) == before


def test_glossary_search_category_and_reset(app):
    _open(app, "glossary")
    app.text_input(key="glossary_search").set_value("峰度").run()
    assert any("Pearson kurtosis · Pearson 峰度" in e.label for e in app.expander)
    app.text_input(key="glossary_search").set_value("β").run()
    app.selectbox(key="glossary_category").set_value("entropy").run()
    assert not app.exception
    assert any("Inverse temperature · 逆温度" in e.label for e in app.expander)
    app.text_input(key="glossary_search").set_value("no-such-physics-term").run()
    assert len(app.info) == 1
    app.button(key="glossary_reset").click().run()
    assert app.text_input(key="glossary_search").value == ""
    assert app.selectbox(key="glossary_category").value == "all"
    assert any("Probability density function · 概率密度函数" in e.label for e in app.expander)
    assert not app.exception


def test_chinese_reference_deep_link():
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params = {"lang": "zh", "lab": "glossary"}
    app.run()
    assert not app.exception
    assert app.button_group(key="language").value == "zh"
    assert _nav(app).value == "glossary"
    assert any("参考</div>" in e.value for e in app.markdown)


def test_restored_controls_do_not_also_supply_widget_defaults(monkeypatch):
    from streamlit.elements.lib import policies

    duplicate_keys = []
    original = policies.check_session_state_rules

    def check(default_value, key, writes_allowed=True):
        # Check every invocation; Streamlit normally logs only the first conflict
        # in a process, which could otherwise conceal later offending widgets.
        if (
            key is not None
            and default_value is not None
            and policies.get_session_state().is_new_state_value(key)
        ):
            duplicate_keys.append(key)
        return original(default_value, key, writes_allowed)

    monkeypatch.setattr(policies, "check_session_state_rules", check)
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert app.select_slider(key="dist_n").value == 300
    assert app.slider(key="dist_interval").value == (0.25, 0.75)
    assert app.toggle(key="dist_fences").value is True
    for model in ("pareto", "lognormal", "student_t"):
        app.selectbox(key="dist_name").set_value(model).run()
    _open(app, "tails")
    assert app.toggle(key="tail_logx").value is True
    for model in ("lognormal", "student_t", "pareto"):
        app.selectbox(key="tail_name").set_value(model).run()
    _open(app, "clt")
    assert app.slider(key="clt_n").value == 30
    assert app.select_slider(key="clt_repetitions").value == 2000
    app.selectbox(key="clt_distribution").set_value("pareto").run()
    _open(app, "entropy")
    assert app.slider(key="ent_n").value == 40
    assert app.slider(key="ent_q").value == 10
    app.slider(key="ent_n").set_value(64).run()
    app.button_group(key="language").set_value("zh").run()
    _open(app, "glossary")
    _open(app, "entropy")
    assert app.slider(key="ent_n").value == 64
    assert not app.exception
    assert duplicate_keys == []
