#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
GROUP = ['mermaid','plantuml-colorset-renderer','echarts-animated-svg','slidev-echarts','slidev-animejs','slidev-quality-audit']
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
