#!/usr/bin/env python3
"""
Dump every slide's shapes, bracket-style placeholder text, and geometry
from a .pptx template -- the first thing to run against any new template
before writing a content spec against it.

Why this exists: filling a template mechanically requires knowing, for
each slide, (a) which shapes hold `[bracket placeholder]` text you can
target with deck_lib.find_shape(), and (b) the exact EMU position/size of
any image placeholder or table, so generated charts/tables land in the
right box. Reading this by hand (python-pptx one-off REPL commands) is
exactly what this script replaces.

Usage:
    python inspect_template.py template.pptx
    python inspect_template.py template.pptx --slide 5   # just one slide
"""
import argparse
import sys

from pptx import Presentation

EMU_PER_IN = 914400


def emu_to_in(v):
    return round(v / EMU_PER_IN, 3) if v is not None else None


def describe_shape(shp):
    geom = f"L={emu_to_in(shp.left)}in T={emu_to_in(shp.top)}in W={emu_to_in(shp.width)}in H={emu_to_in(shp.height)}in"
    parts = [f"- {shp.shape_type!s:<14} name={shp.name!r:<22} {geom}"]
    if shp.has_text_frame:
        for pi, para in enumerate(shp.text_frame.paragraphs):
            text = "".join(r.text for r in para.runs)
            if text.strip():
                is_ph = text.strip().startswith("[") and text.strip().endswith("]")
                tag = "  <-- bracket placeholder" if is_ph else ""
                parts.append(f"    p{pi}: {text!r}{tag}")
    if shp.has_table:
        tbl = shp.table
        parts.append(f"    table: {len(tbl.rows)} rows x {len(tbl.columns)} cols")
        for r in tbl.rows:
            parts.append("      row: " + " | ".join(c.text for c in r.cells))
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx_path")
    ap.add_argument("--slide", type=int, default=None, help="1-indexed slide number, omit for all")
    args = ap.parse_args()

    prs = Presentation(args.pptx_path)
    print(f"# {args.pptx_path}")
    print(f"# slide size: {emu_to_in(prs.slide_width)}in x {emu_to_in(prs.slide_height)}in "
          f"({prs.slide_width} x {prs.slide_height} EMU)")
    print(f"# total slides: {len(prs.slides._sldIdLst)}\n")

    for i, slide in enumerate(prs.slides, 1):
        if args.slide is not None and i != args.slide:
            continue
        print(f"=== Slide {i} (layout: {slide.slide_layout.name}) ===")
        for shp in slide.shapes:
            print(describe_shape(shp))
        print()


if __name__ == "__main__":
    sys.exit(main())
