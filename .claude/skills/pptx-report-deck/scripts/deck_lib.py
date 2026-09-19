"""
Fill helpers for `[bracket placeholder]` style pptx templates -- the kind
of template where every fill-in spot is a text run that reads like
`[핵심 메시지를 한 문장으로]` or `[Insert headline here]`.

These are the mechanical parts of turning a restructured draft deck (see
restructure.py) into a finished report: swap placeholder text for real
text, drop a chart PNG into an image placeholder at its exact box, resize
a table to however many rows your data needs, bold/color the keywords in
a sentence, and keep the footer page count and source footnote correct.

What's deliberately NOT in here: the actual sentences, which numbers to
bold, how many slides a section needs, what the data even is. That
judgment belongs in the per-report driver script you write each time (see
examples/fill_deck.py for the pattern) -- this module just makes the
mechanical part fast and hard to get wrong (off-by-one page numbers,
tables overlapping the box below them, run formatting getting clobbered).
"""
from __future__ import annotations

import copy

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt


# ------------------------------------------------------------------ finding
def find_shape(slide, text_startswith=None, text_exact=None, name=None):
    """Locate a shape by its exact/prefix text content or by shape name.

    Raises if not found -- fail loudly rather than silently skip a slide,
    since a missed placeholder means a stray `[bracket]` shipping in the
    final deck.
    """
    for shp in slide.shapes:
        if name is not None and shp.name == name:
            return shp
        if shp.has_text_frame:
            t = shp.text_frame.text.strip()
            if text_exact is not None and t == text_exact:
                return shp
            if text_startswith is not None and t.startswith(text_startswith):
                return shp
    raise ValueError(f"shape not found: {text_startswith or text_exact or name!r}")


def find_table_shape(slide):
    for shp in slide.shapes:
        if shp.has_table:
            return shp
    raise ValueError("no table shape on this slide")


# --------------------------------------------------------------- plain text
def set_plain(shape, text: str) -> None:
    """Replaces a shape's first paragraph text, keeping the first run's
    formatting (font/size/color/bold) and clearing any extra runs.

    Never do `shape.text_frame.text = "..."` on a styled template shape --
    that collapses the paragraph to one unstyled run and silently drops
    the template's font/size/color.
    """
    p = shape.text_frame.paragraphs[0]
    runs = p.runs
    if not runs:
        run = p.add_run()
        run.text = text
        return
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


# ------------------------------------------------------------- rich (bold/color keywords)
def split_keywords(text: str, keywords: list[str]) -> list[tuple[str, bool]]:
    """Splits `text` into (segment, is_keyword) pieces for each keyword
    substring, in the order they appear. A keyword not found in the text
    is silently skipped (so a slightly-off keyword string doesn't crash a
    whole deck build -- but do check your output, a skipped keyword means
    that number won't get highlighted).
    """
    segments = []
    pos = 0
    for kw in keywords:
        idx = text.find(kw, pos)
        if idx == -1:
            continue
        if idx > pos:
            segments.append((text[pos:idx], False))
        segments.append((text[idx:idx + len(kw)], True))
        pos = idx + len(kw)
    if pos < len(text):
        segments.append((text[pos:], False))
    return segments


def set_rich(shape, segments, size_pt, bold, color: RGBColor, kw_color: RGBColor, font="Pretendard"):
    """Rebuilds a shape's first paragraph as a sequence of runs, one per
    `(text, is_keyword)` segment from split_keywords(). Keyword segments
    get bold + kw_color; everything else gets the base bold/color.
    """
    p = shape.text_frame.paragraphs[0]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    for text, is_kw in segments:
        if text == "":
            continue
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size_pt)
        run.font.bold = True if is_kw else bold
        run.font.color.rgb = kw_color if is_kw else color
        run.font.name = font


def set_text_with_keywords(shape, text, keywords, size_pt, bold, color, kw_color, font="Pretendard"):
    """Convenience: split_keywords + set_rich in one call."""
    set_rich(shape, split_keywords(text, keywords), size_pt, bold, color, kw_color, font)


# --------------------------------------------------------------------- image
def add_image_into_placeholder(slide, placeholder_text_startswith: str, image_path: str):
    """Removes the `[image placeholder]` shape and drops a picture in at
    *its exact position and size* -- read live off the placeholder shape,
    so you never have to hardcode EMU coordinates for a given template.
    Generate your chart PNG at the same aspect ratio (see chart_lib's
    figsize) so it isn't stretched or letterboxed.
    """
    ph = find_shape(slide, text_startswith=placeholder_text_startswith)
    left, top, width, height = ph.left, ph.top, ph.width, ph.height
    ph._element.getparent().remove(ph._element)
    return slide.shapes.add_picture(image_path, left, top, width, height)


# --------------------------------------------------------------------- footer
def set_footer(slide, page_num: int, total: int, suffix_hint: str = "/ ") -> bool:
    """Finds the `N / TOTAL` footer textbox (by looking for a shape whose
    text contains suffix_hint, e.g. "/ 6" in the source template) and
    rewrites it as `page_num / total`. Returns False if no footer shape
    exists on this slide (some layouts, like section dividers, may not
    have one -- that's fine, not every slide needs a page count).
    """
    for shp in slide.shapes:
        if shp.has_text_frame and suffix_hint in shp.text_frame.text:
            set_plain(shp, f"{page_num} / {total}")
            return True
    return False


def set_source_footnote(
    slide,
    text: str,
    placeholder_text_startswith: str = "[출처",
    avoid_shape_hint: str | None = "/ ",
    gap_emu: int = 137160,
) -> None:
    """Sets the source citation and right-aligns it -- the convention for
    a bottom-right footnote.

    If the template also has a page-number footer ("N / TOTAL") sitting in
    that same bottom-right corner, right-aligning both to the slide's edge
    makes their boxes overlap -- they'd render on top of each other. Pass
    `avoid_shape_hint` (a substring found in the footer's text, default
    matches "N / TOTAL" style footers) and this narrows the source box so
    it ends `gap_emu` before the footer begins, instead of at the slide
    edge -- the footnote then sits just to the footer's left, both still
    reading as "bottom-right". Pass None to skip this and just right-align
    to the box's own original edge.
    """
    shp = find_shape(slide, text_startswith=placeholder_text_startswith)
    shp.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    set_plain(shp, text)

    if avoid_shape_hint:
        for other in slide.shapes:
            if other is shp or not other.has_text_frame:
                continue
            if avoid_shape_hint in other.text_frame.text:
                new_right_edge = other.left - gap_emu
                shp.width = Emu(max(int(new_right_edge - shp.left), 1))
                break


# ---------------------------------------------------------------------- table
def fit_table(
    slide,
    header: list[str],
    rows: list[list[str]],
    below_shape_names: list[str] | None = None,
    gap_emu: int = 91440,
    min_row_h_emu: int = 190000,
    max_row_h_emu: int = 274320,
):
    """Resizes a table to fit `len(rows)` data rows (adding/removing `<a:tr>`
    rows as needed, since python-pptx has no add_row API), fills every
    cell, and pushes any shapes listed in `below_shape_names` (e.g. an
    "insight" callout box, a source footnote) down to sit just below the
    table's new bottom edge -- so a table with more rows than the template
    shipped with doesn't overlap the box underneath it.

    The available vertical budget is computed from the LAST shape in
    `below_shape_names` (read before this call moves anything) down to
    the slide's own bottom margin, so you don't need to know or hardcode
    the template's EMU coordinates -- they're read live off the shapes.

    Row height shrinks (down to min_row_h_emu) and cell font size follows
    it, so a 10-row table stays legible without spilling past the box
    below it; a table with <= the template's default row count is left at
    the template's own row height (this is a no-op for the common case).
    """
    tbl_shape = find_table_shape(slide)
    table = tbl_shape.table
    tbl_elem = table._tbl

    n_data = len(rows)
    ncols = len(header)
    total_rows = n_data + 1
    cur_data = len(tbl_elem.tr_lst) - 1
    if n_data > cur_data:
        last_tr = tbl_elem.tr_lst[-1]
        for _ in range(n_data - cur_data):
            tbl_elem.append(copy.deepcopy(last_tr))
    elif n_data < cur_data:
        for _ in range(cur_data - n_data):
            tbl_elem.remove(tbl_elem.tr_lst[-1])

    below_shapes = [find_shape(slide, name=n) for n in (below_shape_names or [])]
    if below_shapes:
        # budget = space between the table's current top and the bottom
        # edge of the last "below" shape, read BEFORE we move anything --
        # i.e. the template's own default layout, which we treat as the
        # ground truth for "how much room this slide has".
        last_shape = below_shapes[-1]
        table_area_bottom = last_shape.top + last_shape.height
        avail = table_area_bottom - tbl_shape.top
    else:
        avail = tbl_shape.height  # no repositioning to do; keep default budget

    row_h = min(max_row_h_emu, max(min_row_h_emu, avail // total_rows))
    for tr in tbl_elem.tr_lst:
        tr.set("h", str(row_h))
    tbl_shape.height = row_h * total_rows

    font_sz = 9 if row_h >= 260000 else (8 if row_h >= 220000 else 7)

    for c, htext in enumerate(header):
        _set_cell_text(table.cell(0, c), htext, font_sz)
    for r, row in enumerate(rows, start=1):
        for c in range(ncols):
            _set_cell_text(table.cell(r, c), row[c], font_sz)

    if below_shapes:
        cursor = tbl_shape.top + tbl_shape.height + gap_emu
        for shp in below_shapes:
            shp.top = Emu(int(cursor))
            cursor += shp.height + gap_emu

    return table


def _set_cell_text(cell, text, font_sz):
    p = cell.text_frame.paragraphs[0]
    if not p.runs:
        run = p.add_run()
        run.text = text
        run.font.size = Pt(font_sz)
        return
    p.runs[0].text = text
    p.runs[0].font.size = Pt(font_sz)
    for r in p.runs[1:]:
        r.text = ""
