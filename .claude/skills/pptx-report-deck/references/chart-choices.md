# Chart form choices

`chart_lib.py` ships two forms on purpose, not more -- a report deck
reads as one coherent system when it doesn't mix chart types without a
reason. Pick by what the data's job is (see the `dataviz` skill for the
full method this borrows from); most report-deck data is ranked
magnitude, which is why `hbar_chart` does most of the work.

## `hbar_chart` -- ranked / count data (the default)

Use for: "here's a breakdown of category X" -- gender split, age bands,
a top-N ranking, a distribution across buckets. This is the overwhelming
majority of report-deck charts. Horizontal bars beat vertical for this
because category labels (especially Korean, or anything longer than a
couple characters) wrap badly under a vertical axis but read fine as a
row label.

- 2-6 categories: renders comfortably, generous label/data-label font.
- 10-20 categories (a top-15 industry breakdown, a top-20 skill list):
  still works -- bar height and font scale down automatically -- but
  check the render; past ~20 categories, consider showing only the top
  N in the chart and putting the rest in a companion table instead of
  shrinking the chart further.

`highlight_top=True` (the default) colors the single largest bar in the
accent color -- this is a "the eye should land here" cue, not decoration.
Turn it off (`highlight_top=False`) only when no single category is
meant to read as the standout (rare for count/ranking data).

## `stat_bar_chart` -- a handful of independent rates, side by side

Use for: a closing "key metrics" slide comparing rates that come from
*different* underlying breakdowns and don't share a denominator or
category axis -- e.g. "경영학 전공 84%" next to "이직 경험 38%" next to
"자격증 없음 47%". These aren't parts of one distribution (they don't
sum to 100%), so they don't belong in one `hbar_chart` call; they're
independent facts placed next to each other for a summary glance.

Keep this to 3-6 bars. Past that, it stops reading as "a few headline
numbers" and starts looking like a chart missing its axis labels.

## When *not* to chart

- A single number (a headline stat, "평균 경력 5.4년") doesn't need a
  chart at all -- put it directly in the headline banner text, bolded.
- Two categories with a huge disparity (e.g. 1 vs 99) will produce a
  chart where the small bar is nearly invisible; consider a stat callout
  or the table form instead.
- Data that's inherently tabular and precise (an exact certification
  list with odd category names) often reads better as the table
  companion slide than forced into a chart -- see the outline-design
  section of SKILL.md for the chart-then-table pairing pattern.
