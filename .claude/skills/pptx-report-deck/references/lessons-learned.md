# Lessons learned (read before extending this skill)

## The source-footnote / page-number overlap bug

The first version of this deck (before it became a skill) right-aligned
the source footnote to "put it at the bottom-right" as requested, and
separately left the page-number footer ("N / 30") at its own template
position -- also bottom-right, on every content slide. Both boxes had
the *same* right edge (`457200 + 11277569 == 10271729 + 1463040 ==
11734769` in the original template, to the EMU), and their vertical
ranges overlapped by design even before either box was touched (the
template's own source-box height and footer-box height overlap by
~0.15in). Right-aligning the footnote text made it render directly
through the page number on every one of the 22 content slides -- a
defect that shipped in the first delivered file before it was caught by
manually re-checking shape geometry (there was no automated check for
it at the time).

`deck_lib.set_source_footnote` now fixes this by default: it looks for a
sibling shape matching `avoid_shape_hint` (default `"/ "`, matching a
"N / TOTAL" footer) and narrows the footnote box so its right edge stops
`gap_emu` (default 0.15in) before the footer begins, rather than at the
slide edge. `qa_check.py`'s overlap check exists specifically because
this bug shipped once with no automated catch -- run it on every deck,
even ones that "should obviously be fine."

**If you're adapting this to a template where the footnote and footer
don't share a corner** (e.g. the footnote is bottom-left, or there's no
page-number footer at all), the default behavior is harmless -- it just
won't find a matching shape and leaves the footnote at its own edge.
Only worry about this if your template's page number lives somewhere
`avoid_shape_hint` might false-match (unlikely, since it's a specific
"/ " substring) or where you actively *want* the footnote to run all the
way to the slide edge regardless (pass `avoid_shape_hint=None`).

## Why `fit_table` reads geometry live instead of hardcoding EMU values

The first version of the table-resizing logic hardcoded the template's
own coordinates as Python constants (`SOURCE_TOP_DEFAULT = 6217920`,
etc.), discovered by manually reading the unpacked slide XML once. That
only works for the exact template it was measured against -- port the
skill to a different template and every one of those constants is wrong
silently (no error, just a table that overlaps something or leaves a
huge gap).

`deck_lib.fit_table` instead reads the "below" shapes' current
`.top`/`.height` at call time and computes the available budget from
that, on the (safe) assumption that a freshly-cloned, not-yet-modified
slide still has the template's own default layout. This is why
`fit_table` must be called on each slide before anything else on that
slide has permanently moved the insight-box/footnote shapes -- if you
write a driver that calls `fit_table` twice on the same slide, or moves
those shapes some other way first, the second call will compute its
budget from the *already-shrunk* position, not the template's original
one.

## Why `restructure.py` shells out to `add_slide.py` instead of
reimplementing slide duplication

Duplicating a pptx slide correctly means handling relationship IDs,
`[Content_Types].xml` registration, and not sharing chart/diagram/OLE
parts between the original and the copy (they'd otherwise silently
share state -- editing one slide's embedded chart would edit the
other's too). The `pptx` skill's `add_slide.py` already solves this
robustly; reimplementing it here would be maintaining two copies of the
same non-trivial bookkeeping. `restructure.py`'s value-add is purely the
outline-driven ordering and cleanup on top of that primitive.
