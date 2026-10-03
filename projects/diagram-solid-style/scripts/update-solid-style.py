#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the diagram group's source changes; authored project helper, not runtime."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GROUP = ["mermaid", "plantuml-colorset-renderer", "echarts-animated-svg", "slidev-echarts", "slidev-animejs", "slidev-quality-audit"]

PY_HELPER = '''

def relative_luminance(fill: str) -> float:
    channels = [value / 255 for value in rgb(canonical(fill))]
    values = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return sum(value * weight for value, weight in zip(values, (0.2126, 0.7152, 0.0722)))

def readable_text(fill: str) -> str:
    """Choose the higher WCAG relative-luminance contrast, including bright colors."""
    luminance = relative_luminance(fill)
    return "#000000" if (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05) else "#ffffff"

def solid_colors(colorset: str = "colorset1", canvas: str = "#ffffff") -> list[str]:
    palette = COLORSETS[colorset]
    preferred = palette.get("solidSequence", palette["sequence"])
    soft = {"#ffccd5", "#cdf3ff", "#dbffcc", "#ffe5cc", "#fff4cc", "#f9ccff", "#e7e7e7", "#f7f7f7", "#ffffff", "#cfcfcf"}
    order = [c for c in preferred if c not in soft] + [c for c in palette["allowed"] if c not in soft] + [c for c in preferred if c in soft] + [c for c in palette["allowed"] if c in soft]
    return list(dict.fromkeys(c for c in order if c != canonical(canvas)))

def solid_style(index: int, colorset: str = "colorset1", canvas: str = "#ffffff") -> dict[str, object]:
    """Exhaust unique solid fills before explicit, deterministic outline overflow."""
    if index < 0:
        raise ValueError("Category index must be nonnegative")
    colors = solid_colors(colorset, canvas)
    cycle, slot = divmod(index, len(colors))
    fill = colors[slot]
    width = 0 if cycle == 0 else 1 + (cycle - 1) // 3
    border = "none" if cycle == 0 else colors[(slot + cycle) % len(colors)]
    return {"fill": fill, "text": readable_text(fill), "stroke": border, "strokeWidth": width, "dash": ("", "6 3", "2 2")[(cycle - 1) % 3] if cycle else "", "overflow": cycle > 0}
'''

for skill in GROUP:
    path = ROOT / "skills" / skill / "references/colorset-contract.md"
    text = path.read_text(encoding="utf-8")
    lead = """## Solid-first category style

Use one opaque solid fill and no decorative outline for initial category choices. Keep the exact finite palette. Allocate every distinct usable palette color before recycling a fill with an outline; exclude the actual canvas color, put saturated/base colors first, then dark/bright/neutral colors, and soft colors last. Keep each category's fill, text and any overflow outline stable across panels, series, legends and motion states. Declare overflow explicitly and cycle border color, dash and width only after that solid capacity is exhausted.

For text inside a filled shape, choose exactly `#000000` or `#ffffff` by the greater WCAG relative-luminance contrast against the actual fill. Do not assume every saturated color needs white text: orange, yellow, cyan and medium green often need black. Labels outside shapes use the canvas contrast. Use spacing and silhouette for grouping before borders. Preserve connectors, chart lines, class compartments, actor line art, meaningful data boundaries, source artwork and explicit user style. Containers are layout surfaces, not new categories.

"""
    if "## Solid-first category style" not in text:
        path.write_text(text.rstrip()+"\n\n"+lead, encoding="utf-8")
    path = ROOT / "skills" / skill / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    anchor = "Default to colorset1; declare colorset2 when its category distinctions are needed."
    text = text.replace(anchor, anchor + " Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast.")
    path.write_text(text, encoding="utf-8")

for skill in GROUP[:3]:
    path = ROOT / "skills" / skill / "scripts/palette_paints.py"
    text = path.read_text(encoding="utf-8")
    if "def solid_style(" not in text:
        path.write_text(text+PY_HELPER, encoding="utf-8")

p = ROOT / "skills/mermaid/scripts/style_mermaid_directory.py"
t = p.read_text(encoding="utf-8")
t = t.replace("from typing import Iterable", "from typing import Iterable\nfrom palette_paints import solid_colors, solid_style")
t = t.replace('candidates = (palette["surface"], palette["ink"], palette["gray900"], palette["black"])', 'candidates = ("#ffffff", "#000000")')
start = t.index('    roles = (', t.index('def series_colors('))
end = t.index('\n\n\ndef theme_variables', start)
t = t[:start]+'''    return solid_colors("colorset2" if extended else "colorset1")
'''+t[end:]
start = t.index('    fill_type_roles = (', t.index('def theme_variables('))
end = t.index('    variables = {', start)
t = t[:start]+'''    fill_type_colors = scale_colors[:8]
'''+t[end:]
start=t.index('    keys = set(CORE_THEME_KEYS)', t.index('def theme_variables'))
t=t[:start]+'''    # Native diagram containers retain their layout semantics; filled category
    # nodes use saturated solids and never require a contrasting rim.
    for fill_key, border_key, text_key, color in (
        ("primaryColor", "primaryBorderColor", "primaryTextColor", scale_colors[0]),
        ("secondaryColor", "secondaryBorderColor", "secondaryTextColor", scale_colors[1]),
        ("tertiaryColor", "tertiaryBorderColor", "tertiaryTextColor", scale_colors[2]),
        ("noteBkgColor", "noteBorderColor", "noteTextColor", scale_colors[3]),
        ("actorBkg", "actorBorder", "actorTextColor", scale_colors[0]),
        ("taskBkgColor", "taskBorderColor", "taskTextColor", scale_colors[1]),
        ("activeTaskBkgColor", "activeTaskBorderColor", None, scale_colors[2]),
        ("doneTaskBkgColor", "doneTaskBorderColor", None, scale_colors[3]),
        ("stateBkg", "compositeBorder", "stateLabelColor", scale_colors[1]),
    ):
        variables[fill_key] = color
        variables[border_key] = color
        if text_key:
            variables[text_key] = readable_text_color(color, p)
    variables.update(mainBkg=scale_colors[0], nodeBkg=scale_colors[0], nodeBorder=scale_colors[0], classText=readable_text_color(scale_colors[0], p), labelBackgroundColor=scale_colors[1], labelColor=readable_text_color(scale_colors[1], p), activationBkgColor=scale_colors[2], activationBorderColor=scale_colors[2])
    for role in ("Ui", "Processor", "ReadModel", "Command", "Event"):
        position = ("Ui", "Processor", "ReadModel", "Command", "Event").index(role)
        variables[f"em{role}Fill"] = scale_colors[position]
        variables[f"em{role}Stroke"] = scale_colors[position]
'''+t[start:]
start=t.index('    p = PALETTES[colorset]', t.index('def class_style'))
end=t.index('\n\ndef sankey_node_colors',start)
t=t[:start]+'''    style = solid_style(COLOR_CLASS_ORDER.index(class_name), colorset)
    return f"classDef {class_name} fill:{style['fill']},stroke:{style['stroke']},color:{style['text']},stroke-width:{style['strokeWidth']}px;"
'''+t[end:]
start=t.index('    p = PALETTES[colorset]',t.index('def sankey_node_colors'))
end=t.index('\n\ndef compact_layouts',start)
t=t[:start]+'''    palette = solid_colors(colorset)
    return {node: palette[index % len(palette)] for index, node in enumerate(nodes)}
'''+t[end:]
t=t.replace('".treemapLeaf { fill-opacity: 0.5 !important; stroke-width: 6px !important; }"','".treemapLeaf { fill-opacity: 1 !important; stroke-width: 0 !important; }"')
p.write_text(t,encoding="utf-8")

print("Updated six independent diagram contracts and three Python allocators.")

# Subsequent stages are deliberately separate from reusable bundle resources.
import json
import re

for skill in GROUP[:3]:
    p = ROOT / "skills" / skill / "scripts/palette_paints.py"
    t = p.read_text(encoding="utf-8")
    t = t.replace('    preferred = palette.get("solidSequence", palette["sequence"])', '    if "solidSequence" in palette:\n        return [color for color in palette["solidSequence"] if color != canonical(canvas)]\n    preferred = palette["sequence"]')
    p.write_text(t, encoding="utf-8")

p = ROOT / "skills/mermaid/scripts/style_mermaid_directory.py"
t = p.read_text(encoding="utf-8")
anchor = '    for config_key, defaults in compact_layouts(family, source).items():'
t = t.replace(anchor, '''    # Remove decorative node rims; meaningful edge/compartment paths stay native.
    config["themeCSS"] = ".node > rect, .node > circle, .node > ellipse, .node > polygon, .node > path, rect.actor, .note, .task, .task0, .task1, .task2, .task3 { stroke-width: 0 !important; }"
'''+anchor)
t = t.replace('        config["themeCSS"] = (\n            ".treemapLeaf', '        config["themeCSS"] += (\n            ".treemapLeaf')
p.write_text(t, encoding="utf-8")

palette = json.loads((ROOT / "skills/mermaid/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
js = '''
export function readableText(fill) {
  const channels = rgb(fill).map((c) => c / 255).map((c) => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
  const luminance = channels.reduce((sum, c, i) => sum + c * [.2126,.7152,.0722][i], 0)
  return (luminance + .05) / .05 >= 1.05 / (luminance + .05) ? '#000000' : '#ffffff'
}
export function solidColors(colorset = 'colorset1', canvas = '#ffffff') {
  return sequences[colorset].filter((color) => color !== canvas.toLowerCase())
}
export function solidCategoryStyle(index, colorset = 'colorset1', canvas = '#ffffff') {
  if (!Number.isInteger(index) || index < 0) throw new Error('Category index must be a nonnegative integer')
  const colors = solidColors(colorset, canvas), cycle = Math.floor(index/colors.length), slot = index%colors.length, fill = colors[slot]
  return {color:fill,borderColor:cycle ? colors[(slot+cycle)%colors.length] : 'none',borderWidth:cycle ? 1+Math.floor((cycle-1)/3) : 0,borderType:cycle ? ['solid','dashed','dotted'][(cycle-1)%3] : 'solid',textColor:readableText(fill),overflow:cycle>0}
}
function solidPresentation(option, colorset) {
  // Preserve explicit user source styling through this documented narrow opt-out.
  if (option.colorsetPresentation === 'source') { delete option.colorsetPresentation; return }
  delete option.colorsetPresentation
  const soft = {'#ffccd5':'#9e1b32','#cdf3ff':'#007298','#dbffcc':'#45842a','#ffe5cc':'#e77204','#fff4cc':'#f1c319','#f9ccff':'#652f6c'}
  const shapeTypes = new Set(['bar','pie','funnel','graph','tree','treemap','sunburst','sankey','scatter','effectScatter','pictorialBar','heatmap'])
  const seriesList = Array.isArray(option.series) ? option.series : option.series ? [option.series] : []
  const visit = (node, inheritedFill, filled) => {
    if (!node || typeof node !== 'object') return
    let fill = node.itemStyle?.color ?? inheritedFill
    if (typeof fill === 'string' && soft[fill.toLowerCase()]) fill = normalizePaint(soft[fill.toLowerCase()], colorset)
    if (filled) {
      node.itemStyle = {...node.itemStyle,borderWidth:0}
      if (typeof fill === 'string' && fill !== 'transparent') node.itemStyle.color = fill
      // ECharts inside positions and native filled-node labels must use actual fill contrast.
      if (typeof fill === 'string' && /^#[\\da-f]{6}$/i.test(fill) && node.label?.show !== false && (!node.label?.position || /^inside|middle$/.test(node.label.position))) node.label = {...node.label,color:readableText(fill),textBorderWidth:0,textShadowBlur:0}
      if (node.emphasis?.itemStyle) node.emphasis.itemStyle.borderWidth = 0
      if (node.select?.itemStyle) node.select.itemStyle.borderWidth = 0
    }
    for (const child of node.children ?? []) visit(child, fill, filled)
    for (const child of node.data ?? []) if (typeof child === 'object' && !Array.isArray(child)) visit(child, fill, filled)
    for (const child of node.levels ?? []) visit(child, fill, filled)
  }
  seriesList.forEach((series,index) => visit(series, option.color?.[index%option.color.length] ?? solidColors(colorset)[index%solidColors(colorset).length], shapeTypes.has(series.type)))
  if (option.tooltip) option.tooltip.borderWidth = 0
}
'''
for skill in ("echarts-animated-svg", "slidev-echarts"):
    p = ROOT / "skills" / skill / "assets/templates/echarts-colorsets.mjs"
    t = p.read_text(encoding="utf-8")
    seq = {name: value["solidSequence"] for name, value in palette.items()}
    t = re.sub(r'const sequences = .*', 'const sequences = '+json.dumps(seq), t, count=1)
    anchor = "export function nearestColor"
    t = t.replace(anchor, js+"\n"+anchor)
    t = t.replace("  walk(option)\n  option.color ||= sequences[colorset]", "  option.color ||= solidColors(colorset)\n  solidPresentation(option, colorset)\n  walk(option)")
    t = t.replace("borderColor:'#cfcfcf',textStyle", "borderWidth:0,borderColor:'#cfcfcf',textStyle")
    p.write_text(t, encoding="utf-8")
    p = ROOT / "skills" / skill / "references/colorset-contract.md"
    t = p.read_text(encoding="utf-8")
    t += "\nUse the independent `assets/templates/echarts-colorsets.mjs` helpers: `solidColors(colorset, canvas)` gives the complete solid capacity; `solidCategoryStyle(index, colorset, canvas)` returns stable fill, border, inside text and explicit overflow. Build a stable category ID-to-index map before rendering; use the same map for legends and data. `prepareColorsetOption` defaults filled marks to zero border width and resolves inside text contrast, while keeping chart/connector lines. For an explicit source-style preservation request set `colorsetPresentation: 'source'` on the editable option. Quantitative continuous scales, boxplot whiskers and candlestick wicks retain their measurement meaning.\n"
    p.write_text(t, encoding="utf-8")

# PlantUML theme defaults color object kinds with solid fills; line art is explicit.
shapes = ['Note','SequenceParticipant','Usecase','Class','Object','Activity','ActivityDiamond','Component','Interface','Node','Database','Cloud','Queue','State']
for mode in (1,2):
    name = f"colorset{mode}"
    colors = [c for c in palette[name]['solidSequence'] if c != '#ffffff']
    lines = [f"' plantuml-colorset-renderer: cs{mode} custom theme", 'skinparam backgroundColor #ffffff', 'skinparam shadowing false', 'skinparam DefaultFontName Arial', 'skinparam DefaultFontColor #000000', 'skinparam ArrowColor #696969', 'skinparam RoundCorner 6', 'skinparam TitleFontColor #000000']
    from importlib.util import spec_from_file_location, module_from_spec
    sp = spec_from_file_location('paints', ROOT/'skills/plantuml-colorset-renderer/scripts/palette_paints.py')
    helper = module_from_spec(sp); sp.loader.exec_module(helper)
    for i, shape in enumerate(shapes):
        color = colors[i]
        lines += [f'skinparam {shape}BackgroundColor {color}',f'skinparam {shape}BorderColor {color}', f'skinparam {shape}BorderThickness 0',f'skinparam {shape}FontColor {helper.readable_text(color)}']
    lines += ['skinparam ClassHeaderBackgroundColor '+colors[3], 'skinparam SequenceActorBackgroundColor #ffffff', 'skinparam SequenceActorBorderColor #333e48','skinparam SequenceActorFontColor #000000','skinparam SequenceLifeLineBorderColor #696969','skinparam SequenceArrowColor #696969','skinparam ActorBackgroundColor #ffffff','skinparam ActorBorderColor #333e48','skinparam ActorFontColor #000000','skinparam ActivityStartColor #333e48','skinparam ActivityEndColor #e8002a','skinparam StateStartColor #333e48','skinparam StateEndColor #e8002a','skinparam TimingBackgroundColor #ffffff','skinparam TimingFontColor #000000','skinparam TimingLineColor #696969','skinparam LegendBackgroundColor #ffffff','skinparam LegendBorderColor #ffffff','skinparam LegendBorderThickness 0','<style>', 'root {', '  Padding 6', '  FontColor #000000', '  LineColor #696969', '  BackgroundColor #ffffff', '}', 'arrow {', '  LineColor #696969', '  FontColor #000000', '}', 'actor {', '  LineColor #333e48', '  FontColor #000000', '  BackGroundColor #ffffff', '}']
    types = [('node, artifact, folder, frame, rectangle, card',9),('component, interface',7),('database, storage, collections',10),('cloud',11),('queue',12),('agent, participant',1),('class',3),('diamond',6),('note',0),('activity',5),('state',13)]
    for selector,i in types:
        lines += [selector+' {','  FontColor '+helper.readable_text(colors[i]), '  LineColor '+colors[i], '  LineThickness 0', '  BackGroundColor '+colors[i], '}']
    lines += ['chartDiagram {','  BackGroundColor #ffffff','  FontColor #000000','  axis {','    LineColor #696969','    FontColor #000000','  }','  grid {','    LineColor #e7e7e7','  }','  bar {','    LineColor '+colors[0],'    BackGroundColor '+colors[0],'    LineThickness 0','  }','  line {','    LineColor '+colors[1],'  }','  scatter {','    MarkerColor '+colors[2],'  }','}','</style>']
    (ROOT/'skills/plantuml-colorset-renderer/assets/themes'/f'cs{mode}.puml').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print("Updated native Mermaid/PlantUML and ECharts solid defaults.")
