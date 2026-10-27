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
