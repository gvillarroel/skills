#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Qualify a native concept option in Chromium at delivery and resize states."""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


SNAPSHOT = """() => {
  const svg=document.querySelector('#chart svg'),chart=window.chart;
  const root=svg.getScreenCTM().inverse();
  const quad=e=>{const b=e.getBBox(),m=root.multiply(e.getScreenCTM());return [[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>[m.a*x+m.c*y+m.e,m.b*x+m.d*y+m.f])};
  const box=e=>{const b=e.getBoundingClientRect(),s=svg.getBoundingClientRect();return {x:b.x-s.x,y:b.y-s.y,width:b.width,height:b.height}};
  const native=element=>{const b=element.getBoundingRect().clone();b.applyTransform(element.getComputedTransform());return {x:b.x,y:b.y,width:b.width,height:b.height}};
  const nativeQuad=e=>{const b=e.getBoundingRect(),m=e.getComputedTransform()||[1,0,0,1,0,0];return [[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>[m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]])};
  const nodes=[],heads=[],routes=[],captions=[];
  chart.getModel().eachSeriesByType('graph',series=>{
    const graph=series.getGraph();
    graph.eachNode(node=>{const element=node.getGraphicEl();nodes.push({id:node.id,label:node.getModel().get('name'),bounds:native(element.getSymbolPath()),symbolSize:node.getModel().get('symbolSize')})});
    graph.eachEdge(edge=>{
      const element=edge.getGraphicEl(),head=element.childOfName('toSymbol'),line=element.childOfName('line'),text=element.getTextContent();
      const points=[];for(let t=0;t<=1;t+=.005)points.push(line.pointAt(t));
      routes.push({source:edge.node1.id,target:edge.node2.id,points});
      if(head)heads.push({source:edge.node1.id,target:edge.node2.id,bounds:native(head)});
      if(text&&!text.ignore)captions.push({source:edge.node1.id,target:edge.node2.id,label:String(text.style.text),bounds:native(text),nativeQuad:nativeQuad(text)});
    });
  });
  const labels=[...svg.querySelectorAll('text')].map(e=>({text:e.textContent,fontSize:parseFloat(getComputedStyle(e).fontSize),bounds:box(e),quad:quad(e)}));
  for(const caption of captions)caption.glyphQuads=caption.label.split('\\n').map(line=>labels.filter(label=>label.text===line).sort((a,b)=>Math.hypot(a.bounds.x+a.bounds.width/2-caption.bounds.x-caption.bounds.width/2,a.bounds.y+a.bounds.height/2-caption.bounds.y-caption.bounds.height/2)-Math.hypot(b.bounds.x+b.bounds.width/2-caption.bounds.x-caption.bounds.width/2,b.bounds.y+b.bounds.height/2-caption.bounds.y-caption.bounds.height/2))[0]?.quad).filter(Boolean);
  const shafts=[...svg.querySelectorAll('path')].filter(e=>getComputedStyle(e).fill==='none'&&Number.parseFloat(getComputedStyle(e).strokeWidth)>0).map(e=>{
    const m=root.multiply(e.getScreenCTM()),length=e.getTotalLength(),points=[];
    for(let i=0;i<=240;i++){const p=e.getPointAtLength(length*i/240);points.push([m.a*p.x+m.c*p.y+m.e,m.b*p.x+m.d*p.y+m.f]);}
    return {points,width:Number.parseFloat(getComputedStyle(e).strokeWidth)};
  });
  return {width:chart.getWidth(),height:chart.getHeight(),nodes,heads,routes,captions,labels,shafts};
}"""


def overlaps(a: dict, b: dict) -> bool:
    return a['x'] < b['x'] + b['width'] and a['x'] + a['width'] > b['x'] and a['y'] < b['y'] + b['height'] and a['y'] + a['height'] > b['y']


def segment_quad_distance(a: list, b: list, quad: list) -> float:
    """Independent segment/polygon distance, including full stroke envelopes."""
    def cross(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def inside(point):
        signs = [cross(quad[i], quad[(i + 1) % 4], point) for i in range(4)]
        return min(signs) >= -1e-8 or max(signs) <= 1e-8

    def point_distance(point, start, end):
        dx, dy = end[0] - start[0], end[1] - start[1]
        denominator = dx * dx + dy * dy
        t = max(0, min(1, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / denominator)) if denominator else 0
        return ((point[0] - start[0] - t * dx) ** 2 + (point[1] - start[1] - t * dy) ** 2) ** .5

    if inside(a) or inside(b):
        return 0.0
    minimum = float('inf')
    for i, start in enumerate(quad):
        end = quad[(i + 1) % 4]
        if cross(a, b, start) * cross(a, b, end) <= 0 and cross(start, end, a) * cross(start, end, b) <= 0:
            if max(min(a[0], b[0]), min(start[0], end[0])) <= min(max(a[0], b[0]), max(start[0], end[0])) + 1e-8 and max(min(a[1], b[1]), min(start[1], end[1])) <= min(max(a[1], b[1]), max(start[1], end[1])) + 1e-8:
                return 0.0
        minimum = min(minimum, point_distance(a, start, end), point_distance(b, start, end), point_distance(start, a, b), point_distance(end, a, b))
    return minimum


def qualify(option: dict, width: int, height: int, preview: Path) -> dict:
    workspace = Path.cwd().resolve()
    bundle = Path(__file__).resolve().parents[1]
    package = workspace / 'node_modules/echarts/package.json'
    if not package.is_file() or json.loads(package.read_text(encoding='utf-8')).get('version') != '6.1.0':
        raise ValueError('Run render_concept_graph.py first to install task-owned ECharts 6.1.0.')
    if len(option.get('series', [])) != 1 or option['series'][0].get('type') != 'graph' or option['series'][0].get('layout') != 'none':
        raise ValueError('Qualify one fixed native graph option from render_concept_graph.py.')
    modules = []
    for filename in ['echarts-colorsets.mjs', 'concept-graph-labels.mjs']:
        code = (bundle / 'assets/templates' / filename).read_bytes()
        modules.append('data:text/javascript;base64,' + base64.b64encode(code).decode('ascii'))
    result = {'ok': True, 'echartsVersion': '6.1.0', 'states': [], 'pageErrors': [], 'findings': [], 'preview': str(preview)}
    with sync_playwright() as runtime:
        options = {} if Path(runtime.chromium.executable_path).is_file() else {'channel': 'msedge'}
        browser = runtime.chromium.launch(**options)
        try:
            page = browser.new_page(viewport={'width': min(16384, width + 200), 'height': min(16384, height + 130)})
            page.on('pageerror', lambda error: result['pageErrors'].append(str(error)))
            page.set_content('<!doctype html><style>body{margin:0;background:white}</style><div id="chart"></div>')
            page.add_script_tag(path=str(workspace / 'node_modules/echarts/dist/echarts.js'))
            page.evaluate("""async ({option,width,height,modules})=>{
              if(echarts.version!=='6.1.0')throw new Error('Native qualification requires ECharts 6.1.0');
              const palette=await import(modules[0]),captions=await import(modules[1]);
              const host=document.getElementById('chart');host.style.width=width+'px';host.style.height=height+'px';
              window.chart=echarts.init(host,null,{renderer:'svg',width,height});
              window.original=option;
              await document.fonts.ready;
              for(const family of ['18px "Open Sans"','14px "Open Sans"'])await document.fonts.load(family);
              window.settle=async()=>{
                await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
                await document.fonts.ready;chart.getZr().refreshImmediately();
                const proof=palette.insetGraphArrowRoutes(chart,3);window.captionPlacement=captions.settleConceptGraphCaptions(chart);
                chart.getZr().refreshImmediately();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return proof;
              };
            }""", {'option': option, 'width': width, 'height': height, 'modules': modules})
            for name, w, h in [('delivery', width, height), ('resized', min(16384, width + 160), min(16384, height + 90)), ('restored', width, height), ('replay', width, height), ('reduced-motion', width, height)]:
                if name == 'reduced-motion':
                    page.emulate_media(reduced_motion='reduce')
                page.evaluate("""([w,h])=>{const host=document.getElementById('chart');host.style.width=w+'px';host.style.height=h+'px';chart.resize({width:w,height:h});chart.setOption(structuredClone(original),true)}""", [w, h])
                clearance = page.evaluate('settle()')
                repeat = page.evaluate('settle()')
                state = page.evaluate(SNAPSHOT)
                state.update({'state': name, 'clearance': clearance, 'repeat': repeat})
                state['captionPlacement'] = page.evaluate('captionPlacement')
                result['states'].append(state)
                if name == 'delivery':
                    page.locator('#chart svg').screenshot(path=str(preview))
            page.evaluate('chart.dispose()')
        finally:
            browser.close()
    original_nodes = option['series'][0]['data']
    for state in result['states']:
        def finding(issue, detail=None):
            result['findings'].append({'state': state['state'], 'issue': issue, 'detail': detail})
        if len(state['nodes']) != len(original_nodes) or len(state['heads']) != len(option['series'][0].get('links', [])):
            finding('Missing native nodes or complete heads')
        if state['repeat']['adjustedEdges']:
            finding('Repeated native inset is unstable')
        for record in [*state['nodes'], *state['heads'], *state['labels'], *state['captions']]:
            b = record['bounds']
            if b['x'] < -.25 or b['y'] < -.25 or b['x'] + b['width'] > state['width'] + .25 or b['y'] + b['height'] > state['height'] + .25:
                finding('Native envelope outside canvas', record)
        for node in state['nodes']:
            expected = next(item for item in original_nodes if item['id'] == node['id'])
            if any(abs(node['bounds'][axis] - expected['symbolSize'][index]) > .1 for index, axis in enumerate(['width', 'height'])):
                finding('Native symbol dimensions changed', node)
            for line in expected['name'].splitlines():
                candidates = [label for label in state['labels'] if label['text'] == line]
                b = node['bounds']
                if not any(label['fontSize'] >= 16 and label['bounds']['x'] >= b['x'] and label['bounds']['y'] >= b['y'] and label['bounds']['x'] + label['bounds']['width'] <= b['x'] + b['width'] and label['bounds']['y'] + label['bounds']['height'] <= b['y'] + b['height'] for label in candidates):
                    finding('Complete readable label does not fit its native symbol', line)
        for head in state['heads']:
            b = head['bounds']
            head['minimumBodyGap'] = min(((max(node['bounds']['x'] - b['x'] - b['width'], b['x'] - node['bounds']['x'] - node['bounds']['width'], 0) ** 2 + max(node['bounds']['y'] - b['y'] - b['height'], b['y'] - node['bounds']['y'] - node['bounds']['height'], 0) ** 2) ** .5 for node in state['nodes']), default=None)
            if head['minimumBodyGap'] is None or head['minimumBodyGap'] < 2.4:
                finding('Complete head overlaps a native body', head)
        for route in state['routes']:
            unrelated = [node for node in state['nodes'] if node['id'] not in [route['source'], route['target']]]
            if any(overlaps({'x': x, 'y': y, 'width': .01, 'height': .01}, node['bounds']) for x, y in route['points'] for node in unrelated):
                finding('Route crosses an unrelated node', {'source': route['source'], 'target': route['target']})
            del route['points']
        for caption in state['captions']:
            if any(overlaps(caption['bounds'], node['bounds']) for node in state['nodes']):
                finding('Caption overlaps a node', caption)
            if any(overlaps(caption['bounds'], head['bounds']) for head in state['heads']):
                finding('Caption overlaps a complete head', caption)
            quads = [caption['nativeQuad'], *caption['glyphQuads']]
            for quad in caption['glyphQuads']:
                glyph_box = {'x': min(p[0] for p in quad), 'y': min(p[1] for p in quad), 'width': max(p[0] for p in quad) - min(p[0] for p in quad), 'height': max(p[1] for p in quad) - min(p[1] for p in quad)}
                if any(overlaps(glyph_box, item['bounds']) for item in [*state['nodes'], *state['heads']]):
                    finding('Actual caption glyph envelope overlaps a body or complete head', caption)
            caption['minimumShaftPaintGap'] = min((segment_quad_distance(a, b, quad) - shaft['width'] / 2 for quad in quads for shaft in state['shafts'] for a, b in zip(shaft['points'], shaft['points'][1:])), default=None)
            if caption['minimumShaftPaintGap'] is None or caption['minimumShaftPaintGap'] < .75:
                finding('Caption glyph or backing envelope meets a shaft', caption)
            if not caption['glyphQuads']:
                finding('Native caption glyph envelope is missing', caption)
        for edge in option['series'][0].get('links', []):
            if edge.get('label', {}).get('show') and not any(label['text'] == edge.get('value') and label['fontSize'] >= 14 for label in state['labels']):
                finding('Complete readable relationship caption is missing', edge.get('value'))
        for i, label in enumerate(state['labels']):
            if any(overlaps(label['bounds'], other['bounds']) for other in state['labels'][i + 1:]):
                finding('Native text envelopes overlap', label['text'])
        del state['shafts']
    result['ok'] = not result['pageErrors'] and not result['findings']
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('option', type=Path)
    parser.add_argument('--width', type=int, required=True)
    parser.add_argument('--height', type=int, required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--preview', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.width <= 16384 or not 1 <= args.height <= 16384:
        parser.error('Use positive dimensions at most 16384 pixels.')
    workspace = Path.cwd().resolve()
    bundle = Path(__file__).resolve().parents[1]
    for output in [args.review, args.preview]:
        if not output.resolve().is_relative_to(workspace) or output.resolve().is_relative_to(bundle):
            parser.error('Write native review and preview inside the task workspace, outside the skill bundle.')
        output.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = qualify(json.loads(args.option.read_text(encoding='utf-8')), args.width, args.height, args.preview)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    args.review.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'review': str(args.review), 'preview': str(args.preview), 'states': len(result['states']), 'pageErrors': result['pageErrors'], 'findings': result['findings']}))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
