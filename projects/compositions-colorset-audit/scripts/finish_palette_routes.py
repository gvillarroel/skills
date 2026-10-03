#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finish finite authored palette routes and compact, honest output guidance."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
for name in ['compose-synchronized-svg','diagram-composition','hierarchy-lens','usefulcharts-style','video','manim-svg-video']:
    bundle=ROOT/'skills'/name
    reference=bundle/'references/palette-policy.md'
    reference.write_text('''# Authored colorset contract

Use the exact tokens in [colorsets.json](../assets/palettes/colorsets.json) for every authored stage, mark, label, connector, control, annotation and export. Prefer colorset1 for red and neutral explanations. Use colorset2 for simultaneous categories or numeric color bands that need additional semantic separation, and record the category/encoding reason. Pick one active set; colorset1 tokens are a subset of colorset2.

Do not generate new hues or opaque RGB tints. Use allowed discrete tokens, geometry, direct labels, dash patterns and opacity for emphasis. Numeric hierarchy lenses use fixed palette bands with an explicit legend; selected states keep those bands and use neutral tokens for inactive cells. Rasterization, antialiasing, shadows and video compression can introduce intermediate display pixels; validate authored paints and exact canvas cells rather than claiming that every encoded MP4 pixel is an exact token.

Preserve producer-owned photographs, portraits, maps, screenshots, brand artwork and imported SVG or video when source fidelity is requested. Those pixels are source material, not authored palette compliance. Report imported source preservation separately from wrapper compliance. To claim that the entire result fits a colorset, obtain or author an explicitly restyled producer asset and validate it before composition; never silently recolor factual source imagery.

Check actual exported SVG paint, computed browser paint or canvas RGB values at initial, changed and highlighted states. Keep essential text at 4.5:1 contrast against its actual backing. A declaration in metadata or unused CSS does not establish compliance.
''',encoding='utf-8')
    path=bundle/'SKILL.md';text=path.read_text(encoding='utf-8')
    title_end=text.index('\n',text.index('# '))+1
    text=text[:title_end]+'\nRead [palette-policy.md](references/palette-policy.md) before authoring or composing visuals. Apply one exact colorset to authored content and report preserved source media separately.\n'+text[title_end:]
    path.write_text(text,encoding='utf-8')

path=ROOT/'skills/hierarchy-lens/assets/templates/pixels.html';text=path.read_text(encoding='utf-8')
text=text.replace('--muted:#b5b5b5','--muted:#696969').replace('--edge:#333e48','--edge:#cfcfcf').replace('color:#cfcfcf;text-transform','color:#9e1b32;text-transform').replace('background:#19202cf7','background:#ffffff')
path.write_text(text,encoding='utf-8')
path=ROOT/'skills/hierarchy-lens/assets/templates/decision-ui.js';text=path.read_text(encoding='utf-8').replace('color:#cfcfcf','color:#696969').replace('color:#e7e7e7','color:#333e48').replace('accent-color:#cfcfcf','accent-color:#9e1b32').replace('solid #cfcfcf','solid #9e1b32');path.write_text(text,encoding='utf-8')
path=ROOT/'skills/hierarchy-lens/assets/templates/explorer.html';text=path.read_text(encoding='utf-8').replace('transition:fill .18s,opacity .18s','transition:opacity .18s')
bands=['#fff4cc','#ffd332','#ff9633','#e77204','#e8002a','#9e1b32','#6d1222']
stops=','.join(f'{c} {i/len(bands)*100:.3f}% {((i+1)/len(bands))*100:.3f}%' for i,c in enumerate(bands))
text=text.replace('linear-gradient(to right,#e7e7e7,#004d66)',f'linear-gradient(to right,{stops})');path.write_text(text,encoding='utf-8')

palette=json.loads((ROOT/'skills/video/assets/palettes/colorsets.json').read_text())['colorsets']['colorset2']['allowed']
path=ROOT/'skills/video/assets/examples/ai-concept-videos/renderer.js';text=path.read_text(encoding='utf-8')
text='''// Quantize animated paint changes to the declared colorset2 token set.
const authoredColorset2 = '''+json.dumps(palette)+''';
globalThis.quantizeColorset2 = (a, b, t) => {
  const parse = hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
  const left = parse(a), right = parse(b), rgb = left.map((v, i) => v + (right[i] - v) * Math.max(0, Math.min(1, t)));
  return authoredColorset2.reduce((best, c) => {
    const distance = paint => parse(paint).reduce((sum, v, i) => sum + (v - rgb[i]) ** 2, 0);
    return distance(c) < distance(best) ? c : best;
  });
};
'''+text
text=text.replace('d3.interpolateRgb("#ffffff", token.color)(matrixReveal)','globalThis.quantizeColorset2("#ffffff", token.color, matrixReveal)').replace('d3.interpolateRgb(token.color, "#ffffff")(matrixReveal)','globalThis.quantizeColorset2(token.color, "#ffffff", matrixReveal)').replace('d3.interpolateRgb("#ffffff", candidates[selectedIndex].color)(travelP)','globalThis.quantizeColorset2("#ffffff", candidates[selectedIndex].color, travelP)').replace('d3.interpolateRgb(candidates[selectedIndex].color, "#ffffff")(travelP)','globalThis.quantizeColorset2(candidates[selectedIndex].color, "#ffffff", travelP)')
path.write_text(text,encoding='utf-8')
path=ROOT/'skills/video/assets/examples/ai-concept-videos/scenes/llm-mechanism.js';text=path.read_text(encoding='utf-8').replace('globalThis.d3.interpolateRgb("#ffffff", activeStep.selected.color)(travelP)','globalThis.quantizeColorset2("#ffffff", activeStep.selected.color, travelP)').replace('globalThis.d3.interpolateRgb(activeStep.selected.color, "#ffffff")(travelP)','globalThis.quantizeColorset2(activeStep.selected.color, "#ffffff", travelP)');path.write_text(text,encoding='utf-8')
print('Updated palette guidance, hierarchy chrome and animated video paint routes.')
