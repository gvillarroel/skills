#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Align five producer overflow pools with finite contrast-safe border variants."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SKILLS=['compose-synchronized-svg','diagram-composition','usefulcharts-style','video','manim-svg-video']
replacement='''def relative_luminance(fill):
    """Compute WCAG sRGB relative luminance for an opaque palette token."""
    channels = [int(fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722)))

def contrast_ratio(first, second):
    luminances = sorted((relative_luminance(first), relative_luminance(second)))
    return (luminances[1] + .05) / (luminances[0] + .05)

def category_style(index, colorset="colorset2", canvas="#f7f7f7"):
    """Exhaust solids before finite contrast-safe border/dash/width variants."""
    if not isinstance(index, int) or index < 0:
        raise ValueError("Category index must be a nonnegative integer")
    solids = solid_colors(colorset, canvas)
    fill = solids[index % len(solids)]
    cycle = index // len(solids)
    style = {"fill": fill, "text": text_on_fill(fill, colorset), "stroke": "none",
             "strokeWidth": 0, "dash": "", "overflow": False,
             "overflowExhausted": False}
    if cycle:
        borders = [paint for paint in COLORSETS[colorset]["allowed"]
                   if paint != fill and contrast_ratio(paint, fill) >= 3]
        # Border colors vary first, then three dash types, then widths 1..3.
        # The finite pool eventually repeats; labels/symbols/split views must
        # distinguish identities beyond it rather than growing border width.
        phase = cycle - 1
        style.update(stroke=borders[phase % len(borders)],
                     strokeWidth=1 + (phase // (3 * len(borders))) % 3,
                     dash=("", "6 3", "2 3")[(phase // len(borders)) % 3],
                     overflow=True, overflowExhausted=phase >= 9 * len(borders))
    return style
'''
for skill in SKILLS:
    path=ROOT/'skills'/skill/'scripts/palette_contract.py'
    text=path.read_text(encoding='utf-8');start=text.index('def category_style(')
    path.write_text(text[:start]+replacement,encoding='utf-8')
    ref=ROOT/'skills'/skill/'references/solid-surfaces.md'
    text=ref.read_text(encoding='utf-8')
    text=text.replace('Reuse fills with border color, then dash, then width variants; keep direct',
        'Reuse fills with border colors having at least 3:1 WCAG contrast against\n   the fill, then solid/dashed/dotted lines and widths 1–3; keep direct')
    text=text.replace('`overflow` and keeps stroke width zero throughout the first solid cycle.',
        '`overflow` and keeps stroke width zero throughout the first solid cycle.\n   Each fill has a finite pool of nine variants per qualifying border color.\n   `overflowExhausted` reports when that pool repeats; use direct labels,\n   symbols or split views beyond it. Never grow borders past width 3.')
    ref.write_text(text,encoding='utf-8')
print('Updated five finite contrast-safe overflow helpers and references.')
