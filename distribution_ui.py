"""Distribution names and parameter descriptions, independent of UI runtime/models.

Render translated dictionaries once per rerun, then pass their ``get`` methods
as widget formatters. A formatter must not read session state when serialized.
Page-specific slider ranges and scientific calculations remain in their owners.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DistributionText:
    en: str
    zh: str
    base_parameters: str = ""
    shape_symbol: str = ""
    note_en: str = ""
    note_zh: str = ""

    def name(self, lang: str) -> str:
        return self.zh if lang == "zh" else self.en


DISTRIBUTION_TEXT = {
    "normal": DistributionText("Normal", "正态", "μ = 0, σ = 1"),
    "uniform": DistributionText(
        "Uniform", "均匀", "[−√3, √3]", note_en="Mean 0, variance 1", note_zh="均值 0，方差 1"
    ),
    "exponential": DistributionText("Exponential", "指数", "λ = 1"),
    "lognormal": DistributionText("Lognormal", "对数正态", shape_symbol="σ"),
    "pareto": DistributionText("Pareto", "Pareto", shape_symbol="α"),
    "student_t": DistributionText("Student t", "Student t", shape_symbol="ν"),
    "cauchy": DistributionText(
        "Cauchy", "Cauchy", "x₀ = 0, γ = 1", note_en="Mean undefined", note_zh="均值不存在"
    ),
}


def distribution_label(name: str, lang: str, *, parameters: bool = False) -> str:
    spec = DISTRIBUTION_TEXT[name]
    label = spec.name(lang)
    return f"{label} · {spec.base_parameters}" if parameters and spec.base_parameters else label


def distribution_description(name: str, lang: str, *, shape: float) -> str:
    spec = DISTRIBUTION_TEXT[name]
    label = distribution_label(name, lang, parameters=True)
    return f"{label} · {spec.shape_symbol} = {shape:g}" if spec.shape_symbol else label


def distribution_help(name: str, lang: str) -> str | None:
    spec = DISTRIBUTION_TEXT[name]
    note = spec.note_zh if lang == "zh" else spec.note_en
    return " · ".join(part for part in (spec.base_parameters, note) if part) or None
