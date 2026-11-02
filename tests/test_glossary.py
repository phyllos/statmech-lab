"""Content integrity and search contracts for the bilingual reference."""

from copy import deepcopy

import pytest

from experiments import EXPERIMENT_BY_ID
from glossary import _CATEGORIES, search_terms
from glossary_data import RELATED_IDS, TERMS


def test_entries_have_unique_ids_and_complete_bilingual_text():
    ids = [term["id"] for term in TERMS]
    assert len(ids) == len(set(ids))
    for term in TERMS:
        for field in ("id", "en", "zh", "definition_en", "definition_zh"):
            assert isinstance(term[field], str) and term[field].strip(), (term["id"], field)
        for field in ("symbol", "formula", "note_en", "note_zh"):
            assert isinstance(term[field], str), (term["id"], field)
        assert bool(term["note_en"]) == bool(term["note_zh"]), term["id"]
        assert all(isinstance(alias, str) and alias.strip() for alias in term["aliases"])


def test_topic_membership_and_curated_references_are_valid():
    topics = set(_CATEGORIES) - {"all"}
    by_id = {term["id"]: term for term in TERMS}
    assert set(RELATED_IDS) == topics == set(EXPERIMENT_BY_ID)
    for topic in topics:
        assert any(topic in term["related_lab"] for term in TERMS), topic
    for term in TERMS:
        membership = term["related_lab"]
        assert membership and len(membership) == len(set(membership)), term["id"]
        assert set(membership) <= topics, term["id"]
    for topic, ids in RELATED_IDS.items():
        assert ids and len(ids) == len(set(ids)), topic
        for term_id in ids:
            assert term_id in by_id, (topic, term_id)
            assert topic in by_id[term_id]["related_lab"], (topic, term_id)


@pytest.mark.parametrize(
    "query,category,expected_id",
    [
        ("  ＩＱＲ  ", "all", "iqr"),
        ("KURTOSIS", "tails", "kurtosis"),
        ("峰度", "tails", "kurtosis"),
        ("i.i.d.", "clt", "iid"),
        ("β", "entropy", "inverse_temperature"),
        ("conditional density", "joint", "conditional_density"),
    ],
)
def test_search_accepts_bilingual_names_symbols_and_aliases(query, category, expected_id):
    assert expected_id in {term["id"] for term in search_terms(query, category)}


def test_search_preserves_content_order_and_combines_filters():
    original_terms = deepcopy(TERMS)
    original_related = deepcopy(RELATED_IDS)
    assert search_terms() == TERMS
    for category in _CATEGORIES:
        expected = [term for term in TERMS if category == "all" or category in term["related_lab"]]
        assert search_terms("", category) == expected

    assert search_terms("峰度", "joint") == []
    assert search_terms("kurtosis no-such-term") == []
    assert search_terms("", "unknown-topic") == []
    assert TERMS == original_terms
    assert RELATED_IDS == original_related
