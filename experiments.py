"""Experiment metadata shared by navigation, persistence and reference topics.

Importing this module does not load Streamlit or experiment pages. Page modules
are loaded only after the application has validated the selected route.
"""

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module


@dataclass(frozen=True, kw_only=True)
class Experiment:
    id: str
    number: int
    name_en: str
    name_zh: str
    module: str
    control_prefix: str
    topic_names: tuple[str, str] | None = None

    @property
    def navigation_labels(self) -> tuple[str, str]:
        return (f"{self.number:02d}  {self.name_en}", f"{self.number:02d}  {self.name_zh}")

    @property
    def topic_labels(self) -> tuple[str, str]:
        return self.topic_names or (self.name_en, self.name_zh)


# Tuple order is the navigation order. IDs and control prefixes are persistent
# identifiers; changing a display name must not change either of them.
EXPERIMENTS = (
    Experiment(
        id="distributions",
        number=1,
        name_en="Distributions & boxplots",
        name_zh="分布与箱型图",
        module="labs.distributions",
        control_prefix="dist_",
    ),
    Experiment(
        id="tails",
        number=2,
        name_en="Shape & tails",
        name_zh="偏度、峰度与尾部",
        module="labs.tails",
        control_prefix="tail_",
        topic_names=("Moments & tails", "矩与尾部"),
    ),
    Experiment(
        id="clt",
        number=3,
        name_en="LLN & CLT",
        name_zh="大数定律与 CLT",
        module="labs.clt",
        control_prefix="clt_",
        topic_names=("Sampling & limit theorems", "抽样与极限定理"),
    ),
    Experiment(
        id="entropy",
        number=4,
        name_en="Microstates & entropy",
        name_zh="微观态与熵",
        module="labs.entropy",
        control_prefix="ent_",
    ),
    Experiment(
        id="joint",
        number=5,
        name_en="Joint & conditional probability",
        name_zh="联合与条件概率",
        module="labs.joint",
        control_prefix="joint_",
    ),
    Experiment(
        id="thermal",
        number=6,
        name_en="Thermal contact",
        name_zh="热接触与能量分配",
        module="labs.thermal",
        control_prefix="thermal_",
    ),
    Experiment(
        id="canonical",
        number=7,
        name_en="Reservoir & canonical ensemble",
        name_zh="热库与正则系综",
        module="labs.canonical",
        control_prefix="canon_",
    ),
    Experiment(
        id="response",
        number=8,
        name_en="Temperature & heat capacity",
        name_zh="温度与热容量",
        module="labs.response",
        control_prefix="response_",
    ),
    Experiment(
        id="gas",
        number=9,
        name_en="Ideal gas & speed",
        name_zh="理想气体与速率",
        module="labs.gas",
        control_prefix="gas_",
    ),
    Experiment(
        id="landau",
        number=10,
        name_en="Free energy & stability",
        name_zh="自由能与稳定性",
        module="labs.landau",
        control_prefix="landau_",
    ),
)

EXPERIMENT_BY_ID = {experiment.id: experiment for experiment in EXPERIMENTS}
CONTROL_PREFIXES = tuple(experiment.control_prefix for experiment in EXPERIMENTS)
DEFAULT_EXPERIMENT = EXPERIMENTS[0].id

# Reference material is a page, not a numbered experiment.
REFERENCE_ID = "glossary"
PAGE_LABELS = {
    **{experiment.id: experiment.navigation_labels for experiment in EXPERIMENTS},
    REFERENCE_ID: ("Reference · Glossary", "参考 · 术语表"),
}
_PAGE_MODULES = {
    **{experiment.id: experiment.module for experiment in EXPERIMENTS},
    REFERENCE_ID: "glossary",
}


def load_renderer(page_id: str) -> Callable[[], None]:
    """Load a registered page; reject unknown IDs before importing any module."""
    return import_module(_PAGE_MODULES[page_id]).render
