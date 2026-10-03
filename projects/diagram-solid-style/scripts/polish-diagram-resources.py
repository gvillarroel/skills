#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Update portable assets and authoring recipes without changing geometry."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
GROUP = ['mermaid','plantuml-colorset-renderer','echarts-animated-svg','slidev-echarts','slidev-animejs','slidev-quality-audit']
for skill in GROUP:
    path=ROOT/'skills'/skill/'SKILL.md'
    text=path.read_text(encoding='utf-8')
    sentence=" Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast."
    text=text.replace(sentence+sentence,sentence)
    path.write_text(text,encoding='utf-8')

for skill in ['echarts-animated-svg','slidev-echarts']:
    path=ROOT/'skills'/skill/'assets/templates/echarts-colorsets.mjs'
    text=path.read_text(encoding='utf-8')
    text=text.replace("  const visit = (node, inheritedFill, filled) => {", "  const categoryTypes = new Set(['pie','funnel','graph','tree','treemap','sunburst','sankey'])\n  const categoryIndices = new Map()\n  const visit = (node, inheritedFill, filled, categorical, insideDefault) => {")
    text=text.replace("    if (filled) {\n      node.itemStyle = {...node.itemStyle,borderWidth:0}", "    let category\n    if (categorical && node.name !== undefined) {\n      const key = String(node.id ?? node.name)\n      if (!categoryIndices.has(key)) categoryIndices.set(key,categoryIndices.size)\n      category = solidCategoryStyle(categoryIndices.get(key),colorset)\n      fill = category.color\n    }\n    if (filled) {\n      node.itemStyle = {...node.itemStyle,borderWidth:0,opacity:1,...(category ?? {})}\n      delete node.itemStyle.textColor\n      delete node.itemStyle.overflow")
    text=text.replace("(!node.label?.position || /^inside|middle$/.test(node.label.position))", "((!node.label?.position && insideDefault) || /^(?:inside|middle)/.test(node.label?.position ?? ''))")
    text=text.replace("visit(child, fill, filled)", "visit(child, fill, filled, categorical, insideDefault)")
    text=text.replace("shapeTypes.has(series.type)))", "shapeTypes.has(series.type),categoryTypes.has(series.type),['pie','funnel','treemap','sunburst'].includes(series.type)))")
    text=text.replace("  option.color ||= solidColors(colorset)", "  if (option.colorsetPresentation !== 'source') option.color = solidColors(colorset)\n  option.color ||= solidColors(colorset)")
    path.write_text(text,encoding='utf-8')

# Portable Anime.js surfaces: preserve drawable circuits, routes, orbit lines
# and other open line geometry. Recolor only bounded surfaces and inside text.
soft={'#cdf3ff':'#007298','#dbffcc':'#45842a','#fff4cc':'#f1c319','#ffe5cc':'#e77204','#ffccd5':'#9e1b32','#f9ccff':'#652f6c'}
pack=ROOT/'skills/slidev-animejs/assets/templates/slidev-svg-asset-pack'
for path in (pack/'assets/animated-svg').glob('*.svg'):
    text=path.read_text(encoding='utf-8')
    def shape(match):
        tag=match.group()
        fill=re.search(r'\bfill="(#[\da-fA-F]{6})"',tag)
        if not fill:return tag
        color=fill.group(1).lower()
        if color in soft:
            tag=tag.replace('fill="'+color+'"','fill="'+soft[color]+'"')
        if re.search(r'\b(?:rect|circle|ellipse|polygon)\b',tag) and 'stroke=' in tag:
            tag=re.sub(r'\s+stroke="[^"]*"',' stroke="none"',tag)
            tag=re.sub(r'\s+stroke-width="[^"]*"',' stroke-width="0"',tag)
        return tag
    text=re.sub(r'<(?:rect|circle|ellipse|polygon)\b[^>]*>',shape,text)
    # Paths used as bars remain visible on the newly dark dashboard cards.
    if path.name=='stagger-dashboard.svg':
        for value in ('#007298','#45842a'):
            text=text.replace('stroke="'+value+'" stroke-width="18"','stroke="#ffffff" stroke-width="18"')
        text=text.replace('stroke="#e77204" stroke-width="18"','stroke="#000000" stroke-width="18"')
    # Native backgrounds are inspected below with a browser, retaining labels.
    path.write_text(text,encoding='utf-8')

for skill in ['slidev-echarts','slidev-animejs']:
    path=ROOT/'skills'/skill/'assets/examples'/skill/'styles/index.css'
    text=path.read_text(encoding='utf-8')
    # UI outlines add no information; keyboard focus remains a functional cue.
    text=re.sub(r'border:\s*[\d.]+px solid #[\da-fA-F]{6};','border: 0;',text)
    for fill,solid in soft.items():
        # CSS fills, excluding actual drawing paint and measurement code.
        text=text.replace('background: '+fill+';', 'background: '+solid+';')
    # Explicit category chips use the higher black/white contrast.
    for fill,label in [('#45842a','#000000'),('#007298','#ffffff'),('#f1c319','#000000'),('#9e1b32','#ffffff'),('#652f6c','#ffffff')]:
        text=re.sub(r'(background:\s*'+fill+r';\s*color:)\s*#[\da-fA-F]{6}',r'\1 '+label,text)
    path.write_text(text,encoding='utf-8')

for skill in ['slidev-animejs','slidev-echarts']:
    p=ROOT/'skills'/skill/'references/visual-tokens.md'
    text=p.read_text(encoding='utf-8')
    text += '\n## Initial fill treatment\n\nUse saturated/base solid fills for category chips, blocks and animated marks, with zero decorative border width. Choose black or white inside text by the higher WCAG contrast on the final fill; animate text color categorically with its fill. Preserve drawable paths, connection lines, axes, measurement lines and keyboard focus indicators. Use border/dash/width variants only after all usable colors in the bundled solidSequence (excluding the actual canvas) have been assigned.\n'
    p.write_text(text,encoding='utf-8')
print('Updated filled chart defaults, portable Anime.js surfaces and Slidev chrome.')
