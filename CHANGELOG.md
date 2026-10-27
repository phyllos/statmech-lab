# Release notes / 版本说明

## Unreleased / 未发布

- Keep the active experiment and display scale when switching languages; require a selected language and preserve Pearson's proper name.
- Add a compact sticky control toolbar on narrow or short screens, with persistent parameter visibility and shared resampling state. Reduce parameter-panel and header spacing.
- Move fixed distribution reference parameters into help, improve secondary-text contrast, and standardize the Chinese term for population inversion.
- Generate standalone chart HTML only when requested; downloading does not rerun the experiment.
- Add responsive-control state tests and an opt-in browser regression script. Browser execution remains to be verified in an environment that permits local browser access.

- 切换语言后保留当前实验与显示尺度；语言始终有选中项，Pearson 保留专有名词大小写。
- 窄屏或短窗口使用紧凑吸顶控制栏，参数区可展开／收起，与桌面共用抽样状态；收紧面板和标题间距。
- 固定分布参数移入提示，增强辅助文字对比度，统一“粒子数反转”术语。
- 点击下载时才生成交互图 HTML，下载不触发实验重新运行。
- 新增面板状态回归测试与独立浏览器检查脚本；真实浏览器执行仍需在允许本机页面访问的环境验证。

## v0.1.0 — Initial baseline / 初始基线

- Four interactive experiments: distributions and boxplots; skewness, kurtosis and tails; LLN and CLT; microstates and entropy.
- English/Chinese interface, searchable bilingual glossary and contextual mathematical explanations.
- Reproducible sampling, linked probability intervals, retained comparisons and a step-by-step CLT sampling walkthrough.
- Compact numerical readouts, optional explanations and responsive chart layouts.
- Session settings preserved across navigation and language changes, with a single source of widget initialization.
- Pure numerical models shared by the app and scientific figure exports; separate state, presentation and styling modules.
- Numerical and interaction regression tests, Ruff formatting/lint rules and locked Python dependencies.
- Docker configuration and deployment documentation. Container build and startup validation remain a deployment step.

- 四个交互实验：分布与箱型图、偏度与峰度及尾部、大数定律与中心极限定理、微观态与熵。
- 中英双语界面、可搜索术语表与相关数学解释。
- 可复现抽样、概率区间联动、保留结果对照及逐步 CLT 抽样演示。
- 紧凑读数、按需说明与响应式图表布局。
- 页面与语言切换保留会话参数，控件使用统一的初始化来源。
- 应用与科学出图共享纯数值模型；状态、展示组件及样式独立组织。
- 数值与交互回归测试、Ruff 格式和检查规则，以及锁定的 Python 依赖。
- Docker 配置与部署文档；容器构建和启动验证在部署阶段完成。
