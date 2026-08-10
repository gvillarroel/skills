#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a deterministic offline D3 bar, network, or logo from literal CLI contracts."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys


COLORSET1 = {
    "background": "#f7f7f7", "surface": "#ffffff", "ink": "#333e48",
    "ink_dark": "#1c1c1c", "primary": "#9e1b32", "primary_dark": "#6d1222",
    "accent": "#e8002a", "accent_soft": "#ffccd5", "muted": "#828282",
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


def palette_for(colorset: str) -> dict[str, str]:
    return dict(COLORSET1 if colorset == "colorset1" else COLORSET2)


def json_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def svg_attribute_text(args: argparse.Namespace, attributes: dict[str, str]) -> str:
    merged = {
        "id": args.svg_id, "viewBox": f"0 0 {args.width} {args.height}", "role": "img",
        "data-renderer": "d3", "data-colorset": args.colorset,
        "data-pattern-id": args.pattern_id, **attributes,
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
        "body{display:grid;place-items:center;padding:16px}"
        "svg{display:block;width:min(100%,1000px);height:auto;background:var(--surface);"
        "border:1px solid var(--line)}text{fill:var(--ink);font-family:Arial,Helvetica,sans-serif}"
        ".contract-title{font-size:24px;font-weight:700}.is-focus{stroke:var(--accent);stroke-width:4}"
    )


def base_html(args: argparse.Namespace, description: str, attributes: dict[str, str], script: str) -> str:
    skill_root = Path(__file__).resolve().parents[1]
    runtime = (skill_root / "assets" / "vendor" / "d3.v7.9.0.min.js").read_text(encoding="utf-8")
    runtime = runtime.replace("</script", "<\\/script")
    palette = palette_for(args.colorset)
    attrs = svg_attribute_text(args, attributes)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(args.title)}</title><style>{css_for(palette)}</style></head>
<body data-renderer="d3" data-colorset="{args.colorset}">
<svg {attrs} aria-label="{escape(args.title, quote=True)}"><title>{escape(args.title)}</title><desc>{escape(description)}</desc></svg>
<script>/* D3 v7.9.0, BSD-3-Clause */\n{runtime}</script><script>{script}</script>
</body></html>
"""


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
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),defs=svg.append("defs");
defs.append("marker").attr("id",`${spec.svgId}-arrow`).attr("viewBox","0 0 10 10").attr("refX",9).attr("refY",5)
.attr("markerWidth",7).attr("markerHeight",7).attr("orient","auto").append("path").attr("d","M0,0 L10,5 L0,10 Z").attr("fill",spec.palette.ink);
const r=Math.min(spec.width,spec.height)*.34,cx=spec.width/2,cy=spec.height/2+12;
spec.nodes.forEach((n,i)=>{const a=-Math.PI/2+i/spec.nodes.length*Math.PI*2;n.x=cx+Math.cos(a)*r;n.y=cy+Math.sin(a)*r});
const byId=new Map(spec.nodes.map(n=>[n.id,n]));
const lines=svg.append("g").selectAll("line").data(spec.links).join("line").attr("class",spec.linkClass)
.attr("x1",d=>byId.get(d.source).x).attr("y1",d=>byId.get(d.source).y).attr("x2",d=>byId.get(d.target).x).attr("y2",d=>byId.get(d.target).y)
.attr("stroke",spec.palette.ink).attr("stroke-width",2).attr("marker-end",`url(#${spec.svgId}-arrow)`).attr("opacity",0);
const groups=svg.append("g").selectAll("g").data(spec.nodes).join("g").attr("class",spec.nodeClass).attr("tabindex",0)
.attr("transform",d=>`translate(${d.x},${d.y})`).attr("opacity",0);
groups.append("circle").attr("r",34).attr("fill",d=>d.color).attr("stroke",spec.palette.surface).attr("stroke-width",3);
groups.append("text").attr("text-anchor","middle").attr("dy",5).attr("fill",spec.palette.surface).attr("font-weight",700).text(d=>d.id);
groups.on("focus",function(){d3.select(this).classed("is-focus",true)}).on("blur",function(){d3.select(this).classed("is-focus",false)});
lines.transition().duration(360).delay((d,i)=>i*45).attr("opacity",1);
groups.transition().duration(360).delay((d,i)=>120+i*55).attr("opacity",1);})();
""".replace("__SPEC__", json_script(spec))


def logo_script(args: argparse.Namespace, palette: dict[str, str]) -> str:
    if not args.brand or not args.tagline:
        raise ValueError("Logo artifacts require --brand and --tagline")
    spec = {
        "svgId": args.svg_id, "brand": args.brand, "tagline": args.tagline,
        "width": args.width, "height": args.height, "colorset": args.colorset,
        "palette": palette,
    }
    return """
(()=>{const spec=__SPEC__,svg=d3.select(`#${CSS.escape(spec.svgId)}`),cx=spec.width*.28,cy=spec.height*.46;
const mark=svg.append("g").attr("class","logo-mark");
mark.append("circle").attr("class","orbit").attr("cx",cx).attr("cy",cy).attr("r",Math.min(spec.width,spec.height)*.22)
.attr("fill","none").attr("stroke",spec.palette.primary).attr("stroke-width",5);
mark.append("circle").attr("cx",cx).attr("cy",cy).attr("r",18).attr("fill",spec.palette.primary);
if(spec.colorset==="colorset2"){[spec.palette.blue,spec.palette.orange,spec.palette.green,spec.palette.purple].forEach((color,i)=>{
const a=-Math.PI/2+i*Math.PI/2,x=cx+Math.cos(a)*74,y=cy+Math.sin(a)*74;
mark.append("path").attr("class","orbit-link").attr("d",`M${cx},${cy}L${x},${y}`).attr("stroke",color).attr("stroke-width",3).attr("fill","none");
mark.append("circle").attr("class","orbit-node").attr("cx",x).attr("cy",y).attr("r",10).attr("fill",color);});}
svg.append("text").attr("class","brand-text").attr("x",spec.width*.48).attr("y",spec.height*.43).attr("font-size",36).attr("font-weight",700).text(spec.brand);
svg.append("text").attr("class","tagline").attr("x",spec.width*.48).attr("y",spec.height*.55).attr("font-size",18).attr("fill",spec.palette.muted).text(spec.tagline);})();
""".replace("__SPEC__", json_script(spec))


def build(args: argparse.Namespace) -> tuple[str, dict[str, str]]:
    palette = palette_for(args.colorset)
    attributes = checked_attributes(args.attribute)
    if args.kind == "bar":
        attributes.setdefault("data-chart-kind", "bar")
        description = f"{args.description} Items in order: {', '.join(label for label, _ in args.item)}. Unit: {args.unit}."
        script = bar_script(args, palette)
    elif args.kind == "network":
        attributes.setdefault("data-layout", args.layout)
        description = f"{args.description} Nodes in order: {', '.join(label for label, _ in args.node)}."
        script = network_script(args, palette)
    else:
        attributes.setdefault("data-logo-pattern", args.pattern_id)
        description = f"{args.description} Brand: {args.brand}. Tagline: {args.tagline}."
        script = logo_script(args, palette)
    decision = {"route": args.route, "colorset": args.colorset, "patternId": args.pattern_id, "reason": args.reason}
    return base_html(args, description, attributes, script), decision


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Literal formats:
  --attribute DATA-NAME=VALUE        repeat for exact public data-* attributes
  --item LABEL=NUMBER                repeat in required bar order
  --node LABEL=ROLE                  repeat in required node order
  --link 'SOURCE->TARGET'            repeat in required link order; quote in shells

Roles:
  colorset1: primary, primary-dark, red, neutral, muted
  colorset2 also: blue, orange, green, purple, yellow

Minimal form-specific examples:
  bar:     --kind bar --item Alpha=12 --unit "escaped defects"
  network: --kind network --node Gateway=blue --node Queue=orange --link 'Gateway->Queue'
  logo:    --kind logo --brand "Northstar Lab" --tagline "Signals made clear"

All forms also require --output, --decision-output, --title, --description,
--route, --colorset, --pattern-id, --svg-id, and --reason.
""",
    )
    parser.add_argument("--kind", choices=("bar", "network", "logo"), required=True)
    parser.add_argument("--output", type=Path, required=True, help="Exact HTML output path.")
    parser.add_argument("--decision-output", type=Path, required=True, help="Exact decision JSON output path.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), required=True)
    parser.add_argument("--pattern-id", required=True)
    parser.add_argument("--svg-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=520)
    parser.add_argument("--attribute", action="append", type=parse_pair, default=[], metavar="DATA-NAME=VALUE")
    parser.add_argument("--item", action="append", type=parse_pair, default=[], metavar="LABEL=NUMBER")
    parser.add_argument("--unit", default="Value")
    parser.add_argument("--mark-class", default="data-mark")
    parser.add_argument("--node", action="append", type=parse_pair, default=[], metavar="LABEL=ROLE")
    parser.add_argument("--link", action="append", type=parse_link, default=[], metavar="SOURCE->TARGET")
    parser.add_argument("--node-class", default="node")
    parser.add_argument("--link-class", default="link")
    parser.add_argument("--layout", choices=("force", "pre-ticked-force"), default="pre-ticked-force")
    parser.add_argument("--brand")
    parser.add_argument("--tagline")
    parser.add_argument("--force", action="store_true")
    return parser


def parse_args() -> argparse.Namespace:
    return make_parser().parse_args()


def main() -> int:
    args = parse_args()
    if args.width < 320 or args.height < 240:
        raise SystemExit("--width and --height must be at least 320x240")
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
