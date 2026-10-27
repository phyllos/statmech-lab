# Learning interactions / 教学交互

The experiments combine reproducible calculations with linked plots and optional explanations.

实验通过可复现计算、图形联动与按需解释，连接操作和概念。

## One interval, three views / 同一区间，三种表示

In **Distributions & boxplots**, move the probability-interval endpoints. The PDF area, the two CDF endpoints, and the band behind the sample points refer to the same x interval. All sample points use a consistent style: circular markers, size 5 and opacity 0.6. Fence outliers remain purple; selection no longer changes point appearance.

在 **分布与箱型图** 中调整累计概率区间端点：PDF 的阴影、CDF 的两个端点及样本图上的区间阴影都对应同一个 x 区间。所有样本点使用统一样式：大小为 5 的圆点、透明度 0.6。围栏外观测仍用紫色；选择区间不再改变散点外观。

The interval slider is the only selection control. Its default 0.25–0.75 interval spans the population IQR; the sample box retains its own estimated quartiles. Alignment, visible range and fences are available under **Display**.

概率区间滑块是唯一的区间选择控件。默认的 0.25–0.75 区间跨越总体 IQR；样本箱体仍使用样本自身估计的分位数。对齐方式、显示范围及围栏开关收在 **显示选项** 中。

## Retain a reference / 保留一个对照

Open **Compare** beside **Display**, then **Keep this result**. Resample or change sample size to compare with the dashed reference. For example, in the CLT lab retain n = 1, then change to n = 30 or 100.

打开 **显示选项** 旁的 **对照**，点击 **保留当前结果**。重新抽样或改变样本量后，可与虚线参照比较。例如在 CLT 中先保留 n = 1，再改成 n = 30 或 100。

The reference includes its distribution, shape, sample size, repetitions where applicable, and random seed. It survives language changes and navigation within the session. Replace or clear it explicitly. Changing the probability model or distribution alignment pauses comparison until compatible settings return or a new result is saved. A fresh browser session starts without references.

对照记录分布、形状参数、样本量、重复次数（适用时）和随机种子。同一会话中，切换语言或页面不会清除它；可主动替换或清除。改变概率模型或分布对齐方式时，对照暂停；恢复对应参数或保留新结果后继续。新的浏览器会话不保留旧对照。

Both densities use common bins and each run's full observation count. CLT standardization uses each run's own n. Values outside the display or bins are reported; hiding them does not remove them from the normalization or statistics.

两组密度使用相同分箱，各自按完整观测数归一化；CLT 标准化各自使用对应的 n。视窗或分箱外的数据会明确说明，不从归一化分母及统计计算中移除。

## Replay the CLT construction / 回看 CLT 图形的生成

Open the collapsed **Understand sampling** section below the main CLT plots:

在 CLT 主图下方展开默认收起的 **理解抽样过程**：

1. **Draw a group / 抽一组样本**: see all observations in the first actual group of the current run.
2. **Take its mean / 计算均值**: reveal their arithmetic mean and the corresponding line.
3. **Repeat / 重复积累**: reveal the first 10, 50, 100, 500, or all groups, using fixed bins.

These steps replay existing data and never advance the random seed. The instructional histogram shows raw means and counts, including all extreme values. The main plot retains its chosen scale and probability-density convention. Parameter changes or resampling restart the walkthrough; changing language or opening the glossary preserves progress.

这些步骤重放已有数据，不会推进随机种子。演示直方图使用原始均值和频数，包含全部极端值；主图保持原有尺度及概率密度约定。改变实验参数或重新抽样会从第一步开始；切换语言或打开术语表会保留进度。

The classical CLT's finite-variance requirement still applies. Repeating a Cauchy experiment does not make a Gaussian limit valid.

经典 CLT 仍要求有限方差；重复 Cauchy 实验并不会使高斯极限成立。

## Information hierarchy / 信息层次

The default view shows primary parameters, core plots and brief reading cues. Display conventions and comparisons use compact popovers; derivations and the sampling walkthrough are collapsed. Critical conditions such as undefined moments and failure of the classical CLT remain visible. Detailed normalization and display-window notes remain in the mathematical sections.

默认界面展示主要参数、核心图形与简短提示。显示约定和对照功能使用小型弹出入口；推导与抽样演示默认折叠。矩不存在、经典 CLT 不适用等关键条件仍直接提示。完整的归一化及视窗说明保留在数学说明中。


## Space and hover readouts / 空间与悬浮读数

The header and metric cards use a compact shared layout. The distribution interval and secondary actions share a row on wider screens; narrow screens can wrap naturally. Main PDF/CDF plots have matching sizes. The page keeps normal scrolling for the three-row boxplot and detailed explanations rather than forcing all content into a fixed-height viewport.

标题和指标卡采用紧凑的统一布局。宽屏下，分布页的区间控制与辅助操作并排；窄屏允许自然换行。PDF 与 CDF 图保持相同尺寸；三行箱型图和详细解释仍可正常向下浏览，不强行挤进固定高度的窗口。

Hover over a sample-box summary position to read just that statistic, rounded to three significant figures. Whisker readouts use actual observations inside the fences, not the fences or the full-sample minimum and maximum. The underlying numeric data remain unchanged in charts and exports.

悬停在样本箱型图的统计位置，仅显示该项名称和三位有效数字。须线读数使用围栏内的实际观测值，不混同于围栏或全样本极值。图形与导出中的底层数值保持完整精度。


## Readings and controls / 读数与参数区

Metrics show **name = value** inline. Hover over a reading, focus its information button with Tab, or tap the button to reveal its explanation. Critical model conditions remain visible in the page. Continuous chart readouts use three significant figures (scientific notation for very small/large values); observation indices and counts stay integer-valued. Probability sliders retain their step precision. Formatting does not round the stored data or change calculations.

指标采用 **名称 = 数值**。鼠标悬停、Tab 聚焦说明按钮或轻触按钮，可查看解释；关键适用条件仍直接显示。连续量的图表读数统一为三位有效数字，极大或极小值使用科学计数法；观测序号和计数保留整数，概率滑块保留步长精度。显示格式不改变数据与计算精度。

At desktop widths of at least 1,100 px and heights of at least 760 px, the experiment's control bar stays below the app header while scrolling through its results. It is scoped to the experiment and releases before the shared glossary/footer. Smaller windows use ordinary scrolling. This keeps the relevant controls available at the boxplot and tail-convergence plot without reducing every plot to fit one screen.

宽度至少 1,100 px、高度至少 760 px 的桌面窗口中，实验参数栏在浏览结果时停留在应用顶栏下方，仅作用于当前实验区域，到公共术语与页脚前结束。小窗口保持普通滚动。这样看箱型图或样本峰度变化图时，仍可直接调整参数。

The interface separates immediate results from optional explanations and keeps controls near the active experiment. Related concepts use consistent colors, terminology and chart conventions.

界面将主结果与补充解释分层展示，让控件贴近当前实验；相关概念使用一致的颜色、术语和图形约定。


Interval endpoints belong to the selected population probability interval and use teal with white outlines. Purple sample points denote observations beyond the sample's 1.5 IQR fences. Moving the interval changes the PDF area, CDF markers and sample-plot band; it does not change the sample fences. **Show fence lines** hides or shows the dotted thresholds and their labels, while the outlying observations remain visible.

区间端点属于选中的总体概率区间，使用青色白描边；紫色样本点表示落在样本 1.5 IQR 围栏之外的观测。调整区间只联动 PDF 面积、CDF 端点与样本图阴影，不改变样本围栏。“显示围栏线”仅切换阈值点线及标签，保留围栏外观测标记。
