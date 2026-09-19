"""
Reusable chart-image generator for data-report slide decks.

Produces clean horizontal-bar charts (the workhorse chart for ranked/count
data) and a small multi-bar "stat comparison" chart, styled with a brand
palette and a Korean-capable font, sized to drop straight into a pptx
picture placeholder.

Typical usage (see examples/gen_charts.py for a full worked example):

    from chart_lib import hbar_chart, stat_bar_chart, Palette

    pal = Palette(primary="#00806F", highlight="#ED7D31", text="#06231F")
    hbar_chart(
        "out/gender.png",
        labels=["남성", "여성"],
        values=[67, 33],
        palette=pal,
    )

Design notes (why it looks the way it does):
- One hue for magnitude + one accent for "the standout value" reads cleanly
  at a glance without a legend (see the dataviz skill's color-formula: this
  is a single-series magnitude chart, not a categorical-identity chart, so
  one hue + a highlight is correct -- do not rainbow it).
- Horizontal bars beat vertical for anything with text labels (Korean or
  long English labels wrap badly on a vertical x-axis).
- Direct data labels at the bar end remove the need for gridlines/axis
  ticks entirely, which keeps the chart uncluttered ("recessive axes").
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# ------------------------------------------------------------------ palette
@dataclass
class Palette:
    primary: str = "#00806F"     # main bar color
    highlight: str = "#ED7D31"   # accent for the top/standout bar
    text: str = "#06231F"        # dark text/label color
    muted: str = "#6E6E6E"       # secondary/gray text
    background: str = "#FFFFFF"


# --------------------------------------------------------------- Korean font
def _register_korean_font() -> tuple[str, str]:
    """Registers NanumGothic (regular+bold) with matplotlib if present.

    Returns (regular_family_name, bold_family_name). Falls back to
    matplotlib's default sans-serif if Nanum isn't installed -- Korean text
    will then render as tofu boxes, so install it if you see that:
        apt-get install -y fonts-nanum
    """
    candidates_reg = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    ]
    candidates_bold = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
    ]
    reg_path = next((p for p in candidates_reg if os.path.exists(p)), None)
    bold_path = next((p for p in candidates_bold if os.path.exists(p)), None)
    if reg_path is None:
        return (plt.rcParams["font.family"][0], plt.rcParams["font.family"][0])
    fm.fontManager.addfont(reg_path)
    reg_name = fm.FontProperties(fname=reg_path).get_name()
    plt.rcParams["font.family"] = reg_name
    plt.rcParams["axes.unicode_minus"] = False
    if bold_path:
        fm.fontManager.addfont(bold_path)
        bold_name = fm.FontProperties(fname=bold_path).get_name()
    else:
        bold_name = reg_name
    return reg_name, bold_name


_REG_FONT, _BOLD_FONT = _register_korean_font()


# ------------------------------------------------------------------- charts
def hbar_chart(
    out_path: str,
    labels: list[str],
    values: list[float],
    palette: Palette = Palette(),
    unit: str = "명",
    pct_of: float | None = None,
    highlight_top: bool = True,
    value_fmt=None,
    figsize: tuple[float, float] = (11.0, 4.88),
    dpi: int = 200,
) -> str:
    """Ranked horizontal bar chart. Highest value on top, direct labels.

    figsize defaults to a 2.25:1 aspect ratio -- this matches the picture
    placeholder box on the bundled biyard report template (see
    inspect_template.py to read the real placeholder size off *your*
    template and pass it here so the PNG drops in without cropping/padding).

    pct_of: if set, labels show "N명 (X%)" with X = value/pct_of*100.
        Pass the total N (e.g. 100) for count-of-N data. Leave None to
        show only the raw value (value_fmt overrides both).
    """
    n = len(labels)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(palette.background)
    ax.set_facecolor(palette.background)

    y_pos = list(range(n))
    colors = [palette.primary] * n
    if highlight_top and values:
        colors[values.index(max(values))] = palette.highlight

    bar_h = min(0.62, 9.0 / max(n, 1))
    bars = ax.barh(y_pos, values, height=bar_h, color=colors, zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontproperties=fm.FontProperties(family=_REG_FONT),
                        fontsize=max(9, min(15, 220 // max(n, 1))), color=palette.text)
    ax.invert_yaxis()

    ax.set_xlim(0, max(values) * 1.22 if values else 1)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False)

    max_v = max(values) if values else 1
    for i, (v, color) in enumerate(zip(values, colors)):
        if value_fmt:
            label = value_fmt(v)
        elif pct_of:
            label = f"{v}{unit} ({v / pct_of * 100:.0f}%)"
        else:
            label = f"{v}{unit}"
        is_hl = color == palette.highlight
        fp = fm.FontProperties(family=_BOLD_FONT if is_hl else _REG_FONT)
        txt_color = palette.highlight if is_hl else palette.text
        ax.text(v + max_v * 0.02, i, label, va="center", ha="left",
                 fontproperties=fp, fontsize=max(9, min(14, 200 // max(n, 1))),
                 color=txt_color, zorder=4)

    longest_label = max((len(str(l)) for l in labels), default=0)
    plt.subplots_adjust(left=0.22 if longest_label < 14 else 0.30,
                         right=0.97, top=0.96, bottom=0.04)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fig.savefig(out_path, facecolor=palette.background)
    plt.close(fig)
    return out_path


def stat_bar_chart(
    out_path: str,
    labels: list[str],
    values: list[float],
    value_labels: list[str] | None = None,
    palette: Palette = Palette(),
    figsize: tuple[float, float] = (11.0, 4.88),
    dpi: int = 200,
    ylim: tuple[float, float] = (0, 100),
) -> str:
    """Small vertical bar set for comparing a handful of independent rates
    side by side (e.g. a closing "key metrics" slide). Not for ranked
    single-category data -- use hbar_chart for that.
    """
    n = len(labels)
    value_labels = value_labels or [str(v) for v in values]
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(palette.background)
    ax.set_facecolor(palette.background)

    x_pos = list(range(n))
    bars = ax.bar(x_pos, values, width=0.5, color=palette.primary, zorder=3)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontproperties=fm.FontProperties(family=_REG_FONT),
                        fontsize=13, color=palette.text)
    ax.set_ylim(*ylim)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(bottom=False)

    span = ylim[1] - ylim[0]
    for b, v, lbl in zip(bars, values, value_labels):
        ax.text(b.get_x() + b.get_width() / 2, v + span * 0.025, lbl,
                 ha="center", va="bottom",
                 fontproperties=fm.FontProperties(family=_BOLD_FONT),
                 fontsize=15, color=palette.text)

    plt.subplots_adjust(left=0.04, right=0.98, top=0.88, bottom=0.14)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fig.savefig(out_path, facecolor=palette.background)
    plt.close(fig)
    return out_path
