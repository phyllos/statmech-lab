# Learning interactions

English · [简体中文](../zh-CN/interactions.md) · [Project overview](../../README.md)

The experiments combine reproducible calculations with linked plots and optional explanations.

## One interval, three views

In **Distributions & boxplots**, the interval slider links the PDF area, the two CDF endpoints and the band behind the sample points to the same x interval. Sample points use consistent circular markers with purple indicating observations beyond the fences. Interval selection changes the band without changing the point styling.

The interval slider is the only selection control. Its default 0.25–0.75 interval spans the population IQR; the sample box retains its own estimated quartiles. Alignment, visible range and fences are available under **Display**.

## Retain a reference

Open **Compare** beside **Display**, then **Keep this result**. Resample or change sample size to compare with the dashed reference. For example, in the CLT lab retain n = 1, then change to n = 30 or 100.

The reference includes its distribution, shape, sample size, repetitions where applicable, and random seed. It survives language changes and navigation within the session. Replace or clear it explicitly. Changing the probability model or distribution alignment pauses comparison until compatible settings return or a new result is saved. A fresh browser session starts without references.

Both densities use common bins and each run's full observation count. CLT standardization uses each run's own n. Values outside the display or bins are reported; hiding them does not remove them from the normalization or statistics.

## Replay the CLT construction

Open the collapsed **Understand sampling** section below the main CLT plots:

1. **Draw a group**: see all observations in the first actual group of the current run.
2. **Take its mean**: reveal their arithmetic mean and the corresponding line.
3. **Repeat**: reveal the first 10, 50, 100, 500, or all groups, using fixed bins.

These steps replay existing data and never advance the random seed. The instructional histogram shows raw means and counts, including all extreme values. The main plot retains its chosen scale and probability-density convention. Parameter changes or resampling restart the walkthrough; changing language or opening the glossary preserves progress.

The classical CLT requires finite variance. Repeating a Cauchy experiment does not make a Gaussian limit valid.

## Information hierarchy

The default view shows primary parameters, core plots and brief reading cues. Display conventions and comparisons use compact popovers; derivations and the sampling walkthrough are collapsed. Critical conditions such as undefined moments and failure of the classical CLT remain visible. Detailed normalization and display-window notes remain in the mathematical sections.

## Space and hover readouts

The header and metric cards use a compact shared layout. Wide control panels place Parameters on the left and actions on the right. Compact panels use two rows: Parameters/Resample, then Display/Compare where available. Main PDF/CDF plots have matching sizes. The three-row boxplot and detailed explanations follow in the page's vertical flow.

Hover over a sample-box summary position to read just that statistic, rounded to three significant figures. Whisker readouts use actual observations inside the fences, not the fences or the full-sample minimum and maximum. The underlying numeric data remain unchanged in charts and exports.

## Readings and controls

Metrics show **name = value** inline. Hover over a reading, focus its information button with Tab, or tap the button to reveal its explanation. Critical model conditions remain visible in the page. Continuous chart readouts use three significant figures (scientific notation for very small/large values); observation indices and counts stay integer-valued. Probability sliders retain their step precision. Formatting does not round the stored data or change calculations.

The control panel stays below the app header while scrolling through the active experiment and releases at the end of that workspace. Parameters start expanded and can be collapsed. In narrow panels or short windows, the parameter area has a bounded height and scrolls internally; toolbar actions remain accessible above it.

The interface separates immediate results from optional explanations and keeps controls near the active experiment. Related concepts use consistent colors, terminology and chart conventions.

Interval endpoints belong to the selected population probability interval and use teal with white outlines. Purple sample points denote observations beyond the sample's 1.5 IQR fences. Moving the interval changes the PDF area, CDF markers and sample-plot band; it does not change the sample fences. **Show fence lines** hides or shows the dotted thresholds and their labels, while the outlying observations remain visible.
