#!/usr/bin/env python3
"""
Turn a small pptx template (one example slide per "role": title, TOC,
section divider, chart-layout, table-layout, ...) into a deck with however
many slides your report actually needs, in whatever order you need them --
by cloning each role slide as many times as the outline calls for.

This automates the exact manual steps used to build the 30-slide resume
report this session: loop `add_slide.py` to clone each layout N times,
rewrite `<p:sldIdLst>` in presentation.xml into the desired final order,
then run `clean.py` to drop any role slide that ends up unused (e.g. a
layout in the template you didn't need this time, like the bullet-point
layout that got dropped from the 30-slide deck in favor of chart/table
slides only).

Depends on the `pptx` skill's helper scripts (add_slide.py, clean.py) --
load that skill first, or pass --pptx-scripts pointing at its scripts/ dir.

Usage as a library:

    from restructure import restructure

    role_map = {
        "title": "slide1.xml", "toc": "slide2.xml", "divider": "slide3.xml",
        "chart": "slide5.xml", "table": "slide6.xml",
    }
    outline = ["title", "toc", "divider", "chart", "chart", "table", "divider", ...]
    restructure("template.pptx", outline, role_map, "draft.pptx")

Usage as a CLI (outline/role_map passed as JSON):

    python restructure.py template.pptx outline.json draft.pptx

outline.json:
    {
      "role_map": {"title": "slide1.xml", "toc": "slide2.xml", ...},
      "outline": ["title", "toc", "divider", "chart", "chart", "table", ...]
    }
"""
from __future__ import annotations

import glob
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SLDID_RE = re.compile(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>')
SLDIDLST_RE = re.compile(r"(<p:sldIdLst>).*?(</p:sldIdLst>)", re.DOTALL)
REL_RE = re.compile(r'<Relationship Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"')


def find_pptx_skill_scripts() -> Path:
    """Locates the `pptx` skill's scripts/ directory (has add_slide.py, clean.py)."""
    for base in ("~/.claude/skills", "/root/.claude/skills"):
        for hit in glob.glob(str(Path(base).expanduser() / "**" / "add_slide.py"), recursive=True):
            return Path(hit).parent
    raise FileNotFoundError(
        "Could not find the `pptx` skill's add_slide.py. Load the `pptx` skill "
        "first, or pass its scripts/ directory explicitly."
    )


def _unzip(pptx_path: str, dest: Path) -> None:
    with zipfile.ZipFile(pptx_path) as z:
        z.extractall(dest)


def _rezip(src_dir: Path, out_path: str) -> None:
    out_path = Path(out_path)
    if out_path.exists():
        out_path.unlink()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src_dir.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(src_dir))


def _rel_map(unpacked: Path) -> dict[str, str]:
    """slide filename -> rId, from ppt/_rels/presentation.xml.rels."""
    rels = (unpacked / "ppt/_rels/presentation.xml.rels").read_text()
    return {fn: rid for rid, fn in REL_RE.findall(rels)}


def _sldid_map(unpacked: Path) -> dict[str, str]:
    """rId -> id, from ppt/presentation.xml's <p:sldIdLst>."""
    xml = (unpacked / "ppt/presentation.xml").read_text()
    return {rid: sid for sid, rid in SLDID_RE.findall(xml)}


def restructure(
    template_path: str,
    outline: list[str],
    role_map: dict[str, str],
    out_path: str,
    pptx_scripts_dir: str | Path | None = None,
    keep_workdir: bool = False,
) -> str:
    """Builds a draft deck with one slide per `outline` entry, in order.

    Each entry in `outline` is a role name (a key of `role_map`). The first
    occurrence of a role uses the template's own base slide for that role;
    later occurrences clone it via add_slide.py. Any base slide whose role
    never appears in `outline` is dropped (via clean.py) -- e.g. drop a
    layout from the template you don't need this time.

    Returns the path to the resulting draft pptx (== out_path).
    """
    scripts_dir = Path(pptx_scripts_dir) if pptx_scripts_dir else find_pptx_skill_scripts()
    workdir = Path(tempfile.mkdtemp(prefix="restructure_"))
    unpacked = workdir / "unpacked"
    _unzip(template_path, unpacked)

    rel_map = _rel_map(unpacked)
    sldid_map = _sldid_map(unpacked)

    # (id, rId) pair to place at each outline position, in order.
    ordered_pairs: list[tuple[str, str]] = []
    used_once: set[str] = set()

    for role in outline:
        if role not in role_map:
            raise KeyError(f"outline references unknown role {role!r} (not in role_map)")
        base_file = role_map[role]
        if role not in used_once:
            # first occurrence: use the template's own slide for this role
            used_once.add(role)
            target_file = base_file
        else:
            result = subprocess.run(
                [sys.executable, str(scripts_dir / "add_slide.py"), str(unpacked) + "/", base_file],
                capture_output=True, text=True, cwd=workdir,
            )
            if result.returncode != 0:
                raise RuntimeError(f"add_slide.py failed for role {role!r}:\n{result.stderr}")
            m = re.search(r"Created ppt/slides/(slide\d+\.xml)", result.stdout)
            if not m:
                raise RuntimeError(f"couldn't parse add_slide.py output:\n{result.stdout}")
            target_file = m.group(1)
            # refresh maps -- add_slide.py just added a new rel + sldId
            rel_map = _rel_map(unpacked)
            sldid_map = _sldid_map(unpacked)

        rid = rel_map[target_file]
        sid = sldid_map[rid]
        ordered_pairs.append((sid, rid))

    # rewrite sldIdLst into the exact outline order (drops any role not used)
    new_lst = "<p:sldIdLst>" + "".join(
        f'<p:sldId id="{sid}" r:id="{rid}"/>' for sid, rid in ordered_pairs
    ) + "</p:sldIdLst>"
    pres_path = unpacked / "ppt/presentation.xml"
    pres_xml = pres_path.read_text()
    pres_xml = SLDIDLST_RE.sub(lambda m: new_lst, pres_xml, count=1)
    pres_path.write_text(pres_xml)

    # drop any base-role slide that's now unreferenced (e.g. an unused layout)
    clean_result = subprocess.run(
        [sys.executable, str(scripts_dir / "clean.py"), str(unpacked) + "/"],
        capture_output=True, text=True, cwd=workdir,
    )
    print(clean_result.stdout, end="")
    if clean_result.returncode != 0:
        raise RuntimeError(f"clean.py failed:\n{clean_result.stderr}")

    _rezip(unpacked, out_path)

    if not keep_workdir:
        shutil.rmtree(workdir, ignore_errors=True)
    else:
        print(f"(workdir kept at {workdir})")

    return out_path


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    template_path, outline_json, out_path = sys.argv[1:4]
    spec = json.loads(Path(outline_json).read_text())
    result = restructure(template_path, spec["outline"], spec["role_map"], out_path)
    print(f"wrote {result} ({len(spec['outline'])} slides)")


if __name__ == "__main__":
    main()
