#!/usr/bin/env python3
"""
Automated QA pass for a filled deck -- run this on every deck this skill
produces, before calling it done.

Catches three classes of defect that are easy to ship by accident:
  1. Leftover `[bracket placeholder]` text -- a slide/shape the fill
     script never reached.
  2. A shape hanging off the slide edge (bottom or right).
  3. Two text-bearing shapes whose boxes overlap -- this is exactly the
     bug this skill shipped once already: a right-aligned source
     footnote and a right-aligned page-number footer both anchored to
     the same edge, overlapping and rendering on top of each other. Text
     shapes with no words in them, or a small caption sitting on a large
     background rectangle, are expected to overlap something -- that's
     normal template decoration, not a defect -- so this only flags pairs
     where BOTH shapes hold real text.

This checks layout, not content. Still separately eyeball the actual
numbers in your driver script's data against source, and run the `pptx`
skill's validate.py for OOXML-level structural correctness.

Usage:
    python3 qa_check.py final.pptx
"""
import re
import sys

from pptx import Presentation

BRACKET_RE = re.compile(r"\[[^\[\]]{2,}\]")

# Below this, a "significant" overlap is judged by how much of the SMALLER
# shape's area is covered, not raw EMU^2 -- a template's own tight label/
# value stacking (e.g. "Date" directly above its value) touches by a few
# percent and is normal; two shapes both fighting for the same corner (the
# bug this skill shipped once: a right-aligned footnote under a
# right-aligned page number) cover well over half of each other.
OVERLAP_RATIO_THRESHOLD = 0.35
# Single characters and short markers (bullet glyphs "▪", numerals like
# "01") are frequently laid out overlapping a neighboring box on purpose
# (a large decorative numeral behind a title, a bullet glyph inside its
# text box's own padding) -- ignore pairs where either side is this short.
MIN_TEXT_LEN_FOR_OVERLAP_CHECK = 3


def overlap_ratio(a, b):
    ax0, ay0, ax1, ay1 = a.left, a.top, a.left + a.width, a.top + a.height
    bx0, by0, bx1, by1 = b.left, b.top, b.left + b.width, b.top + b.height
    ox = max(0, min(ax1, bx1) - max(ax0, bx0))
    oy = max(0, min(ay1, by1) - max(ay0, by0))
    area = ox * oy
    if area == 0:
        return 0.0
    smaller = min(a.width * a.height, b.width * b.height)
    return area / smaller if smaller else 0.0


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    prs = Presentation(path)
    sw, sh = prs.slide_width, prs.slide_height

    issues = []

    for i, slide in enumerate(prs.slides, 1):
        text_shapes = []
        for shp in slide.shapes:
            if not shp.has_text_frame:
                continue
            text = shp.text_frame.text.strip()

            for m in BRACKET_RE.finditer(text):
                issues.append(f"slide {i}: leftover placeholder {m.group(0)!r} in shape {shp.name!r}")

            if shp.left is None or shp.top is None:
                continue  # inherited/placeholder geometry, skip bounds check
            if shp.top + shp.height > sh + 1000:
                issues.append(f"slide {i}: shape {shp.name!r} bottom edge past slide bottom "
                               f"({(shp.top + shp.height) / 914400:.2f}in > {sh / 914400:.2f}in)")
            if shp.left + shp.width > sw + 1000:
                issues.append(f"slide {i}: shape {shp.name!r} right edge past slide right "
                               f"({(shp.left + shp.width) / 914400:.2f}in > {sw / 914400:.2f}in)")

            if len(text) >= MIN_TEXT_LEN_FOR_OVERLAP_CHECK:
                text_shapes.append(shp)

        for a_idx in range(len(text_shapes)):
            for b_idx in range(a_idx + 1, len(text_shapes)):
                a, b = text_shapes[a_idx], text_shapes[b_idx]
                ratio = overlap_ratio(a, b)
                if ratio > OVERLAP_RATIO_THRESHOLD:
                    issues.append(f"slide {i}: shapes {a.name!r} and {b.name!r} overlap "
                                   f"{ratio:.0%} of the smaller box (text: "
                                   f"{a.text_frame.text.strip()[:20]!r} / "
                                   f"{b.text_frame.text.strip()[:20]!r})")

    if issues:
        print(f"QA FAILED -- {len(issues)} issue(s):\n")
        for issue in issues:
            print(" -", issue)
        sys.exit(1)
    else:
        print(f"QA passed: no leftover placeholders, no off-slide shapes, no overlapping text boxes "
              f"({len(prs.slides._sldIdLst)} slides checked).")


if __name__ == "__main__":
    main()
