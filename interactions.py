"""Optional learning controls; saved references never advance a random seed."""

from copy import deepcopy

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from i18n import tr
from shared import COLORS, chart


def _save_reference(key, settings):
    st.session_state[key] = deepcopy(settings)


def _clear_reference(key):
    st.session_state.pop(key, None)


def comparison_controls(lab, settings, describe, *, model_keys):
    """Retain reproducible settings, rather than a translated figure or label.

    Action keys deliberately do not use experiment control prefixes: trigger
    button values must never enter the widget restoration mechanism.
    """
    key = f"_reference_{lab}"
    reference = st.session_state.get(key)
    compatible = reference is not None and all(reference[k] == settings[k] for k in model_keys)
    label = tr("Compare", "对照")
    if reference:
        label += tr(" · saved", " · 已保留") if compatible else tr(" · paused", " · 已暂停")
    with st.popover(label, icon=":material/compare_arrows:", key=f"comparison_{lab}"):
        st.caption(
            tr(
                "Keep this result, then change the sample size or resample. A dashed reference stays until you replace or clear it.",
                "先保留当前结果，再改变样本量或重新抽样。虚线对照会一直保留，直到替换或清除。",
            )
        )
        a, b = st.columns(2)
        a.button(
            tr("Replace saved result", "替换保留结果")
            if reference
            else tr("Keep this result", "保留当前结果"),
            key=f"action_keep_{lab}",
            on_click=_save_reference,
            args=(key, settings),
            width="stretch",
        )
        b.button(
            tr("Clear reference", "清除对照"),
            key=f"action_clear_{lab}",
            on_click=_clear_reference,
            args=(key,),
            disabled=reference is None,
            width="stretch",
        )
        if reference:
            st.caption(tr("Saved: ", "已保留：") + describe(reference))
        if reference and not compatible:
            st.caption(
                tr(
                    "Paused: the model or alignment changed. Restore those settings or replace the saved result.",
                    "模型或对齐方式已改变，对照暂时隐藏；恢复对应参数或替换保留结果即可。",
                )
            )
    return reference if compatible else None


def _restart_walkthrough():
    st.session_state["clt_demo_stage"] = "draw"
    st.session_state["clt_demo_count"] = 10


def sampling_walkthrough(result, *, n, repetitions, seed, model):
    """Reveal an actual first group and prefixes of the current run, without resampling."""
    signature = (*model, n, repetitions, seed)
    if st.session_state.get("_walkthrough_run") != signature:
        _restart_walkthrough()
        st.session_state["_walkthrough_run"] = signature
    stages = {
        "draw": tr("1 · Draw a group", "1 · 抽一组样本"),
        "mean": tr("2 · Take its mean", "2 · 计算均值"),
        "repeat": tr("3 · Repeat", "3 · 重复积累"),
    }
    with st.expander(tr("Understand sampling", "理解抽样过程"), expanded=False):
        st.caption(
            tr(
                "Replay this run: the same observations, seed and means as the charts above. Select a step to reveal what happens next.",
                "回看本次实验：使用上方图表同一批观测、随机种子与均值。点击步骤，逐步查看生成过程。",
            )
        )
        stage = st.radio(
            tr("Sampling steps", "抽样步骤"),
            list(stages),
            format_func=stages.get,
            horizontal=True,
            key="clt_demo_stage",
            label_visibility="collapsed",
        )
        count = None
        if stage == "repeat":
            counts = sorted({10, 50, 100, 500, repetitions})
            count = st.select_slider(
                tr("Groups revealed", "已展示组数"), counts, key="clt_demo_count"
            )
        group = np.asarray(result["first_group"])
        means = np.asarray(result["means"])
        first_mean = float(means[0])
        a, b = st.columns(2)
        with a:
            fig = go.Figure(
                go.Scatter(
                    x=np.arange(1, n + 1),
                    y=group,
                    mode="markers",
                    marker=dict(size=6, color=COLORS["sample"], opacity=0.8),
                    name=tr("Observations", "观测值"),
                    hovertemplate=tr(
                        "Observation %{x:d}<br>x = %{y:.3g}<extra></extra>",
                        "第 %{x:d} 个观测<br>x = %{y:.3g}<extra></extra>",
                    ),
                )
            )
            if stage != "draw":
                fig.add_trace(
                    go.Scatter(
                        x=[0.5, n + 0.5],
                        y=[first_mean, first_mean],
                        mode="lines",
                        name=tr("Group mean", "本组均值"),
                        line=dict(color=COLORS["accent"], width=2, dash="dash"),
                    )
                )
            fig.update_xaxes(hoverformat=",d")
            fig.update_layout(
                height=320,
                xaxis_title=tr("Observation index i", "观测序号 i"),
                yaxis_title="xᵢ",
                xaxis_range=[0.5, n + 0.5],
            )
            chart(
                fig,
                key="demo_observations",
                title=tr("One group of observations", "一组原始观测"),
                subtitle=tr(f"Group 1 · all {n} observations", f"第 1 组 · 全部 {n} 个观测"),
            )
        with b:
            if stage == "draw":
                st.markdown(tr("**Each dot is one observation.**", "**每个点是一次观测。**"))
                st.write(
                    tr(
                        f"These {n} values form one group. Their average will contribute just one value to the histogram of means.",
                        f"这 {n} 个数构成一组。取平均后，它们只会向均值直方图贡献一个数。",
                    )
                )
                st.caption(
                    tr(
                        "Choose step 2 to calculate the mean. No new observations are drawn.",
                        "点击步骤 2 计算均值；这一步不会产生新的观测。",
                    )
                )
            elif stage == "mean":
                st.metric(tr("One group → one mean", "一组样本 → 一个均值"), f"{first_mean:.3g}")
                st.latex(r"\bar x_1=\frac{x_{1,1}+\cdots+x_{1,n}}{n}")
                st.write(
                    tr(
                        f"Sum = {group.sum():.3g}; divide by n = {n}. The dashed line on the left is this group's mean.",
                        f"本组总和 = {group.sum():.3g}；除以 n = {n}。左图虚线表示本组均值。",
                    )
                )
                st.caption(
                    tr(
                        "Choose step 3 to accumulate means from independent groups.",
                        "点击步骤 3，积累独立各组的均值。",
                    )
                )
            else:
                # One fixed set of bins for this run; show every mean, including extremes.
                lo, hi = float(means.min()), float(means.max())
                if lo == hi:
                    lo, hi = lo - 0.5, hi + 0.5
                edges = np.linspace(lo, hi, 41)
                frequencies, _ = np.histogram(means[:count], bins=edges)
                fig = go.Figure(
                    go.Bar(
                        x=(edges[:-1] + edges[1:]) / 2,
                        y=frequencies,
                        width=np.diff(edges),
                        marker_color=COLORS["sample"],
                        name=tr("Number of groups", "组数"),
                    )
                )
                fig.update_yaxes(hoverformat=",d")
                fig.update_layout(
                    height=320,
                    xaxis_title=tr("Group mean x̄", "每组均值 x̄"),
                    yaxis_title=tr("Count", "频数"),
                    showlegend=False,
                    xaxis_range=[lo, hi],
                )
                chart(
                    fig,
                    key="demo_histogram",
                    title=tr("One mean from every group", "每一组贡献一个均值"),
                    subtitle=tr(
                        f"First {count:,} groups of this run", f"本次实验的前 {count:,} 组"
                    ),
                )
                st.caption(
                    tr(
                        "Bins stay fixed and include all means. This is a count histogram in raw units; the main plot uses probability density. Extreme means can stretch this view.",
                        "分箱固定并包含全部均值。这是原始尺度上的频数图；上方主图使用概率密度。极端均值可能拉宽此视窗。",
                    )
                )
        if not result["finite_variance"]:
            st.warning(
                tr(
                    "Repeating this construction does not supply the missing finite-variance assumption of the classical CLT.",
                    "重复上述过程，并不会补足经典 CLT 所需的有限方差条件。",
                )
            )
        st.button(
            tr("Back to step 1", "回到步骤 1"),
            key="action_restart_walkthrough",
            on_click=_restart_walkthrough,
        )
