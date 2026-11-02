"""Search and presentation for the bilingual glossary and experiment footers."""

import unicodedata

import streamlit as st

from experiments import EXPERIMENT_BY_ID
from glossary_data import RELATED_IDS as RELATED_IDS
from glossary_data import TERMS as TERMS
from i18n import language, tr
from shared import header

_BY_ID = {term["id"]: term for term in TERMS}
# Reference topics have their own reading order, independent of navigation.
_TOPIC_ORDER = (
    "landau",
    "gas",
    "response",
    "canonical",
    "thermal",
    "joint",
    "distributions",
    "tails",
    "clt",
    "entropy",
)
_CATEGORIES = {
    "all": ("All topics", "全部主题"),
    **{topic: EXPERIMENT_BY_ID[topic].topic_labels for topic in _TOPIC_ORDER},
}


def _normalize(value):
    return unicodedata.normalize("NFKC", value).casefold().strip()


def search_terms(query="", category="all"):
    """Search either language, notation and common abbreviations without UI state."""
    tokens = _normalize(query).split()
    results = []
    for term in TERMS:
        if category != "all" and category not in term["related_lab"]:
            continue
        text = (
            " ".join(
                str(term.get(key, ""))
                for key in (
                    "en",
                    "zh",
                    "symbol",
                    "definition_en",
                    "definition_zh",
                    "note_en",
                    "note_zh",
                )
            )
            + " "
            + " ".join(term["aliases"])
        )
        searchable = _normalize(text)
        if all(token in searchable for token in tokens):
            results.append(term)
    return results


def _title(term):
    label = f"{term['en']} · {term['zh']}"
    return f"{label}  —  {term['symbol']}" if term["symbol"] else label


def _reset_filters():
    st.session_state["glossary_search"] = ""
    st.session_state["glossary_category"] = "all"


def render():
    header(
        "reference",
        tr("Glossary", "术语表"),
        tr(
            "A bilingual reference for the experiments. Search by term, abbreviation or symbol; definitions follow your selected language.",
            "实验中的中英文术语速查。可搜索名称、缩写或符号；定义随所选语言切换。",
        ),
    )
    left, right = st.columns([2, 1])
    with left:
        query = st.text_input(
            tr("Find a term", "查找术语"),
            key="glossary_search",
            placeholder=tr("e.g. kurtosis, IQR, β, 峰度", "例如 kurtosis、IQR、β、峰度"),
        )
    with right:
        category_labels = {key: tr(*names) for key, names in _CATEGORIES.items()}
        category = st.selectbox(
            tr("Topic", "主题"),
            options=list(_CATEGORIES),
            format_func=category_labels.get,
            key="glossary_category",
        )
    results = search_terms(query, category)
    st.caption(
        tr(
            f"{len(results)} of {len(TERMS)} terms",
            f"共 {len(TERMS)} 个术语，当前显示 {len(results)} 个",
        )
    )
    if query or category != "all":
        st.button(tr("Clear filters", "清除筛选"), key="glossary_reset", on_click=_reset_filters)
    if not results:
        st.info(
            tr(
                "No matching terms. Try an English or Chinese keyword, an abbreviation, or another topic.",
                "没有找到匹配的术语。可以尝试中英文关键词、缩写，或切换主题。",
            )
        )
        return
    lang = language()
    for term in results:
        with st.expander(_title(term)):
            st.write(term[f"definition_{lang}"])
            if term["formula"]:
                st.latex(term["formula"])
            if term[f"note_{lang}"]:
                st.markdown(f"**{tr('Keep in mind', '注意区分')}** · {term[f'note_{lang}']}")


def render_related(lab_id):
    """A compact, intentionally closed reference at the end of each experiment."""
    ids = RELATED_IDS.get(lab_id, ())
    if not ids:
        return
    with st.expander(tr("Key terms · English / 中文", "相关术语速查 · English / 中文")):
        lang = language()
        for term_id in ids:
            term = _BY_ID[term_id]
            st.markdown(f"**{term['en']} · {term['zh']}**")
            st.write(term[f"definition_{lang}"])
        st.caption(
            tr(
                "Open Glossary in the sidebar for formulas, distinctions and bilingual search.",
                "在侧栏打开完整术语表，可查看公式、易混点并进行中英文搜索。",
            )
        )
