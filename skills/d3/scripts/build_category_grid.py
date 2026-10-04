#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Build an offline responsive D3 category grid and export its actual rendered SVG."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

from playwright.sync_api import sync_playwright

SKILL_ROOT = Path(__file__).resolve().parents[1]


def checked_data(value: object) -> list[dict]:
    if not isinstance(value, list) or not value:
        raise ValueError("Data must be a non-empty ordered JSON array of labels or objects with label")
    result = []
    for index, item in enumerate(value):
        record = {"label": item} if isinstance(item, str) else dict(item) if isinstance(item, dict) else {}
        label = record.get("label")
        if not isinstance(label, str) or not label.strip() or any(ord(char) < 32 for char in label):
            raise ValueError("Every category requires a non-empty label without control characters")
        record.setdefault("id", f"category-{index}")
        if not isinstance(record["id"], str) or not record["id"]:
            raise ValueError("Category IDs must be non-empty strings")
        result.append(record)
    if len({record["id"] for record in result}) != len(result):
        raise ValueError("Category IDs must be unique")
    return result


def script_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def build_document(data: object, *, title: str = "Category catalogue", description: str = "Ordered categories shown as equal-size directly labeled tiles.",
                   colorset: str = "colorset1", canvas: str = "#ffffff", width: int = 960, columns: int = 5,
                   svg_id: str = "category-grid", pattern_id: str = "d3-category-grid", tile_class: str = "category-tile") -> str:
    records = checked_data(data)
    palettes = json.loads((SKILL_ROOT / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
    if colorset not in palettes or canvas not in palettes[colorset]["allowed"]:
        raise ValueError("Canvas must be an exact lowercase token in the chosen bundled colorset")
    if not title.strip() or not description.strip():
        raise ValueError("Title and description must be non-empty")
    if not 320 <= width <= 4096 or not 1 <= columns <= 12:
        raise ValueError("Width must be 320–4096 pixels and columns must be 1–12")
    for name,value in [("SVG ID",svg_id),("pattern ID",pattern_id),("tile class",tile_class)]:
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*",value):
            raise ValueError(f"{name} must be one simple identifier")
    config = dict(data=records,title=title,description=description,colorset=colorset,canvas=canvas,width=width,columns=columns,
                  svgId=svg_id,patternId=pattern_id,tileClass=tile_class,text=palettes[colorset]["textOnFill"][canvas])
    template = (SKILL_ROOT / "assets/templates/category-grid.html").read_text(encoding="utf-8")
    replacements = {"__TITLE__":escape(title),"__DESC__":escape(description),"__SVG_ID__":svg_id,"__PATTERN_ID__":pattern_id,
        "__COLORSET__":colorset,"__CANVAS__":canvas,"__TEXT__":config["text"],"__WIDTH__":str(width),
        "__CONFIG__":script_json(config),"__PALETTES__":script_json(palettes),
        "__D3__":(SKILL_ROOT / "assets/vendor/d3.v7.9.0.min.js").read_text(encoding="utf-8"),
        "__SOLID__":(SKILL_ROOT / "assets/templates/solid-style.js").read_text(encoding="utf-8")}
    return re.sub("|".join(replacements),lambda match:replacements[match.group()],template)


CAPTURE = r'''svg => {
  window.D3SolidStyle.normalize(svg);
  const hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(n=>(+n).toString(16).padStart(2,'0')).join(''):value;};
  const clone=svg.cloneNode(true), originals=[svg,...svg.querySelectorAll('*')],copies=[clone,...clone.querySelectorAll('*')];
  const fields=['fill','stroke','stroke-width','stroke-dasharray','opacity','fill-opacity','stroke-opacity','font-family','font-size','font-weight','text-anchor'];
  originals.forEach((node,index)=>{const style=getComputedStyle(node);fields.forEach(field=>{
    const value=style.getPropertyValue(field);if(value)copies[index].setAttribute(field,hex(value));copies[index].style.removeProperty(field);
  });if(!copies[index].getAttribute('style'))copies[index].removeAttribute('style');});
  const tiles=[...svg.querySelectorAll('rect[data-category-index]')];
  const allocation={canvas:svg.dataset.canvas,labels:tiles.map(node=>node.__data__.label),styles:tiles.map(node=>{
    const style=getComputedStyle(node),text=node.parentElement.querySelector('text');
    return {fill:hex(style.fill),text:hex(getComputedStyle(text).fill),stroke:hex(style.stroke),strokeWidth:parseFloat(style.strokeWidth),strokeDasharray:style.strokeDasharray==='none'?null:style.strokeDasharray,opacity:+style.opacity,tier:node.parentElement.dataset.outlineTier};
  })};
  return {markup:clone.outerHTML,allocation,version:d3.version};
}'''


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,epilog="Use uv run --script. Data is an ordered JSON array of strings or objects with label and optional unique id/extra caller data. Outputs are outside the read-only skill. Correct input/flags and rerun; no post-edit is needed for a supported grid.")
    parser.add_argument("--data",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True,help="Exact offline HTML path")
    parser.add_argument("--svg-output",type=Path,help="Exact actual rendered standalone SVG path")
    parser.add_argument("--allocation-output",type=Path,help="Exact JSON path for actual computed tile styles")
    parser.add_argument("--screenshot",type=Path,help="Optional desktop SVG inspection PNG")
    parser.add_argument("--title",default="Category catalogue")
    parser.add_argument("--description",default="Ordered categories shown as equal-size directly labeled tiles.")
    parser.add_argument("--colorset",choices=("colorset1","colorset2"),default="colorset1")
    parser.add_argument("--canvas",default="#ffffff")
    parser.add_argument("--width",type=int,default=960,help="Maximum page width; narrower layouts recompute columns")
    parser.add_argument("--columns",type=int,default=5,help="Maximum columns; mobile uses fewer columns with complete tile bounds")
    parser.add_argument("--svg-id",default="category-grid")
    parser.add_argument("--pattern-id",default="d3-category-grid")
    parser.add_argument("--tile-class",default="category-tile")
    parser.add_argument("--force",action="store_true")
    return parser


def main() -> int:
    parser=make_parser();args=parser.parse_args()
    paths=[path.resolve() for path in [args.output,args.svg_output,args.allocation_output,args.screenshot] if path]
    try:
        if len(set(paths))!=len(paths) or args.data.resolve() in paths:
            raise ValueError("Input and output paths must all differ")
        if any(path.is_relative_to(SKILL_ROOT) for path in paths):
            raise ValueError("Outputs must be outside the read-only skill directory")
        if any(path.exists() for path in paths) and not args.force:
            raise ValueError("An output exists; pass --force to replace it")
        if args.output.suffix.lower()!='.html' or (args.svg_output and args.svg_output.suffix.lower()!='.svg'):
            raise ValueError("Use .html and .svg output extensions")
        document=build_document(json.loads(args.data.read_text(encoding="utf-8")),title=args.title,description=args.description,
            colorset=args.colorset,canvas=args.canvas,width=args.width,columns=args.columns,svg_id=args.svg_id,pattern_id=args.pattern_id,tile_class=args.tile_class)
        for path in paths:path.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(document,encoding="utf-8",newline="\n")
        if args.svg_output or args.allocation_output or args.screenshot:
            with sync_playwright() as playwright:
                options={} if Path(playwright.chromium.executable_path).exists() else {"channel":"msedge"} if sys.platform=='win32' else {}
                browser=playwright.chromium.launch(**options)
                page=browser.new_page(viewport={"width":args.width,"height":900},reduced_motion="reduce")
                errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(args.output.resolve().as_uri(),wait_until='load');page.wait_for_function('window.categoryGridReady===true')
                locator=page.locator(f'svg#{args.svg_id}');capture=locator.evaluate(CAPTURE)
                if errors or capture['version']!='7.9.0':raise ValueError(f"Browser runtime failed: {errors}")
                if args.svg_output:args.svg_output.write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+capture['markup']+'\n',encoding='utf-8',newline='\n')
                if args.allocation_output:args.allocation_output.write_text(json.dumps(capture['allocation'],indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
                if args.screenshot:locator.screenshot(path=str(args.screenshot.resolve()))
                browser.close()
    except (OSError,ValueError) as error:
        parser.exit(1,f"[ERROR] {error}\n")
    print(json.dumps({"output":str(args.output),"svg":str(args.svg_output) if args.svg_output else None,"allocation":str(args.allocation_output) if args.allocation_output else None,"colorset":args.colorset}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
