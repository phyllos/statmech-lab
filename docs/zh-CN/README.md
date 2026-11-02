# StatMech Lab · PHYS 515

[English](../../README.md) · 简体中文

交互式统计物理概念实验室，连接概率、微观态计数、系综与热力学稳定性。通过图形联动、可复现抽样和按需展开的推导探索概念，支持英文与简体中文，可在本地运行或部署到网页。

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

## 实验内容

| 编号 | 实验 | 核心概念 |
| --- | --- | --- |
| 01 | 分布与箱型图 | PDF/CDF、区间概率、分位数与样本统计 |
| 02 | 偏度、峰度与尾部 | 尾概率、矩的存在条件与样本波动 |
| 03 | 大数定律与 CLT | 样本均值、标准化与收敛条件 |
| 04 | 微观态与熵 | 二能级配置、微观态数、熵与逆温度 |
| 05 | 联合与条件概率 | 高斯相关性、边缘化与条件化 |
| 06 | 热接触与能量分配 | 精确能量分配概率、熵与平衡涨落 |
| 07 | 热库与正则系综 | 有限热库概率与正则近似 |
| 08 | 温度与热容量 | 二能级占据、温度响应与能量涨落 |
| 09 | 理想气体与速率 | 高斯速度分量与麦克斯韦速率分布 |
| 10 | 自由能与稳定性 | Landau 自由能极小值、平衡分支与亚稳态 |

实验 01–03 和 05 介绍概率概念。实验 04、06–08 沿用同一个二能级模型，从固定能量逐步过渡到热接触与温度响应。实验 09 将概率应用于气体速度；实验 10 作为自由能与稳定性的独立入门。

## 使用方式

- **语言与导航**：默认使用英文，在侧栏通过 **English / 中文** 切换；同一会话中保留实验参数、样本和显示设置。
- **控件与解释**：参数默认展开；显示选项、保留对照和推导按实验需要提供。确定性实验不显示重新抽样操作。
- **术语表**：支持按中英文名称、缩写或符号搜索，并按主题筛选。各实验也提供相关术语速查。
- **图形与导出**：悬停读数、拖动缩放、双击复原。工具栏可导出 SVG，下载按钮生成独立交互图 HTML。导出文件保存当前图形，不包含完整应用的调参功能。

[交互说明](interactions.md) 介绍图形联动、保留对照与探索方式；[模型说明](sources.md) 汇总假设和推导。

直达链接使用 `?lab=<id>`，可加 `&lang=en` 或 `&lang=zh` 指定语言。实验标识为 `distributions`、`tails`、`clt`、`entropy`、`joint`、`thermal`、`canonical`、`response`、`gas` 和 `landau`；术语表使用 `glossary`。例如：`?lab=thermal&lang=zh`。

## 可复现与数学约定

- 图形坐标使用无量纲变量；二能级能量单位为正能隙 ε，熵单位为 kB。
- 总体矩来自分布的解析性质，区分未定义（`NaN`）与发散（`∞`）；样本量不能修复不存在的总体矩。方差需要有限均值，标准化偏度与峰度需要有限方差。
- 默认峰度为 Pearson 标准化四阶中心矩（正态分布为 3）；超额峰度为该值减 3。页面有明确标注。
- 样本分位数使用 NumPy `method="linear"`，须线止于 1.5 IQR 围栏内最远的实际观测值。所有统计量用完整样本计算。
- 有限绘图范围不截断分布，也不重新归一化概率。直方图按完整样本量与箱宽归一化，并提示范围外的观测数。
- 抽样使用局部随机数生成器。相同参数和随机种子产生相同结果；重新抽样更新种子，切换语言不改变样本。
- 经典 CLT 视图要求观测独立同分布，且具有有限、非零的方差。不满足条件时不显示正态近似。
- 二能级模型包含 N 个可区分、无相互作用的单元，能量为 0 或 ε。固定激发数 q 时 Ω=binom(N,q)，同一能量层中的配置等概率。
- `βε = ln((N-q)/q)` 是大 N 近似，不是有限 N 离散熵的精确导数。端点是极限，半占据时 β=0。

## 代码结构

```text
app.py                 应用入口与导航
experiments.py         共用实验元数据与页面加载
physics.py             纯数值模型，无界面和文件副作用
distribution_ui.py     共用分布名称、参数与说明
plot_theme.py          交互与静态图共享语义配色
shared.py              共享图形风格与界面组件
styles/                响应式布局、界面样式与图表宽度观察器
interactions.py        实验对照和抽样演示
i18n.py                语言切换与显示文本
state.py               会话内实验状态保存
glossary_data.py       双语术语内容与精选引用
glossary.py            术语搜索与术语表展示
labs/                  实验页面
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

## 内容范围与来源

实验聚焦平衡概率模型与热力学概念，不模拟微观时间演化。Landau 模型假定均匀序参量，不包含空间涨落、成核与滞回动力学。

案例基于 PHYS 515 教学与讨论。[内容与来源](sources.md) 汇总模型假设、数学约定与参考资料。

## 版本管理

项目版本为 **0.1.1**。`v0.1.0` 标记项目初始基线；`main` 包含已集成的改动，版本标签标识发布快照。**Unreleased／未发布** 列出尚未归入版本的变更。参见 [版本说明](CHANGELOG.md) 和 [Git 使用约定](git-workflow.md)。

## 架构与部署

[架构说明](architecture.md) 介绍模块边界和手动界面检查；[部署说明](deployment.md) 提供本地、Community Cloud 与容器配置。应用本身无需账号、API key 或数据库；托管服务有独立的账号和访问权限设置。
