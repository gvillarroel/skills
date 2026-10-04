#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build offline dense task overlap from the bundled renderer and generated layout."""

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
PATTERN = SKILL_ROOT / "references/patterns/task-overlap-dense.md"
VENDOR = SKILL_ROOT / "assets/vendor/d3.v7.9.0.min.js"
PALETTES = {
    "colorset1": dict(blue="#9e1b32", orange="#696969", green="#4f4f4f", red="#9e1b32",
                     purple="#828282", cyan="#696969", blueHover="#6d1222", orangeHover="#4f4f4f",
                     greenHover="#363636", yellowHover="#696969", blueHighlight="#ffccd5",
                     orangeHighlight="#e7e7e7", greenHighlight="#e7e7e7", redHighlight="#ffccd5",
                     purpleHighlight="#e7e7e7", yellowHighlight="#e7e7e7"),
    "colorset2": dict(blue="#007298", orange="#e77204", green="#45842a", red="#9e1b32",
                     purple="#652f6c", cyan="#00ace6", blueHover="#004d66", orangeHover="#994a00",
                     greenHover="#294d19", yellowHover="#98700c", blueHighlight="#cdf3ff",
                     orangeHighlight="#ffe5cc", greenHighlight="#dbffcc", redHighlight="#ffccd5",
                     purpleHighlight="#f9ccff", yellowHighlight="#fff4cc"),
}


def text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError(f"{field} must be non-empty literal text without surrounding whitespace or control characters")
    return value


def number(value: object, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{field} must be positive")
    return value


def validate_layout(payload: object) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("saturated"), dict):
        raise ValueError("Layout requires the saturated object from the bundled layout generator")
    layout = payload["saturated"]
    width, height = number(layout.get("width"), "width", positive=True), number(layout.get("height"), "height", positive=True)
    if width < 480 or height < 320:
        raise ValueError("The dense layout requires width >= 480 and height >= 320")
    circles, tasks = layout.get("circles"), layout.get("tasks")
    if not isinstance(circles, list) or len(circles) != 9 or not isinstance(tasks, list) or len(tasks) != 100:
        raise ValueError("The dense pattern requires exactly 9 regions and 100 tasks")
    if layout.get("circleCount") != 9 or layout.get("targetCount") != 100:
        raise ValueError("Declared region/task counts must agree with the actual layout")
    number(layout.get("dotRadius"), "dotRadius", positive=True)
    circle_ids, task_ids = set(), set()
    for circle in circles:
        if not isinstance(circle, dict): raise ValueError("Each region must be an object")
        identity = text(circle.get("id"), "Region ID")
        if identity in circle_ids: raise ValueError("Region IDs must be unique")
        circle_ids.add(identity)
        text(circle.get("label"), "Region label")
        for field in ("cx", "cy", "r", "lx", "ly"): number(circle.get(field), field, positive=field == "r")
        for field in ("fill", "stroke"):
            if circle.get(field) not in PALETTES["colorset2"]: raise ValueError(f"Unknown region palette key: {field}")
    for task in tasks:
        if not isinstance(task, dict): raise ValueError("Each task must be an object")
        identity = text(task.get("id"), "Task ID")
        if identity in task_ids: raise ValueError("Task IDs must be unique")
        task_ids.add(identity)
        text(task.get("label"), "Task label")
        for field in ("x", "y", "labelX", "labelY", "labelWidth", "labelHeight"):
            number(task.get(field), field, positive=field in ("labelWidth", "labelHeight"))
        for field in ("labelEdgeX", "labelEdgeY", "labelFontSize", "labelTextPaddingX"):
            if field in task: number(task[field], field, positive=field == "labelFontSize")
        memberships = task.get("memberships")
        if not isinstance(memberships, list) or not memberships or len(set(memberships)) != len(memberships) or not set(memberships) <= circle_ids:
            raise ValueError("Task memberships must name distinct existing region IDs")
        if task.get("membershipCount") != len(memberships): raise ValueError("Task membership count is inconsistent")
        if task.get("leaderColorKey") not in PALETTES["colorset2"]: raise ValueError("Unknown leader palette key")
    if not isinstance(layout.get("membershipBuckets"), dict): raise ValueError("Membership buckets are required")
    return payload


def load_layout(path: Path) -> dict:
    assignment = re.fullmatch(r"\s*(?://[^\n]*\n\s*)*window\.D3_TASK_OVERLAP_LAYOUTS\s*=\s*(\{[\s\S]*\})\s*;\s*", path.read_text(encoding="utf-8"))
    if not assignment: raise ValueError("Layout must be the generated JSON assignment, without executable additions")
    return validate_layout(json.loads(assignment.group(1)))


def script_json(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    for character, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("#", "\\u0023")):
        encoded = encoded.replace(character, escaped)
    return encoded


def build_document(payload: dict, *, colorset: str = "colorset1", title: str = "Dense task overlap") -> str:
    validate_layout(payload)
    title = text(title, "Title")
    if colorset not in PALETTES: raise ValueError("Select colorset1 or colorset2")
    match = re.search(r"```js\s*\n(function renderAsymmetricTaskOverlapSaturated\(\)[\s\S]*?)\n```", PATTERN.read_text(encoding="utf-8"))
    if not match: raise ValueError("The bundled dense-overlap renderer excerpt is missing")
    palette = dict(PALETTES[colorset], surface="#ffffff", ink="#333e48", gray700="#4f4f4f", gray200="#cfcfcf")
    contract = json.loads((SKILL_ROOT / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][colorset]
    config = dict(title=title, colorset=colorset, palette=palette,
                  categoryColors=[paint for paint in contract["solidSequence"] if paint != palette["surface"]],
                  patternId="d3-task-overlap-dense-cs1" if colorset == "colorset1" else "d3-task-overlap-dense-cs2")
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,"><title>__TITLE__</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f7f7;color:#000000;font-family:Arial,Helvetica,sans-serif}
main{max-width:960px;padding:12px;margin:auto;min-width:0}h1{font-size:20px;margin:0 0 8px;overflow-wrap:anywhere}
button{border:0;border-radius:4px;background:#9e1b32;color:#ffffff;padding:8px 12px;cursor:pointer;font:inherit}
button:focus-visible{outline:2px solid #000000;outline-offset:3px}.controls{margin-bottom:8px}
.viz-frame{width:100%;overflow-x:auto;background:#ffffff}svg{display:block;max-width:none}
svg text{font-family:Arial,Helvetica,sans-serif}.caption:not([font-size]){font-size:10.5px}
</style></head><body><main><h1>__TITLE__</h1><div class="controls"><button id="replay" type="button">Replay</button></div>
<div class="viz-frame" data-example="task-overlap-dense"><svg id="task-overlap-dense" xmlns="http://www.w3.org/2000/svg" role="img"
aria-labelledby="overlap-title overlap-description" data-pattern-id="__PATTERN_ID__"><title id="overlap-title">__TITLE__</title>
<desc id="overlap-description">Nine regions use semantic transparency to reveal shared membership; 100 task dots and labels stay opaque.</desc></svg></div></main>
<script id="d3-runtime">__D3__</script><script>
const config=__CONFIG__, palette=config.palette, activeColorset=config.colorset, colors=config.categoryColors;
window.D3_TASK_OVERLAP_LAYOUTS=JSON.parse(__LAYOUT_JSON__);
const layout=window.D3_TASK_OVERLAP_LAYOUTS.saturated, width=layout.width, height=layout.height;
const motion=matchMedia('(prefers-reduced-motion: reduce)');
function prepareSvg(id,title,description){
  const svg=d3.select('#task-overlap-dense');svg.selectAll('*').remove();
  svg.attr('width',width).attr('height',height).attr('viewBox',`0 0 ${width} ${height}`)
    .attr('data-colorset',config.colorset).attr('data-pattern-id',config.patternId);
  svg.append('title').attr('id','overlap-title').text(config.title);
  svg.append('desc').attr('id','overlap-description').text(description+' The summary and legend occupy a separate caption rail below the unchanged task layout.');
  return svg;
}
// Every geometry attribute is final immediately; Replay animates opacity only.
function grow(selection,attribute,from,to){selection.attr(attribute,to);}
function fadeIn(selection){selection.attr('opacity',1);}
__RENDERER__
function render(replay=false){
  renderAsymmetricTaskOverlapSaturated();
  const svg=d3.select('#task-overlap-dense'), bottom=Math.max(...layout.tasks.map(task=>task.labelY+task.labelHeight));
  const railTop=Math.max(height,bottom+16), baseline=railTop+18, canvasHeight=baseline+20;
  svg.attr('height',canvasHeight).attr('viewBox',`0 0 ${width} ${canvasHeight}`)
    .attr('data-source-height',height).attr('data-caption-rail-y',railTop);
  svg.select('rect').attr('height',canvasHeight-28);
  svg.selectAll(':scope > text.caption').attr('class','caption overlap-footer').attr('y',baseline).attr('font-size',10.5);
  svg.selectAll(':scope > g').filter(function(){return this.querySelectorAll('circle').length===3 && this.querySelectorAll('text').length===3;})
    .attr('class','overlap-legend').attr('transform',`translate(${width-438},${baseline-3.5})`).selectAll('text').attr('font-size',10.5);
  if(replay && !motion.matches){
    svg.node().setCurrentTime?.(0);
    svg.node().unpauseAnimations?.();
    const reveal=svg.append('animate').attr('attributeName','opacity').attr('values','0;1').attr('dur','.45s').attr('fill','freeze').attr('begin','indefinite');
    reveal.node().beginElement();
  }
  window.D3SolidStyle?.normalize(svg.node());
}
document.querySelector('#replay').addEventListener('click',()=>render(true));
motion.addEventListener('change',()=>render());render();
</script></body></html>'''
    replacements = {"__TITLE__": escape(title).replace("#", "&#35;"), "__CONFIG__": script_json(config),
                    "__LAYOUT_JSON__": script_json(script_json(payload)), "__RENDERER__": match.group(1),
                    "__D3__": VENDOR.read_text(encoding="utf-8"), "__PATTERN_ID__": config["patternId"]}
    document = re.sub("|".join(replacements), lambda item: replacements[item.group()], template)
    return adapt_artifact(document, colorset)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build offline dense overlap from the generated layout. Keep final radius attributes and place captions on a separate rail; export through render_d3_svg.py.")
    parser.add_argument("--layout", type=Path, required=True, help="JavaScript JSON assignment from layout_task_overlap_labels.py")
    parser.add_argument("--output", type=Path, required=True, help="Exact HTML output outside the read-only skill resource")
    parser.add_argument("--colorset", choices=tuple(PALETTES), default="colorset1")
    parser.add_argument("--title", default="Dense task overlap")
    parser.add_argument("--force", action="store_true", help="Replace an existing output outside the skill resource")
    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        output = args.output.resolve()
        if output.is_relative_to(SKILL_ROOT) or output == args.layout.resolve() or output.suffix.lower() != ".html":
            raise ValueError("Output must be an HTML file outside the skill resource and distinct from the layout")
        if output.exists() and not args.force: raise ValueError("Output exists; pass --force to replace it")
        document = build_document(load_layout(args.layout), colorset=args.colorset, title=args.title)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document, encoding="utf-8", newline="\n")
    except (OSError, ValueError, TypeError, OverflowError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1
    print(json.dumps(dict(output=str(output), colorset=args.colorset, regions=9, tasks=100, opacity=.28)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
