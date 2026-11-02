"""Registry integrity and route compatibility across the bilingual app."""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

import experiments
from experiments import CONTROL_PREFIXES, EXPERIMENTS, PAGE_LABELS, load_renderer

ROOT = Path(__file__).resolve().parents[1]


def test_registry_identifiers_and_prefixes_are_unambiguous():
    for field in ("id", "number", "module", "control_prefix"):
        values = [getattr(item, field) for item in EXPERIMENTS]
        assert len(values) == len(set(values)), field
    for item in EXPERIMENTS:
        assert item.id.isidentifier()
        assert item.number > 0
        assert all(text.strip() for text in (*item.navigation_labels, *item.topic_labels))
        assert item.control_prefix.endswith("_")
        assert not any(
            other.startswith(item.control_prefix)
            for other in CONTROL_PREFIXES
            if other != item.control_prefix
        )
    assert experiments.REFERENCE_ID not in experiments.EXPERIMENT_BY_ID


def test_registry_import_does_not_load_ui_or_pages():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import experiments; "
            "assert 'streamlit' not in sys.modules; "
            "assert 'glossary' not in sys.modules; "
            "assert not any(name.startswith('labs.') for name in sys.modules)",
        ],
        cwd=ROOT,
        check=True,
    )


def test_renderer_loads_only_the_registered_module(monkeypatch):
    imported = []

    def renderer():
        return None

    def import_page(name):
        imported.append(name)
        return SimpleNamespace(render=renderer)

    monkeypatch.setattr(experiments, "import_module", import_page)
    assert load_renderer("entropy") is renderer
    assert imported == ["labs.entropy"]
    with pytest.raises(KeyError):
        load_renderer("labs.entropy")
    assert imported == ["labs.entropy"]


@pytest.mark.parametrize("language", ["en", "zh"])
def test_registered_deep_links_survive_language_changes(language):
    other_language = "zh" if language == "en" else "en"
    for page_id in PAGE_LABELS:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
        app.query_params.update(lang=language, lab=page_id)
        app.run()
        assert not app.exception, page_id
        assert app.session_state["active_lab"] == page_id
        nav = app.radio(key=f"nav_{language}")
        assert nav.value == page_id
        assert nav.options == [labels[language == "zh"] for labels in PAGE_LABELS.values()]
        app.button_group(key="language").set_value(other_language).run()
        assert not app.exception, page_id
        assert app.radio(key=f"nav_{other_language}").value == page_id
        assert app.query_params["lab"] == page_id


@pytest.mark.parametrize("route", ["unknown", "04  Microstates & entropy", "labs.entropy"])
def test_invalid_deep_link_uses_default_page(route):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    app.query_params.update(lang="en", lab=route)
    app.run()
    assert not app.exception
    assert app.session_state["active_lab"] == "distributions"
    app.button_group(key="language").set_value("zh").run()
    assert not app.exception
    assert app.query_params["lab"] == "distributions"
