#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an offline D3 treemap with stable borderless sibling tones."""

from __future__ import annotations

import argparse
from html import escape
import json
import math
from pathlib import Path
import re
import sys

from colorset_adapter import adapt_artifact

SKILL_ROOT = Path(__file__).resolve().parents[1]
D3_RUNTIME = SKILL_ROOT / "assets/vendor/d3.v7.9.0.min.js"
CONTRACT = SKILL_ROOT / "assets/palettes/colorsets.json"
FAMILIES = {
    "colorset1": [
        ["#9e1b32", ["#6d1222", "#9e1b32", "#e8002a"]],
        ["#696969", ["#4f4f4f", "#828282", "#b5b5b5"]],
        ["#4f4f4f", ["#363636", "#696969", "#9c9c9c"]],
    ],
    "colorset2": [
        ["#007298", ["#004d66", "#007298", "#00ace6"]],
        ["#e77204", ["#994a00", "#e77204", "#ff9633"]],
        ["#45842a", ["#294d19", "#45842a", "#36b300"]],
    ],
}


def literal(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{field} must be non-empty text without surrounding whitespace")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"{field} must not contain control characters")
    return value


def validate_data(data: object) -> dict:
    """Validate exactly root -> named branches -> positive weighted leaves."""
    def visit(node: object, depth: int) -> None:
        if not isinstance(node, dict):
            raise ValueError("Every hierarchy node must be an object")
        literal(node.get("name"), "Node name")
        if depth < 2:
            children = node.get("children")
            if "value" in node or not isinstance(children, list) or not children:
                raise ValueError("Root and branches require non-empty children and no value")
            names = []
            for child in children:
                visit(child, depth + 1)
                names.append(child["name"])
            if len(names) != len(set(names)):
                raise ValueError("Sibling names must be unique")
        else:
            value = node.get("value")
            if "children" in node or isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("Leaves require a numeric value and no children")
            if not math.isfinite(value) or not 0 < value <= 2**53 - 1:
                raise ValueError("Leaf values must be finite, positive and within JavaScript's safe numeric range")
    visit(data, 0)
    total = sum(leaf["value"] for branch in data["children"] for leaf in branch["children"])
    if not math.isfinite(total) or total > 2**53 - 1:
        raise ValueError("The hierarchy total must be within JavaScript's safe numeric range")
    return data


def script_json(value: object) -> str:
    # Preserve literal names through HTML parsing and the paint-only adapter.
    encoded = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    for character, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("#", "\\u0023")):
        encoded = encoded.replace(character, escaped)
    return encoded


def build_document(data: dict, *, title: str = "Treemap", colorset: str = "colorset1",
                   width: int = 960, height: int = 620) -> str:
    data = validate_data(data)
    title = literal(title, "Title")
    if colorset not in FAMILIES:
        raise ValueError("Select colorset1 or colorset2")
    if width < 320 or height < 320 or width > 4096 or height > 4096:
        raise ValueError("Width and height must be between 320 and 4096 pixels")
    palette = json.loads(CONTRACT.read_text(encoding="utf-8"))["colorsets"][colorset]
    configuration = dict(data=data, title=title, colorset=colorset, width=width, height=height,
                         families=FAMILIES[colorset], textOnFill=palette["textOnFill"])
    safe_title = escape(title).replace("#", "&#35;")
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,"><title>__TITLE__</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f7f7;color:#000000;font-family:Arial,Helvetica,sans-serif}
main{max-width:__WIDTH__px;margin:auto;padding:12px}h1{font-size:20px;margin:0 0 8px;overflow-wrap:anywhere}
button{border:0;border-radius:4px;background:#9e1b32;color:#ffffff;padding:8px 12px;cursor:pointer;font:inherit}
button:focus-visible{outline:2px solid #000000;outline-offset:3px}.controls{margin-bottom:8px}
svg{display:block;width:100%;height:auto;background:#ffffff}svg text{font-family:Arial,Helvetica,sans-serif}
</style></head><body><main><h1>__TITLE__</h1><div class="controls"><button id="replay" type="button">Replay</button></div>
<div id="treemap-frame"><svg id="treemap" xmlns="http://www.w3.org/2000/svg" role="img"
aria-labelledby="treemap-title treemap-description" data-pattern-id="__PATTERN_ID__"
data-label-policy="direct-labels-with-tiny-cell-key"><title id="treemap-title">__TITLE__</title>
<desc id="treemap-description">Opaque stepped sibling tones; cell area encodes the supplied positive values.</desc></svg></div></main>
<script id="d3-runtime">__D3__</script><script>
const config=__CONFIG__;
const svg=d3.select('#treemap'), frame=document.querySelector('#treemap-frame');
const motion=matchMedia('(prefers-reduced-motion: reduce)');
let lastWidth=0;
function label(group, name, value, boxWidth, boxHeight, fill, className){
  const text=group.append('text').attr('class',className).attr('x',6).attr('fill',config.textOnFill[fill])
    .attr('stroke','none').attr('font-weight',700);
  const valueText=String(value), available=Math.max(0,boxWidth-12);
  for(let size=13;size>=9;size--){
    text.attr('font-size',size).text('');
    if(boxHeight<42){
      text.attr('y',size+5).text(`${name} ${valueText}`);const single=text.node().getBBox();
      if(single.width<=available && single.y+single.height<=boxHeight-4)return single.y+single.height+8;
      text.text('').attr('y',null);
    }
    const lines=[];let line='';
    for(const part of name.match(/\S+\s*|\s+/g)||[name]){
      text.text(line+part);
      if(text.node().getComputedTextLength()>available && line){lines.push(line);line=part;}
      else line+=part;
      text.text(line);
      while(size===9 && text.node().getComputedTextLength()>available && Array.from(line).length>1){
        const characters=Array.from(line);let cut=1;
        text.text(characters.slice(0,cut+1).join(''));
        while(cut<characters.length-1 && text.node().getComputedTextLength()<=available){cut++;text.text(characters.slice(0,cut+1).join(''));}
        lines.push(characters.slice(0,cut).join(''));line=characters.slice(cut).join('');text.text(line);
      }
    }
    lines.push(line);lines.push(valueText);
    text.text('');lines.forEach((content,index)=>text.append('tspan').attr('x',6).attr('y',size+5+index*(size+2)).text(content));
    const bounds=text.node().getBBox();
    if(bounds.width<=available && bounds.y>=0 && bounds.y+bounds.height<=boxHeight-4)return bounds.y+bounds.height+8;
  }
  text.remove();return false;
}
function render(replay=false){
  const w=Math.max(48,Math.round(frame.clientWidth)), h=config.height;
  if(!replay && w===lastWidth)return;lastWidth=w;
  svg.selectAll('*').remove();svg.attr('viewBox',`0 0 ${w} ${h}`).attr('width',w).attr('height',h)
    .attr('data-colorset',config.colorset).attr('data-root-name',config.data.name);
  svg.append('title').attr('id','treemap-title').text(config.title);
  svg.append('desc').attr('id','treemap-description').text(`${config.data.name}. Cell area encodes value. Stepped opaque tones distinguish siblings; a complete key appears only when a tiny cell cannot fit its name and value.`);
  svg.append('rect').attr('width',w).attr('height',h).attr('fill','#ffffff').attr('stroke','none');
  const root=d3.hierarchy(config.data).sum(d=>d.value||0).sort((a,b)=>b.value-a.value);
  svg.append('text').attr('class','treemap-root-label').attr('x',12).attr('y',19).attr('font-size',12).attr('fill','#000000').text(`${config.data.name} (${root.value})`);
  d3.treemap().tile((node,x0,y0,x1,y1)=>(node.depth===1?d3.treemapSlice:d3.treemapDice)(node,x0,y0,x1,y1))
    .size([Math.max(0,w-24),h-50]).paddingOuter(4).paddingTop(32).paddingInner(4).round(false)(root);
  const family=new Map(root.children.map((branch,index)=>[branch,config.families[index%config.families.length]]));
  const branch=d=>d.depth===1?d:d.parent;
  const tone=d=>d.parent.children.length===1?1:Math.round(d.parent.children.indexOf(d)*2/(d.parent.children.length-1));
  const g=svg.append('g').attr('transform','translate(12,38)'), hidden=[];
  const nodes=g.selectAll('g').data(root.descendants().filter(d=>d.depth)).join('g')
    .attr('id',(_,index)=>`treemap-node-${index+1}`).attr('class',d=>`treemap-node ${d.children?'treemap-parent':'treemap-leaf'}`)
    .attr('data-name',d=>d.data.name).attr('data-value',d=>d.value).attr('data-branch',d=>branch(d).data.name)
    .attr('data-text-backing',d=>d.children?'.treemap-branch-header':'.treemap-leaf-cell')
    .attr('transform',d=>`translate(${d.x0},${d.y0})`);
  nodes.each(function(d){
    const node=d3.select(this), bw=Math.max(0,d.x1-d.x0), bh=Math.max(0,d.y1-d.y0), [base,ramp]=family.get(branch(d));
    const fill=d.children?'#ffffff':ramp[tone(d)];
    node.append('rect').attr('class',d.children?'treemap-branch-backing':'treemap-leaf-cell')
      .attr('width',bw).attr('height',bh).attr('fill',fill).attr('fill-opacity',1).attr('stroke','none')
      .attr('data-tone-index',d.children?null:tone(d));
    if(d.children){
      node.append('rect').attr('class','treemap-branch-header').attr('width',bw).attr('height',Math.min(28,bh)).attr('fill',base).attr('stroke','none');
      const text=node.append('text').attr('class','treemap-parent-label').attr('x',6).attr('y',18)
        .attr('font-size',12).attr('font-weight',700).attr('fill',config.textOnFill[base]).text(`${d.data.name} (${d.value})`);
      for(let size=11;text.node().getBBox().width>bw-12 && size>=9;size--)text.attr('font-size',size);
      if(text.node().getBBox().width>bw-12 || bh<24){text.remove();hidden.push(d);}
    }else if(bw<20 || bh<24 || !label(node,d.data.name,d.value,bw,bh,fill,'treemap-leaf-label'))hidden.push(d);
  });
  svg.attr('data-branch-count',root.children.length).attr('data-leaf-count',root.leaves().length).attr('data-total-value',root.value)
    .attr('data-key-count',hidden.length);
  if(hidden.length){
    const key=svg.append('g').attr('class','treemap-data-key').attr('data-text-backing','.treemap-key-backing');
    const entries=[root,...root.descendants().filter(d=>d.depth)];let keyHeight=8;
    const backing=key.append('rect').attr('class','treemap-key-backing').attr('y',h).attr('width',w).attr('fill','#ffffff').attr('stroke','none');
    entries.forEach(d=>{keyHeight+=label(key.append('g').attr('transform',`translate(8,${h+keyHeight})`),d.data.name,d.value,w-16,Infinity,'#ffffff','treemap-key-label');});
    keyHeight+=8;backing.attr('height',keyHeight);
    svg.attr('height',h+keyHeight).attr('viewBox',`0 0 ${w} ${h+keyHeight}`);
  }
  if(replay && !motion.matches)nodes.append('animate').attr('attributeName','opacity').attr('values','0;1').attr('dur','.45s').attr('fill','freeze');
  window.D3SolidStyle?.normalize(svg.node());
}
document.querySelector('#replay').addEventListener('click',()=>render(true));
new ResizeObserver(()=>render()).observe(frame);motion.addEventListener('change',()=>render(true));render();
</script></body></html>'''
    replacements = {"__TITLE__": safe_title, "__WIDTH__": str(width),
                    "__PATTERN_ID__": "d3-treemap-cs1" if colorset == "colorset1" else "d3-treemap-cs2",
                    "__CONFIG__": script_json(configuration), "__D3__": D3_RUNTIME.read_text(encoding="utf-8")}
    document = re.sub("|".join(replacements), lambda match: replacements[match.group()], template)
    return adapt_artifact(document, colorset)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a borderless offline D3 treemap. Three stable tones per family; larger sibling sets reuse tones with neutral gutters. Tiny cells use a complete visible SVG key.")
    parser.add_argument("--data", type=Path, required=True, help="JSON hierarchy: named root, named branches, positive numeric leaves")
    parser.add_argument("--output", type=Path, required=True, help="Exact HTML output outside the skill resource")
    parser.add_argument("--title", default="Treemap")
    parser.add_argument("--colorset", choices=tuple(FAMILIES), default="colorset1")
    parser.add_argument("--width", type=int, default=960, help="Maximum HTML width; layout recomputes at narrower widths")
    parser.add_argument("--height", type=int, default=620, help="Treemap height before any tiny-cell data key")
    parser.add_argument("--force", action="store_true", help="Replace an existing output outside the skill resource")
    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    try:
        output = args.output.resolve()
        if output.is_relative_to(SKILL_ROOT) or output.suffix.lower() != ".html" or output == args.data.resolve():
            raise ValueError("Output must be an HTML file outside the skill resource and distinct from the input")
        if output.exists() and not args.force:
            raise ValueError("Output exists; pass --force to replace it")
        data = json.loads(args.data.read_text(encoding="utf-8"))
        document = build_document(data, title=args.title, colorset=args.colorset, width=args.width, height=args.height)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document, encoding="utf-8", newline="\n")
    except (OSError, ValueError, OverflowError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1
    print(json.dumps(dict(output=str(output), colorset=args.colorset, patternId=f"d3-treemap-{'cs1' if args.colorset == 'colorset1' else 'cs2'}", leaves=sum(len(branch['children']) for branch in data['children']))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
