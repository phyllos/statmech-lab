# StatMech Lab · PHYS 515

[English](README.md) · 简体中文

本地交互式统计物理概念实验室。通过图形联动、可复现抽样和公式解释，连接概率分布、涨落与微观态计数。

## 启动

需要 [uv](https://docs.astral.sh/uv/) 和 Python 3.12 或更新的兼容版本。

```bash
cd stat_mech
uv sync --locked
uv run --locked streamlit run app.py
```

浏览器打开终端显示的本地地址，通常是 `http://localhost:8501`。关闭终端服务用 `Ctrl+C`。
锁文件 `uv.lock` 固定依赖版本；本项目使用 `package = false`，无需构建 Python 包。

## 四个实验

1. **分布与箱型图**：PDF、CDF、区间概率、抽样直方图、样本分位数、围栏与实际须线。
2. **偏度、峰度与尾部**：尾概率、分布比较、总体矩存在条件、样本峰度的波动。
3. **大数定律与 CLT**：原始分布、重复实验的样本均值、标准化均值，以及不满足经典 CLT 条件的案例。
4. **微观态与熵**：固定激发数的二能级配置、组合计数、熵曲线和热力学极限的逆温度。

界面默认使用英文；品牌区下方的 **English / 中文** 可以随时切换，保留当前实验、参数和随机抽样。
显示设置和对照收在小型入口中，CLT 演示默认折叠。分布与 CLT 实验保留可选交互：跨图追踪概率区间、保留结果进行对照，以及逐步回看 CLT 抽样过程。详见 [交互说明](docs/interactions.md)。
侧栏 **术语表** 提供 28 个中英对照术语，可按中英文、缩写或符号搜索，并按主题筛选。每个实验底部也有相关术语速查。
导航支持 `?lab=distributions`、`?lab=tails`、`?lab=clt`、`?lab=entropy`、`?lab=glossary`；可加 `&lang=zh` 或 `&lang=en` 指定语言。
图表支持悬停读数、缩放，以及工具栏导出 SVG。页面也可下载独立交互图 HTML。

## 可复现与数学约定

- 图形坐标使用无量纲变量；二能级能量单位为正能隙 ε，熵单位为 kB。
- 总体矩来自分布的解析性质，样本量不能修复不存在的总体矩。对非有限总体矩显示相应状态，不以 0 代替。
- 默认峰度为 Pearson 标准化四阶中心矩（正态分布为 3）；超额峰度为该值减 3。页面有明确标注。
- 样本分位数使用 NumPy `method="linear"`，须线是 1.5 IQR 围栏内最远的实际样本。所有统计量用完整样本计算。
- 有限图形视窗不改变分布支持集。直方图按原始总样本数与箱宽归一化，提示窗外样本。
- 抽样使用局部随机数生成器。相同参数和 seed 产生相同结果；重新抽样按钮更新 seed。
- CLT 实验展示 iid、有限非零方差时的经典标准化。均值与方差不满足条件时不会绘制伪造的高斯理论线。
- 二能级模型是 N 个可区分、无相互作用、能级为 0/ε 的位置。固定 q 时 Ω=binom(N,q)，同一能量层中的配置等概率。
- `βε = ln((N-q)/q)` 是热力学极限近似，不声称是有限 N 离散熵的精确导数。端点是极限，半占据时 β=0。

## 代码结构

```text
app.py                 应用入口与导航
physics.py             纯数值模型，无界面和文件副作用
shared.py              共享图形风格与界面组件
styles/app.css         响应式布局与界面样式
interactions.py        实验对照和抽样演示
i18n.py                语言切换与显示文本
state.py               会话内实验状态保存
glossary.py            双语术语表与相关术语速查
labs/                  四个独立实验页面
export_figures.py      批量导出科学图形
docs/                  内容与来源说明
tests/                 数学检查与界面路径检查
.streamlit/config.toml 本地服务与主题
```

运行检查和静态出图：

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
uv run --locked python export_figures.py
```

静态图保存到 `figs/`，同时提供 PNG 和 SVG。计算与页面共享 `physics.py`。

## 内容范围

当前版本覆盖概率到熵的桥梁；正则系综、系统与热库、理想气体和 Liouville 演化适合作为后续模块。
案例基于 PHYS 515 教学与讨论，涵盖 PDF/CDF、分位数、median/IQR 对齐、survival function、Pareto 与箱型图等概念。详见 [内容与来源](docs/sources.md)。

## 版本管理

`v0.1.0` 是 `main` 上的项目初始基线，包含四个双语实验、图形联动、保留对照、术语表、代码质量工具与部署配置。参见 [版本说明](CHANGELOG.md) 和 [Git 使用约定](docs/git-workflow.md)。

## 架构与部署

[架构说明](docs/architecture.md) 介绍模块边界和扩展方式；[部署说明](docs/deployment.md) 提供本地与容器运行命令。应用无需账号、API key 或数据库。
