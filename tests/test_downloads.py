"""Deferred exports must capture the current chart without eager serialization."""

from concurrent.futures import ThreadPoolExecutor

import plotly.graph_objects as go

import shared


def test_export_is_deferred_and_uses_an_independent_snapshot(monkeypatch):
    calls = []
    buttons = []
    monkeypatch.setattr(shared, "chart_config", lambda: {"locale": "en"})
    monkeypatch.setattr(shared, "tr", lambda en, zh: en)
    monkeypatch.setattr(shared.st, "download_button", lambda *a, **kw: buttons.append(kw))

    def serialize(fig, **kwargs):
        calls.append((list(fig.data[0].y), kwargs))
        return "chart html"

    monkeypatch.setattr(go.Figure, "to_html", serialize)
    fig = go.Figure(go.Scatter(x=[1, 2], y=[3, 4]))
    shared.download_figure(fig, "example")
    assert calls == []
    assert buttons[0]["on_click"] == "ignore"
    fig.data[0].y = [8, 9]
    # Configuration must already be captured; the background callback cannot
    # depend on the current session's language or the caller's mutable figure.
    monkeypatch.setattr(shared, "chart_config", lambda: {"locale": "zh-cn"})
    with ThreadPoolExecutor(max_workers=1) as pool:
        assert pool.submit(buttons[0]["data"]).result() == "chart html"
    assert calls == [([3, 4], {"include_plotlyjs": True, "config": {"locale": "en"}})]


def test_inline_and_download_figures_retain_native_bilingual_headings(monkeypatch):
    from contextlib import nullcontext

    monkeypatch.setattr(shared.st, "container", lambda **kw: nullcontext())
    rendered, buttons = [], []
    monkeypatch.setattr(shared.st, "plotly_chart", lambda fig, **kw: rendered.append((fig, kw)))
    monkeypatch.setattr(shared.st, "download_button", lambda *a, **kw: buttons.append(kw))
    monkeypatch.setattr(shared, "chart_config", lambda: {})
    monkeypatch.setattr(shared, "tr", lambda en, zh: en)
    fig = go.Figure(go.Scatter(x=[0, 1], y=[0, 1]))
    shared.chart(
        fig, title="02 / Cumulative probability", subtitle="同一区间在累计概率中的对应位置"
    )
    display, options = rendered[0]
    assert display.layout.title.text == "02 / Cumulative probability"
    assert display.layout.title.subtitle.text == "同一区间在累计概率中的对应位置"
    assert options["config"]["toImageButtonOptions"]["format"] == "svg"
    assert display.layout.margin.t > 30
    shared.download_figure(fig, "test")
    exports = []

    def serialize(figure, **kw):
        exports.append(figure)
        return "html"

    monkeypatch.setattr(go.Figure, "to_html", serialize)
    assert buttons[0]["data"]() == "html"
    assert exports[0].layout.title == display.layout.title
    assert exports[0].data == display.data


def test_long_headings_wrap_and_escape_markup():
    wrapped, lines = shared._wrapped_heading("A long heading with <symbols> and 中文解释 " * 3, 36)
    assert lines > 1
    assert "<br>" in wrapped
    assert "&lt;symbols&gt;" in wrapped
