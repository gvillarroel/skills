#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build deterministic offline D3 charts, flows, networks, and logos from literal CLI contracts."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys
from colorset_adapter import adapt_artifact, category_style


COLORSET1 = {
    "background": "#f7f7f7", "surface": "#ffffff", "ink": "#333e48",
    "ink_dark": "#1c1c1c", "primary": "#9e1b32", "primary_dark": "#6d1222",
    "accent": "#e8002a", "accent_soft": "#e7e7e7", "muted": "#828282",
    "line": "#cfcfcf", "quiet": "#e7e7e7",
}
COLORSET2 = {
    **COLORSET1, "blue": "#007298", "blue_dark": "#004d66",
    "orange": "#e77204", "green": "#45842a", "purple": "#652f6c",
    "yellow": "#f1c319",
}
ROLE_ALIASES = {
    "red": "primary", "primary": "primary", "primary-dark": "primary_dark",
    "neutral": "muted", "muted": "muted", "blue": "blue", "orange": "orange",
    "green": "green", "purple": "purple", "yellow": "yellow",
}
ATTRIBUTE_RE = re.compile(r"data-[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def parse_pair(value: str) -> tuple[str, str]:
    key, separator, item = value.partition("=")
    if not separator or not key or not item:
        raise argparse.ArgumentTypeError(f"Expected NAME=VALUE, got {value!r}")
    return key, item


def parse_link(value: str) -> tuple[str, str]:
    source, separator, target = value.replace("→", "->").partition("->")
    if not separator or not source.strip() or not target.strip():
        raise argparse.ArgumentTypeError(f"Expected SOURCE->TARGET, got {value!r}")
    return source.strip(), target.strip()


def checked_attributes(values: list[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, value in values:
        lowered = name.casefold()
        if not ATTRIBUTE_RE.fullmatch(lowered):
            raise ValueError(f"Only lowercase data-* attributes are supported: {name}")
        if lowered in {"data-renderer", "data-colorset", "data-pattern-id"}:
            raise ValueError(f"Core attribute is managed by the builder: {lowered}")
        result[lowered] = value
    return result


def require_order_safe_title(title: str, ordered_terms: list[str]) -> None:
    """Prevent document metadata from introducing later data labels too early."""

    occurrences = sorted(
        (position, index)
        for index, term in enumerate(ordered_terms)
        if (position := title.find(term)) >= 0
    )
    if not occurrences:
        return
    observed = [index for _, index in occurrences]
    expected = list(range(max(observed) + 1))
    if observed != expected:
        raise ValueError(
            "Title breaks ordered-label first occurrence; use a generic title or "
            "include only a leading prefix in exact contract order"
        )


def palette_for(colorset: str) -> dict[str, str]:
    return dict(COLORSET1 if colorset == "colorset1" else COLORSET2)


def json_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def svg_attribute_text(args: argparse.Namespace, attributes: dict[str, str]) -> str:
    merged = {
        "id": args.svg_id, "viewBox": f"0 0 {args.width} {args.height}", "role": "img",
        "data-renderer": "d3", "data-colorset": args.colorset,
        "data-pattern-id": args.svg_pattern_id or args.pattern_id, **attributes,
    }
    return " ".join(f'{key}="{escape(value, quote=True)}"' for key, value in merged.items())


def css_for(palette: dict[str, str]) -> str:
    variables = ";".join(
        f"--{name.replace('_', '-')}:{value}" for name, value in sorted(palette.items())
    )
    return (
        f":root{{{variables}}}"
        "*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--background);"
        "color:var(--ink);font-family:Arial,Helvetica,sans-serif}"
        "body{display:grid;grid-template-columns:minmax(0,1fr);place-items:center;padding:12px}"
        ".diagram-viewport{min-width:0;max-width:100%;width:1000px;overflow-x:auto}"
        "svg[data-layout='flow-spine']{min-width:var(--diagram-min-width)}"
        "svg{display:block;width:min(100%,1000px);height:auto;background:var(--surface);"
        "border:1px solid var(--line)}text{fill:var(--ink);font-family:Arial,Helvetica,sans-serif}"
        ".contract-title{font-size:24px;font-weight:700}.flow-node-label{fill:var(--ink);font-size:16px}"
        ".is-focus{stroke:var(--accent);stroke-width:4}"
    )


def base_html(args: argparse.Namespace, description: str, attributes: dict[str, str], script: str) -> str:
    skill_root = Path(__file__).resolve().parents[1]
    runtime = (skill_root / "assets" / "vendor" / "d3.v7.9.0.min.js").read_text(encoding="utf-8")
    runtime = runtime.replace("</script", "<\\/script")
    palette = palette_for(args.colorset)
    attrs = svg_attribute_text(args, attributes)
    return adapt_artifact(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(args.title)}</title><style>{css_for(palette)}</style></head>
<body data-renderer="d3" data-colorset="{args.colorset}"><div class="diagram-viewport" role="region" aria-label="{escape(args.title, quote=True)}" tabindex="0" style="--diagram-min-width:{args.width}px">
<svg {attrs} aria-label="{escape(args.title, quote=True)}"><title>{escape(args.title)}</title><desc>{escape(description)}</desc></svg>
</div>
<script id="d3-runtime">/* D3 v7.9.0, BSD-3-Clause */\n{runtime}</script><script>{script}</script>
</body></html>
""", args.colorset)


def bar_script(args: argparse.Namespace, palette: dict[str, str]) -> str:
    items = []
    for label, display in args.item:
        try:
            numeric = float(display)
        except ValueError as error:
            raise ValueError(f"Bar value must be numeric: {label}={display}") from error
        items.append({"label": label, "value": numeric, "display": display})
    if not items:
        raise ValueError("Bar artifacts require at least one --item LABEL=VALUE")
    spec = {
        "svgId": args.svg_id, "items": items, "unit": args.unit,
        "markClass": args.mark_class, "width": args.width, "height": args.height,
        "palette": palette,
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),m={top:72,right:42,bottom:68,left:58};
const x=d3.scaleBand().domain(spec.items.map(d=>d.label)).range([m.left,spec.width-m.right]).padding(.28);
const y=d3.scaleLinear().domain([0,d3.max(spec.items,d=>d.value)]).nice().range([spec.height-m.bottom,m.top]);
svg.append("text").attr("class","contract-title").attr("x",m.left).attr("y",36).text(spec.unit);
const g=svg.append("g").selectAll("g.bar-item").data(spec.items).join("g").attr("class","bar-item");
const bars=g.append("rect").attr("class",spec.markClass).attr("tabindex",0).attr("x",d=>x(d.label))
.attr("y",spec.height-m.bottom).attr("width",x.bandwidth()).attr("height",0).attr("fill",spec.palette.primary);
g.append("text").attr("x",d=>x(d.label)+x.bandwidth()/2).attr("y",spec.height-m.bottom+28).attr("text-anchor","middle").text(d=>d.label);
g.append("text").attr("x",d=>x(d.label)+x.bandwidth()/2).attr("y",d=>y(d.value)-10).attr("text-anchor","middle").attr("font-weight",700).text(d=>d.display);
bars.on("focus",function(){d3.select(this).classed("is-focus",true)}).on("blur",function(){d3.select(this).classed("is-focus",false)});
bars.transition().duration(420).delay((d,i)=>i*55).attr("y",d=>y(d.value)).attr("height",d=>spec.height-m.bottom-y(d.value));})();
""".replace("__SPEC__", json_script(spec))


def numeric_items(args: argparse.Namespace, form: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for label, display in args.item:
        try:
            numeric = float(display)
        except ValueError as error:
            raise ValueError(f"{form} value must be numeric: {label}={display}") from error
        items.append({"label": label, "value": numeric, "display": display})
    if not items:
        raise ValueError(f"{form} artifacts require at least one --item LABEL=VALUE")
    return items


def lollipop_script(args: argparse.Namespace, palette: dict[str, str]) -> str:
    items = numeric_items(args, "Lollipop")
    spec = {
        "svgId": args.svg_id, "items": items, "unit": args.unit,
        "stemClass": args.stem_class, "dotClass": args.dot_class,
        "width": args.width, "height": args.height, "palette": palette,
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),m={top:88,right:76,bottom:52,left:132};
const x=d3.scaleLinear().domain([0,d3.max(spec.items,d=>d.value)]).nice().range([m.left,spec.width-m.right]);
const y=d3.scaleBand().domain(spec.items.map(d=>d.label)).range([m.top,spec.height-m.bottom]).padding(.34);
svg.append("text").attr("class","contract-title").attr("x",m.left).attr("y",38).text(spec.unit);
svg.append("text").attr("x",m.left).attr("y",64).attr("font-size",14).attr("fill",spec.palette.muted).text(`0 – ${d3.max(spec.items,d=>d.value)} ${spec.unit}`);
const rows=svg.append("g").selectAll("g.lollipop-item").data(spec.items).join("g").attr("class","lollipop-item");
rows.append("text").attr("x",m.left-14).attr("y",d=>y(d.label)+y.bandwidth()/2+5).attr("text-anchor","end").text(d=>d.label);
const stems=rows.append("line").attr("class",spec.stemClass).attr("x1",m.left).attr("x2",m.left)
.attr("y1",d=>y(d.label)+y.bandwidth()/2).attr("y2",d=>y(d.label)+y.bandwidth()/2)
.attr("stroke",spec.palette.primary).attr("stroke-width",5).attr("stroke-linecap","round");
const dots=rows.append("circle").attr("class",spec.dotClass).attr("tabindex",0).attr("role","img")
.attr("aria-label",d=>`${d.label}: ${d.display} ${spec.unit}`).attr("data-value",d=>d.display)
.attr("cx",m.left).attr("cy",d=>y(d.label)+y.bandwidth()/2).attr("r",9)
.attr("fill",spec.palette.primary).attr("stroke",spec.palette.surface).attr("stroke-width",3);
const values=rows.append("text").attr("class","value-label").attr("x",m.left+16)
.attr("y",d=>y(d.label)+y.bandwidth()/2+5).attr("font-weight",700).text(d=>d.display);
dots.on("focus",function(event,d){d3.select(this).classed("is-focus",true).attr("r",13);values.filter(v=>v===d).attr("font-size",18)})
.on("blur",function(event,d){d3.select(this).classed("is-focus",false).attr("r",9);values.filter(v=>v===d).attr("font-size",null)});
stems.transition().duration(420).delay((d,i)=>i*55).ease(d3.easeCubicOut).attr("x2",d=>x(d.value));
dots.transition().duration(420).delay((d,i)=>i*55).ease(d3.easeCubicOut).attr("cx",d=>x(d.value));
values.transition().duration(420).delay((d,i)=>i*55).ease(d3.easeCubicOut).attr("x",d=>x(d.value)+16);})();
""".replace("__SPEC__", json_script(spec))


def diagram_fit_script() -> str:
    return """
const bounds=content.node().getBBox(),padding=18;
const width=spec.autoWidth?Math.ceil(bounds.width+padding*2):spec.width;
const height=spec.autoHeight?Math.ceil(bounds.height+padding*2):spec.height;
if(width<bounds.width+padding*2||height<bounds.height+padding*2)throw new Error("Fixed diagram canvas cannot contain readable nodes, routes and arrows; enlarge the constrained dimension");
content.attr("transform",`translate(${(width-bounds.width)/2-bounds.x},${(height-bounds.height)/2-bounds.y})`);
svg.attr("viewBox",`0 0 ${width} ${height}`).attr("data-compact-width",width).attr("data-compact-height",height).style("width",`${width}px`).style("min-width",`${width}px`);
"""


def network_script(args: argparse.Namespace, palette: dict[str, str]) -> str:
    if not args.node or not args.link:
        raise ValueError("Network artifacts require --node and --link values")
    nodes = []
    for label, role in args.node:
        role_key = ROLE_ALIASES.get(role.casefold())
        if not role_key or role_key not in palette:
            raise ValueError(f"Role {role!r} is unavailable in {args.colorset}")
        nodes.append({"id": label, "color": palette[role_key]})
    node_ids = {node["id"] for node in nodes}
    links = []
    for source, target in args.link:
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"Link endpoint is not declared as a node: {source}->{target}")
        links.append({"source": source, "target": target})
    spec = {
        "svgId": args.svg_id, "nodes": nodes, "links": links,
        "nodeClass": args.node_class, "linkClass": args.link_class,
        "width": args.width, "height": args.height, "palette": palette,
        "autoWidth": getattr(args, "auto_width", False), "autoHeight": getattr(args, "auto_height", False),
        "textOnFill": json.loads((Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][args.colorset]["textOnFill"],
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),defs=svg.append("defs");
defs.append("marker").attr("id",`${spec.svgId}-arrow`).attr("viewBox","0 0 10 10").attr("refX",9).attr("refY",5)
.attr("markerUnits","userSpaceOnUse").attr("markerWidth",10).attr("markerHeight",10).attr("orient","auto").append("path").attr("d","M0,0 L10,5 L0,10 Z").attr("fill",spec.palette.ink);
const content=svg.append("g").attr("class","diagram-content");
const groups=content.append("g").selectAll("g").data(spec.nodes).join("g").attr("class",spec.nodeClass).attr("tabindex",0).attr("opacity",0);
groups.append("text").attr("text-anchor","middle").attr("dy",".35em").attr("font-size",16).style("fill",d=>spec.textOnFill[d.color]).attr("font-weight",700).text(d=>d.id)
.each(function(d){const box=this.getBBox();d.r=Math.max(24,Math.hypot(box.width/2+10,box.height/2+6))});
const n=spec.nodes.length,r=n===1?0:(d3.max(spec.nodes,d=>d.r)+16)/Math.sin(Math.PI/n);
spec.nodes.forEach((node,i)=>{const a=-Math.PI/2+i/n*Math.PI*2;node.x=Math.cos(a)*r;node.y=Math.sin(a)*r});
groups.attr("transform",d=>`translate(${d.x},${d.y})`);
groups.insert("circle","text").attr("r",d=>d.r).attr("fill",d=>d.color);
const byId=new Map(spec.nodes.map(node=>[node.id,node])),seen=new Map();
spec.links.forEach(d=>{const key=JSON.stringify([d.source,d.target]),repeat=seen.get(key)||0;seen.set(key,repeat+1);d.repeat=repeat;
const a=byId.get(d.source),b=byId.get(d.target);if(a===b){const rr=a.r+24+repeat*20,uy=Math.sqrt(1-.65*.65),norm=Math.hypot(a.x,a.y)||1,ox=n===1?0:a.x/norm,oy=n===1?-1:a.y/norm,tx=-oy,ty=ox;
d.path=`M${a.x+(a.r+4)*(ox*uy-tx*.65)},${a.y+(a.r+4)*(oy*uy-ty*.65)}C${a.x+ox*rr*2.2-tx*rr*1.7},${a.y+oy*rr*2.2-ty*rr*1.7} ${a.x+ox*rr*2.2+tx*rr*1.7},${a.y+oy*rr*2.2+ty*rr*1.7} ${a.x+(a.r+7)*(ox*uy+tx*.65)},${a.y+(a.r+7)*(oy*uy+ty*.65)}`;return}
const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy),reciprocal=spec.links.some(e=>e.source===d.target&&e.target===d.source),bend=(reciprocal?30:0)+repeat*22;
const mx=(a.x+b.x)/2-dy/len*bend,my=(a.y+b.y)/2+dx/len*bend;
const la=Math.hypot(mx-a.x,my-a.y),lb=Math.hypot(b.x-mx,b.y-my);
const x1=a.x+(mx-a.x)/la*(a.r+4),y1=a.y+(my-a.y)/la*(a.r+4),x2=b.x-(b.x-mx)/lb*(b.r+7),y2=b.y-(b.y-my)/lb*(b.r+7);
d.path=`M${x1},${y1}Q${mx},${my} ${x2},${y2}`});
const lines=content.insert("g",":first-child").selectAll("path").data(spec.links).join("path").attr("class",spec.linkClass).attr("data-source",d=>d.source).attr("data-target",d=>d.target)
.attr("d",d=>d.path).attr("fill","none").attr("stroke",spec.palette.ink).attr("stroke-width",2).attr("marker-end",`url(#${spec.svgId}-arrow)`).attr("opacity",0);
lines.each(function(d){const length=this.getTotalLength();for(let along=0;along<=length;along+=Math.min(4,length)){const point=this.getPointAtLength(along);for(const node of spec.nodes){if(node.id!==d.source&&node.id!==d.target&&Math.hypot(point.x-node.x,point.y-node.y)<node.r+3)throw new Error("Network route crosses an unrelated node; choose a different layout or split the graph")}}});
groups.on("focus",function(){d3.select(this).classed("is-focus",true)}).on("blur",function(){d3.select(this).classed("is-focus",false)});
__FIT__
lines.transition().duration(360).delay((d,i)=>i*45).attr("opacity",1);
groups.transition().duration(360).delay((d,i)=>120+i*55).attr("opacity",1);})();
""".replace("__SPEC__", json_script(spec)).replace("__FIT__", diagram_fit_script())


def flow_script(args: argparse.Namespace, palette: dict[str, str]) -> str:
    node_labels = list(args.flow_node)
    if not node_labels and args.node:
        node_labels = [label for label, _ in args.node]
    if len(node_labels) < 2 or not args.link:
        raise ValueError("Flow artifacts require at least two --flow-node values and one --link")
    if len(args.link_value) != len(args.link):
        raise ValueError("Flow artifacts require exactly one --link-value for every --link")
    if len(set(node_labels)) != len(node_labels):
        raise ValueError("Flow node labels must be unique")
    node_ids = set(node_labels)
    links = []
    for (source, target), display in zip(args.link, args.link_value, strict=True):
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"Link endpoint is not declared as a flow node: {source}->{target}")
        try:
            numeric = float(display)
        except ValueError as error:
            raise ValueError(f"Flow link value must be numeric: {source}->{target}={display}") from error
        links.append({"source": source, "target": target, "value": numeric, "display": display})
    paint_contract = json.loads((Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][args.colorset]
    node_styles = [category_style(index, paint_contract, palette["surface"]) for index in range(len(node_labels))]
    spec = {
        "svgId": args.svg_id, "nodes": [{"id": label, "color": style["fill"], **style}
            for label, style in zip(node_labels, node_styles, strict=True)], "links": links,
        "textOnFill": paint_contract["textOnFill"],
        "nodeClass": args.node_class, "linkClass": args.link_class,
        "width": args.width, "height": args.height, "palette": palette,
        "paddingX": getattr(args, "node_padding_x", 10), "paddingY": getattr(args, "node_padding_y", 6),
        "title": args.title,
        "autoWidth": getattr(args, "auto_width", False), "autoHeight": getattr(args, "auto_height", False),
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),defs=svg.append("defs"),m={left:92,right:92};
defs.append("marker").attr("id",`${spec.svgId}-arrow`).attr("viewBox","0 0 10 10").attr("refX",9).attr("refY",5)
.attr("markerUnits","userSpaceOnUse").attr("markerWidth",10).attr("markerHeight",10).attr("orient","auto").append("path").attr("d","M0,0 L10,5 L0,10 Z").attr("fill",spec.palette.ink);
const content=svg.append("g").attr("class","diagram-content"),cy=0;
const groups=content.append("g").selectAll("g.flow-node").data(spec.nodes).join("g").attr("class","flow-node").attr("data-outline-tier",d=>d.tier);
groups.append("text").attr("class","flow-node-label").style("fill",d=>spec.textOnFill[d.color]).attr("text-anchor","middle").attr("dy",".35em").attr("font-weight",700).text(d=>d.id)
.each(function(d){const box=this.getBBox();d.w=Math.max(32,box.width+2*spec.paddingX);d.h=Math.max(32,box.height+2*spec.paddingY)});
const valueLabels=content.append("g").selectAll("text.link-value").data(spec.links).join("text").attr("class","link-value").attr("text-anchor","middle").attr("font-weight",700).text(d=>d.display)
.each(function(d){d.labelWidth=this.getBBox().width});
spec.nodes.forEach((node,i)=>{node.index=i});const byId=new Map(spec.nodes.map(node=>[node.id,node])),seen=new Map(),portCounts=new Map(),portUses=new Map();
const portKey=(node,side)=>JSON.stringify([node.id,side]);
spec.links.forEach(d=>{const a=byId.get(d.source),b=byId.get(d.target),key=JSON.stringify([d.source,d.target]),repeat=seen.get(key)||0;seen.set(key,repeat+1);d.direct=b.index===a.index+1&&!repeat;d.side=b.index>=a.index?-1:1;
if(!d.direct)for(const node of [a,b]){const key=portKey(node,d.side);portCounts.set(key,(portCounts.get(key)||0)+1)}});
spec.nodes.forEach(node=>{const count=Math.max(portCounts.get(portKey(node,-1))||0,portCounts.get(portKey(node,1))||0);node.w=Math.max(node.w,(count+1)*14+16)});
const gap=Math.max(36,d3.max(spec.links,d=>d.labelWidth)+12),maxH=d3.max(spec.nodes,d=>d.h);let cursor=0;
spec.nodes.forEach(node=>{node.x=cursor+node.w/2;node.y=cy;cursor+=node.w+gap});groups.attr("transform",d=>`translate(${d.x},${d.y})`);
const port=(node,side)=>{const key=portKey(node,side),use=portUses.get(key)||0,count=portCounts.get(key);portUses.set(key,use+1);return node.x-node.w/2+8+(node.w-16)*(use+1)/(count+1)};
let upper=0,lower=0;
spec.links.forEach(d=>{const a=byId.get(d.source),b=byId.get(d.target);
if(d.direct){d.path=`M${a.x+a.w/2+3},${cy}H${b.x-b.w/2-5}`;d.labelX=(a.x+a.w/2+b.x-b.w/2)/2;d.labelY=cy-maxH/2-10;return}
const side=d.side,lane=side<0?upper++:lower++,laneY=side*(maxH/2+34+lane*32);
const startX=port(a,side),endX=port(b,side),startY=cy+side*(a.h/2+3),endY=cy+side*(b.h/2+5);
d.path=`M${startX},${startY}V${laneY}H${endX}V${endY}`;d.labelX=(startX+endX)/2;d.labelY=laneY-8});
content.append("text").attr("class","contract-title").attr("x",0).attr("y",-maxH/2-44-upper*32).text(spec.title);
const links=content.insert("g",":first-child").selectAll("path").data(spec.links).join("path").attr("class",spec.linkClass).attr("data-source",d=>d.source).attr("data-target",d=>d.target)
.attr("d",d=>d.path)
.attr("fill","none").attr("stroke",spec.palette.ink).attr("stroke-width",d=>Math.max(3,Math.min(9,3+d.value*.35)))
.attr("marker-end",`url(#${spec.svgId}-arrow)`).attr("opacity",.2);
valueLabels.attr("x",d=>d.labelX).attr("y",d=>d.labelY);
const rects=groups.insert("rect","text").attr("class",spec.nodeClass).attr("tabindex",0).attr("role","img").attr("aria-label",d=>d.id)
.attr("x",d=>-d.w/2).attr("y",d=>-d.h/2).attr("width",d=>d.w).attr("height",d=>d.h).attr("rx",6)
.attr("fill",d=>d.color).attr("stroke",d=>d.stroke).attr("stroke-width",d=>d.strokeWidth).attr("stroke-dasharray",d=>d.strokeDasharray).attr("opacity",.2);
rects.on("focus",function(){d3.select(this).classed("is-focus",true)}).on("blur",function(){d3.select(this).classed("is-focus",false)});
__FIT__
links.transition().duration(360).delay((d,i)=>i*45).ease(d3.easeCubicOut).attr("opacity",1);
rects.transition().duration(360).delay((d,i)=>80+i*55).ease(d3.easeCubicOut).attr("opacity",1);})();
""".replace("__SPEC__", json_script(spec)).replace("__FIT__", diagram_fit_script())


def logo_script(args: argparse.Namespace, palette: dict[str, str]) -> str:
    if not args.brand or not args.tagline:
        raise ValueError("Logo artifacts require --brand and --tagline")
    paint_contract = json.loads((Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][args.colorset]
    spec = {
        "svgId": args.svg_id, "brand": args.brand, "tagline": args.tagline,
        "width": args.width, "height": args.height, "colorset": args.colorset,
        "palette": palette, "mode": args.logo_mode, "wedgeCount": args.wedge_count,
        "markClass": args.logo_mark_class, "wedgeClass": args.wedge_class,
        "brandClass": args.brand_class, "taglineClass": args.tagline_class,
        "wedgeStyles": [category_style(index, paint_contract, palette["surface"]) for index in range(args.wedge_count)] if args.colorset == "colorset1" else None,
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),cx=spec.width*.28,cy=spec.height*.46;
const mark=svg.append("g").attr("class",spec.markClass);
if(spec.mode==="wedges"){
const colors=spec.colorset==="colorset2"?[spec.palette.accent,spec.palette.orange,spec.palette.green,spec.palette.purple,spec.palette.blue,spec.palette.yellow,spec.palette.primary]:spec.wedgeStyles.map(style=>style.fill);
const arcs=d3.pie().sort(null).value(1)(d3.range(spec.wedgeCount)),arc=d3.arc().innerRadius(24).outerRadius(Math.min(spec.width,spec.height)*.23).padAngle(.035);
mark.attr("transform",`translate(${cx},${cy})`).selectAll("path").data(arcs).join("path").attr("class",spec.wedgeClass)
.attr("d",arc).attr("fill",(d,i)=>colors[i%colors.length])
.attr("data-outline-tier",(d,i)=>spec.wedgeStyles?.[i].tier??null)
.attr("stroke",(d,i)=>spec.wedgeStyles?.[i].stroke??spec.palette.surface)
.attr("stroke-width",(d,i)=>spec.wedgeStyles?.[i].strokeWidth??2)
.attr("stroke-dasharray",(d,i)=>spec.wedgeStyles?.[i].strokeDasharray??null).attr("opacity",0).attr("transform","scale(.2)")
.transition().duration(460).delay((d,i)=>i*28).ease(d3.easeCubicOut).attr("opacity",1).attr("transform","scale(1)");
}else{
mark.append("circle").attr("class","orbit").attr("cx",cx).attr("cy",cy).attr("r",Math.min(spec.width,spec.height)*.22)
.attr("fill","none").attr("stroke",spec.palette.primary).attr("stroke-width",5);
mark.append("circle").attr("cx",cx).attr("cy",cy).attr("r",18).attr("fill",spec.palette.primary);
if(spec.colorset==="colorset2"){[spec.palette.blue,spec.palette.orange,spec.palette.green,spec.palette.purple].forEach((color,i)=>{
const a=-Math.PI/2+i*Math.PI/2,x=cx+Math.cos(a)*74,y=cy+Math.sin(a)*74;
mark.append("path").attr("class","orbit-link").attr("d",`M${cx},${cy}L${x},${y}`).attr("stroke",color).attr("stroke-width",3).attr("fill","none");
mark.append("circle").attr("class","orbit-node").attr("cx",x).attr("cy",y).attr("r",10).attr("fill",color);});}}
svg.append("text").attr("class",spec.brandClass).attr("x",spec.width*.48).attr("y",spec.height*.43).attr("font-size",36).attr("font-weight",700).text(spec.brand);
svg.append("text").attr("class",spec.taglineClass).attr("x",spec.width*.48).attr("y",spec.height*.55).attr("font-size",18).attr("fill",spec.palette.muted).text(spec.tagline);})();
""".replace("__SPEC__", json_script(spec))


def build(args: argparse.Namespace) -> tuple[str, dict[str, str]]:
    if args.width is None:
        args.auto_width = True
        args.width = 900
    if args.height is None:
        args.auto_height = True
        args.height = 180 if args.kind == "flow" else 520
    palette = palette_for(args.colorset)
    attributes = checked_attributes(args.attribute)
    if args.kind == "bar":
        attributes.setdefault("data-chart-kind", "bar")
        description = f"Items in order: {', '.join(label for label, _ in args.item)}. {args.description} Unit: {args.unit}."
        script = bar_script(args, palette)
    elif args.kind == "lollipop":
        attributes.setdefault("data-chart-kind", "lollipop")
        description = f"Items in order: {', '.join(label for label, _ in args.item)}. {args.description} Unit: {args.unit}."
        script = lollipop_script(args, palette)
    elif args.kind == "network":
        attributes.setdefault("data-layout", args.layout)
        description = f"Nodes in order: {', '.join(label for label, _ in args.node)}. {args.description}"
        script = network_script(args, palette)
    elif args.kind == "flow":
        attributes.setdefault("data-layout", "flow-spine")
        flow_nodes = args.flow_node or [label for label, _ in args.node]
        require_order_safe_title(args.title, flow_nodes)
        description = f"Nodes in order: {', '.join(flow_nodes)}. {args.description} Link values in order: {', '.join(args.link_value)}."
        script = flow_script(args, palette)
    else:
        attributes.setdefault("data-logo-pattern", args.pattern_id)
        description = f"{args.description} Brand: {args.brand}. Tagline: {args.tagline}. Logo mode: {args.logo_mode}."
        script = logo_script(args, palette)
    decision = {"route": args.route, "colorset": args.colorset, "patternId": args.pattern_id, "reason": args.reason}
    return base_html(args, description, attributes, script), decision


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Literal formats:
  --attribute DATA-NAME=VALUE        repeat for exact public data-* attributes
  --item LABEL=NUMBER                repeat in required bar/lollipop order
  --node LABEL=ROLE                  repeat in required node order
  --flow-node LABEL                  repeat in required flow-spine order
  --link 'SOURCE->TARGET'            repeat in required link order; quote in shells
  --link-value NUMBER                repeat once per flow link in the same order

Roles:
  colorset1: primary, primary-dark, red, neutral, muted
  colorset2 also: blue, orange, green, purple, yellow
  colorset2 wedge logos visibly include accent, warning/orange,
  success/green, and special/purple before supporting hues.

Minimal form-specific examples:
  bar:        --kind bar --item Alpha=12 --unit "escaped defects"
  lollipop:   --kind lollipop --item North=14 --unit incidents --stem-class stem --dot-class dot
  network:    --kind network --node Gateway=blue --node Queue=orange --link 'Gateway->Queue'
  flow:       --kind flow --flow-node Capture --flow-node Publish --link 'Capture->Publish' --link-value 9
  orbit logo: --kind logo --brand "Northstar Lab" --tagline "Signals made clear"
  wedge logo: --kind logo --logo-mode wedges --wedge-count 12 --brand "Prism Arc" --tagline "Many signals, one form"

For a recomposition whose decision/global variant ID differs from the SVG's
base pattern metadata, pass the global ID through --pattern-id and the base
pattern through --svg-pattern-id. Pass every other exact data-* contract with
repeated --attribute flags.

All forms also require --output, --decision-output, --title, --description,
--route, --colorset, --pattern-id, --svg-id, and --reason.
""",
    )
    parser.add_argument("--kind", choices=("bar", "lollipop", "network", "flow", "logo"), required=True)
    parser.add_argument("--output", type=Path, required=True, help="Exact HTML output path.")
    parser.add_argument("--decision-output", type=Path, required=True, help="Exact decision JSON output path.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), required=True)
    parser.add_argument("--pattern-id", required=True)
    parser.add_argument("--svg-pattern-id", help="Optional data-pattern-id when it differs from the decision/global pattern ID.")
    parser.add_argument("--svg-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--width", type=int, help="Fixed canvas width; omitted diagram dimensions fit measured content, other forms use 900.")
    parser.add_argument("--height", type=int, help="Fixed canvas height; omitted diagram dimensions fit measured content, other forms use 520.")
    parser.add_argument("--node-padding-y", type=int, default=6, help="Vertical flow-node padding in pixels.")
    parser.add_argument("--node-padding-x", type=int, default=10, help="Horizontal flow-node padding in pixels.")
    parser.add_argument("--attribute", action="append", type=parse_pair, default=[], metavar="DATA-NAME=VALUE")
    parser.add_argument("--item", action="append", type=parse_pair, default=[], metavar="LABEL=NUMBER")
    parser.add_argument("--unit", default="Value")
    parser.add_argument("--mark-class", default="data-mark")
    parser.add_argument("--stem-class", default="stem")
    parser.add_argument("--dot-class", default="dot")
    parser.add_argument("--node", action="append", type=parse_pair, default=[], metavar="LABEL=ROLE")
    parser.add_argument("--flow-node", action="append", default=[], metavar="LABEL")
    parser.add_argument("--link", action="append", type=parse_link, default=[], metavar="SOURCE->TARGET")
    parser.add_argument("--link-value", action="append", default=[], metavar="NUMBER")
    parser.add_argument("--node-class", default="node")
    parser.add_argument("--link-class", default="link")
    parser.add_argument("--layout", choices=("force", "pre-ticked-force"), default="pre-ticked-force")
    parser.add_argument("--brand")
    parser.add_argument("--tagline")
    parser.add_argument("--logo-mode", choices=("orbit", "wedges"), default="orbit")
    parser.add_argument("--wedge-count", type=int, default=12)
    parser.add_argument("--logo-mark-class", default="logo-mark")
    parser.add_argument("--wedge-class", default="wedge")
    parser.add_argument("--brand-class", default="brand-text")
    parser.add_argument("--tagline-class", default="tagline")
    parser.add_argument("--force", action="store_true")
    return parser


def parse_args() -> argparse.Namespace:
    args = make_parser().parse_args()
    args.auto_width = args.width is None
    args.auto_height = args.height is None
    if args.width is None:
        args.width = 900
    if args.height is None:
        args.height = 180 if args.kind == "flow" else 520
    return args


def main() -> int:
    args = parse_args()
    if args.width < 320 or args.height < (120 if args.kind == "flow" else 240):
        raise SystemExit("--width must be at least 320; --height at least 120 for flow or 240 for other forms")
    if min(args.node_padding_x, args.node_padding_y) < 0:
        raise SystemExit("Node padding cannot be negative")
    if args.output.resolve() == args.decision_output.resolve():
        raise SystemExit("--output and --decision-output must differ")
    for path in (args.output, args.decision_output):
        if path.exists() and not args.force:
            raise SystemExit(f"Refusing existing output without --force: {path}")
    try:
        html, decision = build(args)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.decision_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8", newline="\n")
    args.decision_output.write_text(
        json.dumps(decision, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"output": str(args.output), "decision": str(args.decision_output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
