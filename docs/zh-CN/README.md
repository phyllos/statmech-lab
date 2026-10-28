# StatMech Lab · PHYS 515

[English](../../README.md) · 简体中文

可在本地运行或部署到网页的交互式统计物理概念实验室。通过图形联动、可复现抽样和公式解释，连接概率分布、涨落与微观态计数。

## 启动

项目使用 Python 3.12 进行本地开发与部署。安装 [uv](https://docs.astral.sh/uv/getting-started/installation/) 管理运行环境；`.python-version` 指定解释器版本，缺少时可由 uv 安装。

```bash
git clone https://github.com/phyllos/statmech-lab.git
cd statmech-lab
uv sync --locked
uv run --locked streamlit run app.py --server.address=127.0.0.1
```

已有本地项目时，不需要重新克隆，在项目根目录执行最后两条命令即可。浏览器打开终端显示的本地地址，通常是 `http://localhost:8501`。关闭终端服务用 `Ctrl+C`。

锁文件 `uv.lock` 固定依赖版本；本项目使用 `package = false`，无需构建 Python 包。`requires-python` 声明兼容范围，本地验证使用 Python 3.12。

## 部署到 Streamlit Community Cloud

部署时选择仓库 **`phyllos/statmech-lab`**、分支 **`main`**、入口 **`app.py`**，并在 Advanced settings 中明确选择 **Python 3.12**。无需填写 Secrets。平台使用现有 `uv.lock` 与 `pyproject.toml`，不需要另建 `requirements.txt`。

[部署说明](deployment.md) 包含操作步骤、上线验证、分享和更新方式。Dockerfile 支持其他容器托管环境。

## 四个实验

1. **分布与箱型图**：PDF、CDF、区间概率、抽样直方图、样本分位数、围栏与实际须线。
2. **偏度、峰度与尾部**：尾概率、分布比较、总体矩存在条件、样本峰度的波动。
3. **大数定律与 CLT**：原始分布、重复实验的样本均值、标准化均值，以及不满足经典 CLT 条件的案例。
4. **微观态与熵**：固定激发数的二能级配置、组合计数、熵曲线和热力学极限的逆温度。

界面默认使用英文；品牌区下方的 **English / 中文** 可以随时切换，保留当前实验、参数和随机抽样。
显示设置和对照收在小型入口中，CLT 演示默认折叠。分布与 CLT 实验保留可选交互：跨图追踪概率区间、保留结果进行对照，以及逐步回看 CLT 抽样过程。详见 [交互说明](interactions.md)。
侧栏 **术语表** 提供 28 个中英对照术语，可按中英文、缩写或符号搜索，并按主题筛选。每个实验底部也有相关术语速查。
导航支持 `?lab=distributions`、`?lab=tails`、`?lab=clt`、`?lab=entropy`、`?lab=glossary`；可加 `&lang=zh` 或 `&lang=en` 指定语言。
图表支持悬停读数、缩放，以及工具栏导出 SVG。页面也可下载独立交互图 HTML。

## 可复现与数学约定

- 图形坐标使用无量纲变量；二能级能量单位为正能隙 ε，熵单位为 kB。
- 总体矩来自分布的解析性质，区分未定义（`NaN`）与发散（`∞`）；样本量不能修复不存在的总体矩。方差需要有限均值，标准化偏度与峰度需要有限方差。
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
distribution_ui.py     共用分布名称、参数与说明
plot_theme.py          交互与静态图共享语义配色
shared.py              共享图形风格与界面组件
styles/app.css         响应式布局与界面样式
interactions.py        实验对照和抽样演示
i18n.py                语言切换与显示文本
state.py               会话内实验状态保存
glossary.py            双语术语表与相关术语速查
labs/                  四个独立实验页面
export_figures.py      批量导出科学图形
docs/en/               英文教学来源、架构与部署说明
docs/zh-CN/            简体中文文档
tests/                 数学检查与界面路径检查
.python-version        本地 uv 命令使用 Python 3.12
.streamlit/config.toml 共用主题与无界面服务配置
```

运行检查和静态出图：

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
uv run --locked python export_figures.py
```

静态图保存到 `figs/`，同时提供 PNG 和 SVG，与页面共享数值模型和语义配色。这是一组预设教学图，不是当前浏览器会话的导出。

## 内容范围

实验内容涵盖概率分布、抽样、极限定理与二能级熵；正则系综、系统与热库、理想气体和 Liouville 演化不在当前范围内。
案例基于 PHYS 515 教学与讨论，涵盖 PDF/CDF、分位数、median/IQR 对齐、survival function、Pareto 与箱型图等概念。详见 [内容与来源](sources.md)。

## 版本管理

项目版本为 **0.1.1**。`v0.1.0` 标记项目初始基线；`main` 包含已集成的改动，版本标签标识发布快照。**Unreleased／未发布** 列出尚未归入版本的变更。参见 [版本说明](CHANGELOG.md) 和 [Git 使用约定](git-workflow.md)。

## 架构与部署

[架构说明](architecture.md) 介绍模块边界和手动界面检查；[部署说明](deployment.md) 提供本地、Community Cloud 与容器配置。应用本身无需账号、API key 或数据库；托管服务有独立的账号和访问权限设置。
