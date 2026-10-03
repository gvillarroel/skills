#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Promote solid-first composition paint choices into standalone references."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]/'skills'
owners=['compose-synchronized-svg','diagram-composition','hierarchy-lens','usefulcharts-style','hyperframes-explainer','video','manim-svg-video']
reference='''# Solid surfaces and category capacity

Use this recipe for authored diagram nodes, labels, categorical marks, frames,
controls and video chrome in either colorset. Preserve an explicit requested
style, source photographs/video/artwork, meaningful connectors, axes, paths and
physical line geometry. A technical wire or an open vessel wall is meaningful
geometry; a dark outline around an otherwise filled card is decoration.

1. Assign a semantic identity once and reuse it across views. Read the selected
   `assets/palettes/colorsets.json` entry's `solidSequence`. Filter only the actual
   canvas color. Use every remaining distinct solid before repeating a fill.
   Begin with base and saturated colors, then dark, bright and neutral solids;
   soft colors are late alternatives. Do not restrict capacity to the six base
   hues, skip neutral colors, or begin with pale fills carrying dark outlines.
2. Paint each category surface with one opaque fill and `stroke="none"` / zero
   border width. Put gaps between adjoining objects where separation helps.
   Keep direct labels and semantic shapes. Use weight, position, scale or a
   separate marker for ordinary emphasis before adding an outline.
3. Pair each inside label with the actual solid behind the letters. Use the
   selected palette's `textOnFill[fill]`: it selects exact `#000000` or `#ffffff`
   by the higher WCAG sRGB relative-luminance contrast. Do not use a brightness
   guess, near-black, an unconditional white label or a color that merely passes
   on the outer canvas. Keep text outside a mark on the actual canvas pairing.
4. Only after exhausting all usable solids, begin an explicit overflow cycle.
   Reuse fills with border color, then dash, then width variants; keep direct
   labels and show this composite identity consistently in legends and views.
   A border alone cannot justify repeating a color while another usable solid
   remains. For Python producers, `scripts/palette_contract.py` where present
   exposes `solid_colors`, `text_on_fill` and `category_style`; the latter reports
   `overflow` and keeps stroke width zero throughout the first solid cycle.
5. Regenerate from the owning source. Inspect initial, changed and export states.
   Check first-cycle border width, uniqueness before overflow, and the actual
   text/fill pairs. Preserve interaction focus cues and semantic line marks.
   Alpha used for motion/focus is a compositing state, not a new category color;
   keep inside labels opaque or review their composited background separately.

Do not recolor an imported producer asset implicitly. Restyle it at its owning
producer when the request includes that source, and identify source-preserved
pixels separately from authored wrapper paint.
'''
for owner in owners:
    (ROOT/owner/'references/solid-surfaces.md').write_text(reference,encoding='utf-8',newline='\n')
    p=ROOT/owner/'SKILL.md';s=p.read_text(encoding='utf-8')
    sentence='Read [solid-surfaces.md](references/solid-surfaces.md) for solid-first category fills, black/white text on the actual fill, and palette exhaustion before border variants.\n'
    if sentence not in s:
        pos=s.index('\n',s.index('Read [palette-policy.md]'))+1
        s=s[:pos]+sentence+s[pos:]
    if owner=='usefulcharts-style':
        start=s.index('When no colors are supplied, use light category fills:')
        end=s.index('\n',start)
        s=s[:start]+'When no colors are supplied, assign categories from the selected colorset solid sequence, use borderless opaque fills, and select pure black or white text by the actual fill contrast. Preserve explicit colors supplied by the user or source.'+s[end:]
    if owner=='hyperframes-explainer':
        s=s.replace('Try direct labels, grouping, position, shape and stroke before additional hue.', 'Try direct labels, grouping, position and semantic shape before additional hue. Filled category surfaces start without decorative strokes; meaningful mechanism paths remain visible.')
    p.write_text(s,encoding='utf-8',newline='\n')

p=ROOT/'diagram-composition/references/shared-colors.md';s=p.read_text(encoding='utf-8')
s=s.replace('Prefer a few\nmeaningful accents and shared neutral surfaces to a different color per panel.', 'Prefer a few meaningful solid category surfaces. A repeated concept keeps its\nfill across panels; neutral layout surfaces carry no decorative outline.')
s=s.replace('bright colors belong on\nswatches, bands, or outlines.', 'choose pure black or white by the actual category fill contrast.')
s=s.replace('The builder looks up its color, preserves dark labels, and adds the SVG bindings.', 'The builder uses its solid fill, chooses black or white labels by contrast, and\nadds the SVG bindings.')
s=s.replace('use neutral surfaces or related tints/shades with readable\ntext.', 'use the exact solid category fill with readable black or white text.')
s=s.replace('the card outline or adjacent swatch carries', 'a separate solid label or adjacent swatch carries')
s=s.replace('fill="#ffffff"\n      stroke="#007298" stroke-width="2.4"', 'fill="#007298"\n      stroke="none" stroke-width="0"')
s=s.replace('data-color-channel="stroke"', 'data-color-channel="fill"')
p.write_text(s,encoding='utf-8',newline='\n')

p=ROOT/'compose-synchronized-svg/references/color-and-visual-quality.md';s=p.read_text(encoding='utf-8')
s=s.replace('The finite token sequence repeats when its contrast-safe colors are exhausted; use shapes, dash styles and direct labels to preserve identity.', 'The full `solidSequence` excludes only the actual canvas. Use every unique fill\nbefore repeating; only then add explicit border color/dash/width variants plus\ndirect labels to preserve identity. Default category nodes have no border.')
s=s.replace('Generated tint tokens are opaque, contrast-checked discrete palette tokens chosen near the requested mix. Their strength can decrease to preserve the supplied text colors.', 'Neutral layout tints remain contrast-checked palette tokens. Category surfaces\nuse their exact solid color; generated `--on-value-*` tokens choose pure black or\nwhite by maximum WCAG contrast against that fill.')
s=s.replace('`focus` and concept mark colors at 3:1.', '`focus` at 3:1. Solid category fills carry direct black/white labels; a thin\nmeaningful colored line still needs visible contrast against its local canvas.')
s=s.replace('The canonical `--concept-*` paint remains exact for marks and borders.', 'The canonical `--concept-*` paint remains exact for solid marks. Use\n`--on-value-*` on category surfaces and keep decorative borders absent.')
p.write_text(s,encoding='utf-8',newline='\n')

p=ROOT/'video/assets/examples/ai-concept-videos/styles.css';s=p.read_text(encoding='utf-8')
for value in ['1px solid var(--line-soft)','1px solid #e7e7e7','1px solid #cdf3ff','4px solid var(--brand-primary)']:
    s=s.replace('border: '+value,'border: 0').replace('border-left: '+value,'border-left: 0')
p.write_text(s,encoding='utf-8',newline='\n')
print('Promoted solid surface guidance in seven standalone bundles.')
