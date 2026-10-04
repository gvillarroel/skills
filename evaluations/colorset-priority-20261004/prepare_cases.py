#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Materialize compact isolated contract prompts without dispatching Pi."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
PROMPTS = HERE / "prompts"
EXCEPTIONS = {skill: "openai-codex/gpt-5.6-luna" for skill in (
    "d3", "mermaid", "plantuml-colorset-renderer", "threejs-animated-3d",
    "procedural-svg-animation", "compose-synchronized-svg",
    "echarts-animated-svg", "slidev-echarts", "vectorize-art-patterns",
)}
NATURALISTIC_OUTPUTS = {
    "d3": ["priority.html", "priority.svg", "allocation.json"],
    "mermaid": ["source/priority.mmd", "styled/priority.mmd", "priority.svg"],
    "plantuml-colorset-renderer": ["source/priority.puml", "source/layers.puml", "renders/svg/priority.svg", "renders/png/priority.png", "renders/svg/layers.svg", "renders/png/layers.png", "render-report.json"],
}


def python_contract(skill, module, expression):
    return f'''python - <<'PY'
import json, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, "skills/{skill}/scripts")
import {module} as helper
palettes = json.loads(Path("skills/{skill}/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
result = {{"colorset": "colorset1", "canvases": []}}
for canvas in ("#ffffff", "#000000"):
    count = len([paint for paint in palettes["colorset1"]["solidSequence"] if paint != canvas])
    styles = [{expression} for index in range(count + 1)]
    result["canvases"].append({{"canvas": canvas, "styles": styles}})
Path("contract.json").write_text(json.dumps(result, indent=2) + "\\n", encoding="utf-8")
PY'''


def d3_contract():
    return '''node --input-type=commonjs - <<'JS'
const fs = require('node:fs'), vm = require('node:vm');
const palettes = JSON.parse(fs.readFileSync('skills/d3/assets/palettes/colorsets.json','utf8')).colorsets;
const context = { window: { D3_SOLID_PALETTES: palettes }, document: { readyState: 'loading', addEventListener(){} }, MutationObserver: class { observe(){} }, requestAnimationFrame(){} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('skills/d3/assets/templates/solid-style.js','utf8'), context);
const canvases = ['#ffffff','#000000'].map(canvas => {
  const count = palettes.colorset1.solidSequence.filter(paint => paint !== canvas).length;
  return {canvas, styles:Array.from({length:count+1},(_,index)=>context.window.D3SolidStyle.categoryStyle(index,'colorset1',canvas))};
});
fs.writeFileSync('contract.json', JSON.stringify({colorset:'colorset1',canvases},null,2)+'\\n');
const vendor=fs.readFileSync('skills/d3/assets/vendor/d3.v7.9.0.min.js','utf8');
const code=`const canvases=${JSON.stringify(canvases)}; canvases.forEach(entry=>{const svg=d3.select('main').append('svg').attr('viewBox','0 0 504 390').attr('data-canvas',entry.canvas).style('background',entry.canvas);const rows=svg.selectAll('g').data(entry.styles).join('g').attr('data-category-index',(_,i)=>i).attr('transform',(_,i)=>'translate('+(12+i%4*123)+','+(12+Math.floor(i/4)*74)+')');rows.append('rect').attr('width',110).attr('height',58).attr('fill',d=>d.fill).attr('stroke',d=>d.stroke).attr('stroke-width',d=>d.strokeWidth).attr('stroke-dasharray',d=>d.strokeDasharray);rows.append('text').attr('x',55).attr('y',34).attr('text-anchor','middle').attr('font-size',14).attr('font-family','Arial').attr('fill',d=>d.text).text((_,i)=>'Group '+i);});`;
fs.writeFileSync('contract.html','<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Category canvases</title><style>body{margin:0;padding:12px;background:#ffffff}main{max-width:1040px;display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px}svg{width:100%;height:auto;display:block}</style><main></main><script>'+vendor+'</script><script>'+code+'</script></html>');
JS'''


def echarts_contract(skill):
    return f'''npm install --no-audit --no-fund echarts@6.1.0
node --input-type=module - <<'JS'
import fs from 'node:fs';
import * as echarts from 'echarts';
import {{ solidColors, solidCategoryStyle, prepareColorsetOption, insetGraphArrowRoutes, qualifyBoxplotMedians, normalizeSvgPaints }} from './skills/{skill}/assets/templates/echarts-colorsets.mjs';
const canvases = ['#ffffff','#000000'].map(canvas => {{
  const styles = solidColors('colorset1',canvas).map((_,index)=>solidCategoryStyle(index,'colorset1',canvas));
  styles.push(solidCategoryStyle(styles.length,'colorset1',canvas));
  const option={{animation:false,backgroundColor:canvas,series:[{{type:'graph',layout:'none',symbol:'rect',symbolSize:[72,32],label:{{show:true,position:'inside'}},edgeSymbol:['none','arrow'],data:styles.map((_,i)=>({{id:'g'+i,name:'Group '+i,x:60+(i%6)*95,y:50+Math.floor(i/6)*65}})),links:[{{source:'g0',target:'g1'}}]}}]}};
  prepareColorsetOption(option,'colorset1',option.series[0].data.map(node=>node.id));
  const chart=echarts.init(null,null,{{renderer:'svg',ssr:true,width:960,height:540}});
  chart.setOption(option);
  insetGraphArrowRoutes(chart,3);
  qualifyBoxplotMedians(chart,echarts,'colorset1');
  fs.writeFileSync(canvas==='#ffffff'?'priority.white.static.svg':'priority.dark.static.svg',normalizeSvgPaints(chart.renderToSVGString(),'colorset1'));
  chart.dispose();
  const boxplot={{animation:false,backgroundColor:canvas,xAxis:{{type:'category',data:['Batch A','Batch B']}},yAxis:{{type:'value'}},series:[{{type:'boxplot',data:[[1,2,3,4,5],[2,3,4,5,6]]}},{{type:'boxplot',data:[[2,3,4,5,6],[3,4,5,6,7]]}}]}};
  prepareColorsetOption(boxplot,'colorset1');
  const boxChart=echarts.init(null,null,{{renderer:'svg',ssr:true,width:960,height:540}});
  boxChart.setOption(boxplot);
  insetGraphArrowRoutes(boxChart,3);
  const medianQualification=qualifyBoxplotMedians(boxChart,echarts,'colorset1');
  fs.writeFileSync(canvas==='#ffffff'?'boxplot.white.static.svg':'boxplot.dark.static.svg',normalizeSvgPaints(boxChart.renderToSVGString(),'colorset1'));
  boxChart.dispose();
  return {{canvas,styles,preparedOption:option,boxplotPreparedOption:boxplot,medianQualification}};
}});
fs.writeFileSync('contract.json',JSON.stringify({{colorset:'colorset1',canvases}},null,2)+'\\n');
JS'''


def main():
    mermaid_render = '''
python - <<'PY'
import json
from pathlib import Path
record=json.loads(Path('contract.json').read_text(encoding='utf-8'))
styles=record['canvases'][0]['styles']
lines=['flowchart TB','accTitle: Category allocation','accDescr: Seventeen ordered category nodes with directed relationships.']
for index,style in enumerate(styles):
    lines.append(f'N{index}["Group {index}"]:::slot{index}')
    lines.append(f'classDef slot{index} fill:{style["fill"]},color:{style["text"]},stroke:{style["stroke"]},stroke-width:{style["strokeWidth"]}px;')
    if index: lines.append(f'N{index-1} --> N{index}')
Path('priority.mmd').write_text('\\n'.join(lines)+'\\n',encoding='utf-8')
PY
uv run --script skills/mermaid/scripts/style_mermaid_directory.py priority.mmd --colorset colorset1 --write --require-accessibility --report style-report.json
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py priority.mmd --static-output priority.svg --output priority.animated.svg --animation none --require-accessibility'''
    plantuml_render = '''
python - <<'PY'
from pathlib import Path
Path('source').mkdir()
Path('source/priority.puml').write_text('@startuml\\ntitle Delivery architecture\\ncomponent Intake\\ncomponent Review\\ndatabase Record\\ncloud Archive\\nIntake --> Review\\nReview --> Record\\nRecord --> Archive\\n@enduml\\n',encoding='utf-8')
PY
uv run --script skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py source --output renders --colorset colorset1 --engine cli --format svg --format png --report render-report.json'''
    contracts = {
        "d3": (d3_contract(), ["contract.json", "contract.html"]),
        "mermaid": (python_contract("mermaid", "palette_paints", "helper.solid_style(index, 'colorset1', canvas)") + mermaid_render, ["contract.json", "priority.mmd", "priority.svg", "priority.animated.svg", "style-report.json"]),
        "plantuml-colorset-renderer": (python_contract("plantuml-colorset-renderer", "palette_paints", "helper.solid_style(index, 'colorset1', canvas)") + plantuml_render, ["contract.json", "source/priority.puml", "renders/svg/priority.svg", "renders/png/priority.png", "render-report.json"]),
        "compose-synchronized-svg": (python_contract("compose-synchronized-svg", "palette_contract", "helper.category_style(index, 'colorset1', canvas)") + '''
python - <<'PY'
import json
from pathlib import Path
plan=json.loads(Path('skills/compose-synchronized-svg/assets/templates/composition-plan.json').read_text(encoding='utf-8'))
plan['theme']={'preset':'colorset1'}
Path('composition-plan.json').write_text(json.dumps(plan,indent=2)+'\\n',encoding='utf-8')
PY
uv run --script skills/compose-synchronized-svg/scripts/compose_synchronized_svg.py --spec composition-plan.json --output priority.svg --report priority-report.json''', ["contract.json", "composition-plan.json", "priority.svg", "priority-report.json"]),
        "procedural-svg-animation": (python_contract("procedural-svg-animation", "solid_style", "helper.category_style(index, palettes['colorset1'], canvas)") + "\nuv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py procedural-svg-state-sequencer --output priority.svg --palette colorset1 --seed 37 --duration-ms 4000 --report priority-report.json", ["contract.json", "priority.svg", "priority-report.json"]),
        "threejs-animated-3d": ("uv run --script skills/threejs-animated-3d/scripts/build_standalone_threejs.py priority.html --colorset colorset1 --token-count 16", ["priority.html"]),
        "vectorize-art-patterns": ("uv run --script skills/vectorize-art-patterns/scripts/vectorize_art.py skills/vectorize-art-patterns/assets/base-images/bailly-beauties-fancy.jpg bailly.svg --mode organic --colors 16 --colorset colorset1 --max-dimension 320 --source-manifest skills/vectorize-art-patterns/assets/base-images/manifest.json --source-id bailly-beauties-fancy --report bailly.json", ["bailly.svg", "bailly.json"]),
        "echarts-animated-svg": (echarts_contract("echarts-animated-svg"), ["contract.json", "priority.white.static.svg", "priority.dark.static.svg", "boxplot.white.static.svg", "boxplot.dark.static.svg"]),
        "slidev-echarts": (echarts_contract("slidev-echarts"), ["contract.json", "priority.white.static.svg", "priority.dark.static.svg", "boxplot.white.static.svg", "boxplot.dark.static.svg"]),
    }
    cases = {}
    for skill, (command, outputs) in contracts.items():
        path = PROMPTS / f"{skill}-contract.md"
        path.write_text(
            f"Run the exact compact standalone command below and inspect its outputs. "
            f"Treat `skills/{skill}/` as read-only. Use only the copied skill and normal "
            "local tools; do not inspect acceptance examples, sibling skills, parent "
            "run records, repository context, or outside source files. Keep generated "
            "files in this workspace. The contract records the public allocator's "
            "returned styles on two actual canvases, including its first overflow slot, "
            "or exercises the owning native builder. Do not alter the bundled helpers.\n\n"
            f"```bash\n{command}\n```\n", encoding="utf-8")
        case = {"model": EXCEPTIONS.get(skill, "openai-codex/gpt-5.3-codex-spark"), "thinking": "medium", "contract": {"prompt": path.relative_to(HERE).as_posix(), "outputs": outputs, "repetitions": 1}}
        if skill in NATURALISTIC_OUTPUTS:
            filename = "plantuml-naturalistic.md" if skill == "plantuml-colorset-renderer" else f"{skill}-naturalistic.md"
            case["naturalistic"] = {"prompt": f"prompts/{filename}", "outputs": NATURALISTIC_OUTPUTS[skill], "repetitions": 3}
        cases[skill] = case
    (HERE / "cases.json").write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(contracts)} standalone contracts and {len(NATURALISTIC_OUTPUTS)} naturalistic cases; no Pi run was dispatched.")


if __name__ == "__main__":
    main()
