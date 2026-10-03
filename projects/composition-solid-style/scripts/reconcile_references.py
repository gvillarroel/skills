#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Remove superseded outline-first recipes in owned conditional references."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]/'skills'
changes={
'usefulcharts-style/references/visual-grammar.md':[
('Keep the outer border thin and the chart field uninterrupted.', 'Keep the outer edge borderless and the chart field uninterrupted.'),
('Typical families include coral, sky blue, gold, sage, lilac, and orange. Keep text dark on light fills; derive white/dark text from contrast on custom dark colors.', 'Use exact colorset solids in their preferred sequence and no decorative border. Choose pure black or white by the actual fill contrast.')],
'usefulcharts-style/references/editorial-composition.md':[
('Put white outlined family labels near', 'Put solid borderless family labels near'),
('Use clear coral, sky blue, gold, sage, lilac, orange, and pink family colors, with a neutral precursor color when meaningful. Carry the same category through nodes and connectors. Black or near-black text usually fits these light fills; measure contrast.', 'Assign family colors from the chosen colorset solid sequence, including a neutral precursor when meaningful. Carry the same category through nodes and meaningful connectors. Use borderless fills and pure black or white text selected by maximum contrast on that fill.')],
'usefulcharts-style/references/genealogy-nameplates.md':[
('When the task supplies no category colors, use the light coral, sky blue, gold, sage, lilac, orange and pink palette in `SKILL.md`. Keep names predominantly black or near-black. A dark palette can pass contrast checks yet have a visibly different balance from the reference.', 'When the task supplies no category colors, use the selected colorset solid sequence from `SKILL.md`. Keep category nameplates borderless and choose pure black or white by the maximum WCAG contrast against the actual fill.')],
'usefulcharts-style/references/context-landmarks.md': [('a white outlined pill for a family', 'a solid borderless pill with contrast-selected black or white text for a family')],
'usefulcharts-style/references/data-contract.md': [('`emphasis: true` uses a stronger border.', '`emphasis: true` identifies content to emphasize through weight, placement or a separate solid marker; it does not introduce a default outline.')],
'diagram-composition/references/native-panels.md': [('outlines, bands, or swatches and auditable SVG bindings. Keep row/card labels dark;', 'solid borderless category surfaces or swatches and auditable SVG bindings.\nChoose pure black or white for card labels by their actual fill contrast;')],
'diagram-composition/references/connectors-and-surfaces.md': [('Use neutral surfaces or a\ntint/shade of the same concept, with a clearly visible exact-color accent.', 'Use the exact opaque category fill without a decorative outline. Choose pure\nblack or white for its inside labels by the higher actual fill contrast.')],
'compose-synchronized-svg/references/asset-selection-and-composition.md': [('Focus should add outline, halo, weight, or contrast rather than silently changing semantic color.', 'Focus should start with weight, scale or contrast while preserving semantic\ncolor. Use a narrow keyboard focus indicator when needed; decorative outline\nvariants begin only after full usable solid palette capacity is exhausted.')],
'manim-svg-video/references/visual-tokens.md': [('Use highlight colors for subtle fills, selection states, and replay-running states.', 'Use opaque borderless base/saturated category fills first and choose black or\n  white labels by their actual contrast. Use highlight colors late in the solid\n  sequence, and introduce border variants only after every usable solid is used.')]
}
for relative,replacements in changes.items():
    p=ROOT/relative;s=p.read_text(encoding='utf-8')
    for old,new in replacements:s=s.replace(old,new)
    p.write_text(s,encoding='utf-8',newline='\n')
p=ROOT/'usefulcharts-style/scripts/editorial_poster.py';s=p.read_text(encoding='utf-8')
s=s.replace("self.paper if style=='plain' else '#ffffff' if style=='pill' else paint", "self.paper if style=='plain' else paint")
s=s.replace("fill,paint if style=='pill' else 'none',2.5", "fill,'none',0")
s=s.replace("fill,paint if node.get('style')=='pill' else 'none',2.5", "fill,'none',0")
s=s.replace("(x-w/2,y-h/2,w,h),'#ffffff',paint,2.5,12", "(x-w/2,y-h/2,w,h),paint,'none',0,12")
s=s.replace("line,size,bold=a.get('kind')!='heading',css=css,background='#ffffff' if a.get('kind')=='pill' else self.paper", "line,size,text_color(paint) if a.get('kind')=='pill' else text_color(self.paper),bold=a.get('kind')!='heading',css=css,background=paint if a.get('kind')=='pill' else self.paper")
s=s.replace("paint,self.paper,1,4", "paint,'none',0,4").replace("paint,self.paper,1,5", "paint,'none',0,5")
p.write_text(s,encoding='utf-8',newline='\n')
print('Reconciled conditional recipe text and editorial pill paints.')
