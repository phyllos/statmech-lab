"""Static exports follow the same scientific color roles as the live charts."""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pytest

from export_figures import build_figures
from labs import tails
from plot_theme import COLORS


def test_static_interval_markers_match_theory_and_have_white_outline():
    figures = build_figures()
    try:
        cdf = figures["01_probability"].axes[1]
        points = cdf.collections[0]
        np.testing.assert_allclose(points.get_facecolors()[0], mcolors.to_rgba(COLORS["theory"]))
        np.testing.assert_allclose(points.get_edgecolors()[0], mcolors.to_rgba("white"))
        assert cdf.lines[0].get_color() == COLORS["theory"]
        assert figures["04_entropy"].axes[1].lines[0].get_color() == COLORS["accent"]
    finally:
        for fig in figures.values():
            plt.close(fig)


@pytest.mark.parametrize("zh", [False, True])
def test_nonfinite_readouts_distinguish_undefined_and_divergent(monkeypatch, zh):
    monkeypatch.setattr(tails, "tr", lambda en, cn: cn if zh else en)
    assert tails._fmt(np.nan) == ("未定义" if zh else "Undefined")
    assert tails._fmt(np.inf) == ("发散（+∞）" if zh else "Diverges (+∞)")
    assert tails._fmt(1.23456) == "1.23"
