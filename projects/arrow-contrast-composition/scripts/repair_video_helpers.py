#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Promote the shared arrow painter into the three acceptance-scene entry points."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'skills/video/assets/examples/ai-concept-videos'
def replace_function(path, name, replacement):
    text=path.read_text(encoding='utf-8')
    start=text.index(name);brace=text.index('{',start);depth=1;end=brace+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    text=text[:start]+replacement+text[end:]
    path.write_text(text,encoding='utf-8')
replace_function(BASE/'renderer.js','function arrow(','''function arrow(g, x1, y1, x2, y2, color = palette.gray500, opacity = 1, width = 2.5) {
  safeArrow(g, {x:x1,y:y1}, {x:x2,y:y2}, color, opacity, width, 9);
}''')
replace_function(BASE/'scenes/generic-visuals.js','function arrow(','''function arrow(g, from, to, color, opacity, width = 3) {
  safeArrow(g, from, to, color, opacity, width, 12);
}''')
replace_function(BASE/'scenes/evaluation-shared.js','export function drawArrow(','''export function drawArrow(g, from, to, color, opacity = 1, width = 3) {
  safeArrow(g, from, to, color, opacity, width, 10);
}''')
for name,statement in [('renderer.js',"import {drawArrow as safeArrow, finishArrows} from './svg-arrows.js';\n"),
                       ('scenes/generic-visuals.js',"import {drawArrow as safeArrow} from '../svg-arrows.js';\n"),
                       ('scenes/evaluation-shared.js',"import {drawArrow as safeArrow} from '../svg-arrows.js';\n")]:
    path=BASE/name;text=path.read_text(encoding='utf-8')
    if statement not in text:text=statement+text
    if name=='renderer.js':text=text.replace('  solidCategorySurfaces(svg.node());','  solidCategorySurfaces(svg.node());\n  finishArrows(svg.node(), {allowed:authoredColorset2,canvas:palette.white});')
    path.write_text(text,encoding='utf-8')
print('Updated three arrow painters without changing concept or pattern identities.')
