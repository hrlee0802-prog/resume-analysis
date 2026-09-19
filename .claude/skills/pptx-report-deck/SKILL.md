---
name: pptx-report-deck
description: Builds a chart-and-table-centric PowerPoint report deck (any slide count -- 10, 30, 50+) from a structured dataset and a "[bracket placeholder]" pptx template, by cloning template slides to fit the outline, generating brand-styled matplotlib charts, and filling every placeholder, table, and image box programmatically. Use this whenever the user asks for a "발표자료"/"보고서"/"report deck"/"slide deck" built FROM data (a markdown report, a CSV, analysis numbers, survey results) rather than freehand slide authoring -- especially when they specify a slide-count target, ask for "표와 이미지 중심" (table/chart-centric, not bullet text), want key numbers bolded or colored, or want a source footnote. Also trigger when the user wants to turn a one-off pptx-building session into a reusable, repeatable workflow ("이 작업을 스킬로 만들어줘"). Don't use this for a single freehand slide, a deck with no data backing, or when no template exists yet and the user just wants "make me a deck" with full design freedom -- for those, author the deck directly instead.
---

# PPTX Report Deck Builder

## What this is for

A data report deck (population stats, survey results, a quarterly metrics
review, anything with "here are N distributions, each worth one slide")
has a repeatable shape: title, TOC, per-section dividers, then one
chart-or-table slide per data point, with a consistent headline/footnote
style throughout. Authoring that freehand -- one slide at a time, copying
formatting by hand -- is slow and inconsistent. This skill instead treats
the deck as **template slides cloned to fit an outline, then filled by a
script**, the same way this was built for the "이력서 100개 종합 분석
보고서" 30-slide deck this skill was extracted from.

The mechanical parts (cloning slides, resizing a table to however many
rows the data needs, positioning a chart image at the placeholder's exact
box, bolding keywords, keeping page numbers and a source footnote
correct) are scripts in `scripts/`. The parts that need judgment --
what the outline should be, what each headline sentence says, which
numbers matter enough to bold -- are yours to write fresh each time in
a short driver script, following the pattern in `examples/`.

## Prerequisites

- The `pptx` skill must be loaded first (or at least reachable) --
  `restructure.py` shells out to its `add_slide.py` and `clean.py`.
  `scripts/restructure.py` auto-locates it under `~/.claude/skills` or
  `/root/.claude/skills`; pass `pptx_scripts_dir=` explicitly if it lives
  elsewhere.
- `python-pptx`, `matplotlib` (`pip install python-pptx matplotlib`).
- For Korean (or other non-Latin) chart labels: a font with that
  coverage. `chart_lib.py` looks for NanumGothic; install it with
  `apt-get install -y fonts-nanum` if chart text renders as tofu boxes.
  For other scripts/languages, point `chart_lib._register_korean_font`
  (or just install matching system fonts and let matplotlib fall back)
  at the right font files.
- A `[bracket placeholder]`-style template -- one example slide per
  reusable role (title, TOC, section divider, a chart-layout slide, a
  table-layout slide, ...). `assets/biyard-report-template.pptx` is the
  template this was built against, if you don't have your own.

## Workflow

### 1. Inspect the template

```bash
python3 scripts/inspect_template.py your-template.pptx
```

For every slide, read off: which shapes hold `[bracket]` placeholder
text (these are what you'll target with `deck_lib.find_shape`), the
exact size/position of any image placeholder (so generated charts match
its aspect ratio and don't get cropped/padded), and whether a table
slide has a "below" chain of boxes -- an insight callout, a source
footnote -- that need to shift down if the table grows past its default
row count.

This replaces reading a template by hand in a python-pptx REPL, which is
how this was actually figured out the first time.

### 2. Decide the outline, then restructure

Design the deck as a sequence of **roles** (`title`, `toc`, `divider`,
`chart`, `table`, ...), one entry per final slide, based on what the data
actually needs -- not a fixed slide count. A distribution with a handful
of categories is one chart slide; a ranked list worth citing exact
numbers on gets a companion table slide; a section with 5+ data points
gets a divider. Let the data drive the count (this outline landed on 30
slides for 100-record survey data across 5 report sections -- a smaller
dataset should produce a shorter deck, not be padded out to match).

```python
from restructure import restructure

role_map = {
    "title": "slide1.xml", "toc": "slide2.xml", "divider": "slide3.xml",
    "chart": "slide5.xml", "table": "slide6.xml",
}
outline = ["title", "toc", "divider", "chart", "chart", "table", "divider", ...]
restructure("template.pptx", outline, role_map, "draft.pptx")
```

This clones each role slide as many times as the outline needs (only the
*first* use of a role reuses the template's own slide; later uses are
clones), rewrites the slide order to match the outline exactly, and drops
any template slide whose role never got used (e.g. a layout in the
template you didn't need this time).

### 3. Generate chart images

Use `chart_lib.hbar_chart` for ranked/count data (the overwhelming
majority of report charts -- see `references/chart-choices.md` for when
a different form fits better). Pass `figsize` matching the image
placeholder's real aspect ratio from step 1. See
`examples/gen_charts.py` for the full worked pattern, including the
brand `Palette`.

### 4. Write the fill driver and run it

This is the part that needs your judgment, not a bundled script. For
each content slide decide: the headline sentence (factual, describing
what the chart/table shows -- see `references/writing-headlines.md`),
which substrings in it are keywords to bold/color, and for a table slide
its header/rows/insight line. Then call `deck_lib` to apply it:

```python
from deck_lib import (find_shape, set_plain, set_text_with_keywords,
                       add_image_into_placeholder, fit_table,
                       set_source_footnote, set_footer)

set_text_with_keywords(headline_shape, "SQL 31명(31%)이 1위다.",
                        keywords=["31명(31%)"],
                        size_pt=19, bold=True, color=WHITE, kw_color=ORANGE)
add_image_into_placeholder(slide, "[이미지", "charts/skills.png")
fit_table(slide, header, rows, below_shape_names=["Rounded Rectangle 8", "TextBox 9"])
set_source_footnote(slide, "출처: ...")   # auto-avoids a page-number footer, see below
set_footer(slide, page_num, total, suffix_hint="/ 6")
```

`examples/fill_deck.py` is the complete driver for the resume-report
deck -- copy its structure (a `CONTENT` list of `(slide_index, section,
kind, subtopic, headline, keywords, payload)` tuples processed in a
loop) rather than starting from a blank file.

**Why `fit_table` and `set_source_footnote` matter more than they look:**
a table sized for the template's default row count will visually collide
with whatever sits below it (an insight box, a footnote) the moment your
data needs more rows than the template shipped with -- `fit_table`
resizes the table and pushes those boxes down to stay clear. Separately,
a source footnote right-aligned to the slide edge can land exactly where
a page-number footer already sits in that same corner; `set_source_footnote`
narrows the footnote box to stop short of the footer instead. Both are
real bugs this skill shipped once (see `references/lessons-learned.md`)
before the fix was folded into the library -- don't hand-roll either of
these from scratch.

### 5. QA before calling it done

```bash
python3 scripts/qa_check.py final.pptx
# plus, from the pptx skill:
python3 <pptx-skill>/scripts/office/validate.py final.pptx --original template.pptx
markitdown final.pptx | grep -iE '\[.*\]|lorem|TODO'
```

`qa_check.py` catches leftover `[bracket]` placeholders, shapes that run
off the slide edge, and text boxes that significantly overlap each other
(tuned to ignore a template's own intentional tight spacing -- see the
script's docstring for the calibration if you adapt it). `validate.py`
catches OOXML-level corruption. Content correctness (do the numbers in
your driver script actually match the source data) is still on you --
these scripts check layout, not truth.

If LibreOffice (`soffice`) is available in your environment, also render
to images and eyeball a few slides -- it wasn't available in the sandbox
this skill was built in, which is exactly why `qa_check.py` exists: to
catch what a missing visual QA step would otherwise let through.

## Reference files

- `references/writing-headlines.md` -- factual-tone headline writing and
  keyword-selection guidance (what to bold, what not to).
- `references/chart-choices.md` -- when hbar_chart vs stat_bar_chart vs
  "don't chart this" is the right call.
- `references/lessons-learned.md` -- the overlap bug, why it happened,
  and what the fix generalizes to for templates this hasn't been tested
  against.

## Files

```
scripts/
  inspect_template.py   dump shapes/placeholders/geometry from any template
  chart_lib.py           hbar_chart, stat_bar_chart (brand palette + Korean font)
  restructure.py         clone template slides to fit an outline, reorder, clean
  deck_lib.py             find/fill placeholders, bold keywords, fit tables, footnotes
  qa_check.py             leftover placeholders / off-slide shapes / overlap check
examples/
  gen_charts.py           worked chart-generation driver (resume-report dataset)
  fill_deck.py            worked fill driver (same dataset) -- copy this pattern
assets/
  biyard-report-template.pptx   the template this was built against
references/
  writing-headlines.md, chart-choices.md, lessons-learned.md
```
