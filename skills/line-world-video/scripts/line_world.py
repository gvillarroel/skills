#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create and rebuild a project-owned, seekable line-world composition."""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import shutil
import sys
import hashlib
from pathlib import Path
from atlas_story import DEFAULT_ATLAS, coverage, validate_atlas
from attention_contract import DEFAULT_ATTENTION, validate_attention
from video_edit import THEME, validate_theme, theme_css, transaction, setup as setup_editing

SKILL = Path(__file__).resolve().parent.parent
BEATS = ("cloud", "relations", "travel", "compare", "history", "categories", "overview")
DEFAULT = {
    "schemaVersion": 1, "width": 1920, "height": 1080, "fps": 30,
    "palette": "colorset1",
    "paletteReason": "Red guides attention; neutral geometry and direct labels distinguish records.",
    "dataStatus": "synthetic", "unit": "days",
    "presentation": {"contextLabels": {}},
    "attention": copy.deepcopy(DEFAULT_ATTENTION),
    "timing": dict(zip(BEATS, (7, 8, 4, 14, 9, 8, 6))),
    "copy": {"entity": "Stage", "observations": "Observation"},
    "rows": [
        {"id": "intake", "label": "Intake", "before": 18, "after": 12, "trend": [18, 17, 16, 15, 13, 12]},
        {"id": "review", "label": "Review", "before": 14, "after": 8, "trend": [14, 13, 12, 10, 9, 8]},
        {"id": "build", "label": "Build", "before": 24, "after": 16, "trend": [24, 22, 23, 20, 18, 16]},
        {"id": "release", "label": "Release", "before": 10, "after": 6, "trend": [10, 10, 9, 8, 7, 6]}
    ]
}


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(raw):
    if raw.get("mode") == "atlas":
        return validate_atlas(raw)
    story = copy.deepcopy(raw)
    if story.get("schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1.")
    for key in ("width", "height"):
        if not isinstance(story.get(key), int) or isinstance(story[key], bool) or story[key] < 320 or story[key] % 2:
            raise ValueError(f"{key} must be an even integer of at least 320.")
    if story["width"] * 9 != story["height"] * 16:
        raise ValueError("The starter requires 16:9; adapt the layout for another aspect ratio.")
    if story.get("fps") not in (24, 25, 30, 60):
        raise ValueError("fps must be 24, 25, 30 or 60.")
    if story.get("palette") not in ("colorset1", "colorset2"):
        raise ValueError("palette must be colorset1 or colorset2.")
    if story["palette"] == "colorset2" and not story.get("paletteReason", "").strip():
        raise ValueError("colorset2 requires a paletteReason.")
    if story.get("dataStatus") not in ("synthetic", "supplied"):
        raise ValueError("dataStatus must be synthetic or supplied.")
    if not isinstance(story.get("unit"), str) or not story["unit"].strip():
        raise ValueError("A nonempty unit is required.")
    rows = story.get("rows", [])
    if not 2 <= len(rows) <= 8:
        raise ValueError("The starter requires 2–8 rows.")
    ids, lengths = set(), set()
    for row in rows:
        rid = row.get("id", "")
        if not isinstance(rid, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", rid) or rid in ids:
            raise ValueError("Row IDs must be unique lowercase hyphen-case identifiers.")
        ids.add(rid)
        if not isinstance(row.get("label"), str) or not row["label"].strip() or len(row["label"]) > 22:
            raise ValueError("Row labels must contain 1–22 characters; adapt the layout for longer labels.")
        for key in ("before", "after"):
            if not numeric(row.get(key)) or row[key] < 0:
                raise ValueError(f"{rid}.{key} must be a finite nonnegative number.")
        row.setdefault("trend", [row["before"], row["after"]])
        if not isinstance(row["trend"], list) or len(row["trend"]) < 2 or any(not numeric(v) or v < 0 for v in row["trend"]):
            raise ValueError(f"{rid}.trend requires at least two finite nonnegative observations.")
        lengths.add(len(row["trend"]))
    if len(lengths) != 1:
        raise ValueError("All histories must have the same observation count.")
    copy_values = story.get("copy", {})
    for key in DEFAULT["copy"]:
        if not isinstance(copy_values.get(key), str) or not copy_values[key].strip():
            raise ValueError(f"copy.{key} must be a nonempty string.")
    presentation = story.setdefault("presentation", {})
    if not isinstance(presentation, dict):
        raise ValueError("presentation must be an object.")
    context = presentation.setdefault("contextLabels", {})
    if not isinstance(context, dict) or any(key not in BEATS for key in context):
        raise ValueError("contextLabels must map supported beat IDs to explicitly requested short labels.")
    if any(not isinstance(value, str) or not value.strip() or len(value) > 48 or len(value.split()) > 6 for value in context.values()):
        raise ValueError("Requested context labels must contain 1–6 words and at most 48 characters.")
    start, beats = 0.0, []
    if set(story.get("timing", {})) != set(BEATS):
        raise ValueError("timing must contain exactly the seven supported beat IDs.")
    for key in BEATS:
        duration = story["timing"][key]
        if not numeric(duration) or duration < 2:
            raise ValueError(f"timing.{key} must be at least 2 seconds.")
        beats.append({"id": key, "start": start, "duration": duration, "end": start + duration})
        start += duration
    if story["timing"]["compare"] < 2 + 2 * len(rows):
        raise ValueError("compare must allow 2 seconds plus at least 2 seconds per row.")
    if story["timing"]["history"] < 5:
        raise ValueError("history must allow at least 5 seconds.")
    if abs(start * story["fps"] - round(start * story["fps"])) > 1e-7:
        raise ValueError("Total duration must contain an integral number of frames at the selected fps.")
    story.update(duration=start, beats=beats)
    return validate_attention(story)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update(project, patch):
    """Merge a bounded story edit, validate, and rebuild with rollback on failure."""
    path=project/'story.json';original=path.read_bytes();raw=json.loads(original.decode('utf-8-sig'))
    def merge(a,b):
        if not isinstance(b,dict):return copy.deepcopy(b)
        result=copy.deepcopy(a) if isinstance(a,dict) else {}
        for key,value in b.items():
            if value is None:result.pop(key,None)
            else:result[key]=merge(result.get(key),value)
        return result
    if not isinstance(patch,dict):raise ValueError('Patch must be a JSON object.')
    candidate=merge(raw,patch);validate(candidate)
    if candidate==raw:return {'ok':True,'changed':False,'rebuilt':False}
    # Keep authored story and generated outputs intact if an asset preflight fails.
    generated=['story.json','story.js','index.html','timing.json','selection.json','coverage.json','theme.json','theme.css']
    snapshots={name:(project/name).read_bytes() if (project/name).is_file() else None for name in generated}
    history=project/'.line-world/history'/ (hashlib.sha256(original).hexdigest()+'.json')
    write_json(history,raw)
    try:
        write_json(path,candidate);result=build(project)
    except Exception:
        for name,value in snapshots.items():
            target=project/name
            if value is None:
                if target.exists():target.unlink()
            else:target.write_bytes(value)
        raise
    return {**result,'changed':True,'rebuilt':True,'previousStory':str(history)}


def local_svg(project, name, namespace):
    target = (project / name).resolve()
    if not target.is_relative_to(project.resolve()) or target.suffix != ".svg":
        raise ValueError("Diagram assets must be SVG files inside the project.")
    svg = target.read_text(encoding="utf-8")
    if re.search(r"<script\b|<foreignObject\b|\son[a-z]+\s*=|(?:href|src)\s*=\s*['\"](?:https?:|javascript:)|@import|url\(['\"]?https?:", svg, re.I):
        raise ValueError("Flatten diagrams to local script-free SVG without foreignObject.")
    svg = svg[svg.index("<svg"):]
    ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', svg))
    for old in sorted(ids, key=len, reverse=True):
        new = namespace + "-" + old
        svg = re.sub(r'(?P<a>\bid=["\'])' + re.escape(old) + r'(?P<b>["\'])', lambda m: m["a"] + new + m["b"], svg)
        svg = re.sub(r'#' + re.escape(old) + r'(?![\w-])', "#" + new, svg)
        svg = re.sub(r'(?P<a>\baria-(?:labelledby|describedby)=["\'])(?P<v>[^"\']+)(?P<b>["\'])', lambda m: m["a"] + " ".join(new if t == old else t for t in m["v"].split()) + m["b"], svg)
    return svg


def build(project):
    story = validate(json.loads((project / "story.json").read_text(encoding="utf-8-sig")))
    theme_path=project/'theme.json'
    theme=validate_theme(json.loads(theme_path.read_text(encoding='utf-8-sig')) if theme_path.is_file() else {**copy.deepcopy(THEME),'palette':story['palette']})
    palette_path=project / "assets/palettes/video-colors.json"
    if not palette_path.is_file():palette_path=project / "assets/palettes/colorsets.json"
    palette = json.loads(palette_path.read_text(encoding="utf-8"))
    story["textOnFill"] = palette["colorsets"][story["palette"]]["textOnFill"]
    story["colorSequence"] = palette["colorsets"][story["palette"]]["sequence"]
    story["icons"] = {}
    for file in sorted((project / "assets/icons").glob("*.svg")):
        svg = file.read_text(encoding="utf-8")
        body = re.sub(r"^.*?<svg[^>]*>|</svg>.*$", "", svg, flags=re.S).strip()
        story["icons"][file.stem] = '<g fill="none" stroke="var(--lw-ink)" stroke-width="var(--lw-line-width)" stroke-linecap="round" stroke-linejoin="round">' + body + '</g>'
    diagram = story.get("assets", {}).get("mermaid")
    if story.get("mode") == "atlas":
        story["diagrams"] = {name: local_svg(project, filename, "atlas-" + name) for name, filename in story["assets"]["diagrams"].items()}
    story["diagramSvg"] = None
    if diagram:
        target = (project / diagram).resolve()
        if not target.is_relative_to(project.resolve()) or target.suffix != ".svg":
            raise ValueError("The Mermaid asset must be an SVG inside the project.")
        svg = target.read_text(encoding="utf-8")
        if re.search(r"<script\b|<foreignObject\b|(?:href|src)\s*=\s*['\"](?:https?:|javascript:)", svg, re.I):
            raise ValueError("Flatten the diagram to local script-free SVG without foreignObject.")
        story["diagramSvg"] = re.sub(r"^.*?(?=<svg)", "", svg, flags=re.S)
    transaction({theme_path:(json.dumps(theme,indent=2)+'\n').encode('utf-8'),project/'theme.css':theme_css(theme).encode('utf-8')})
    (project / "story.js").write_text("window.STORY = " + json.dumps(story, ensure_ascii=False).replace("</", "<\\/") + ";\n", encoding="utf-8")
    index = project / "index.html"
    html = index.read_text(encoding="utf-8")
    values = {"WIDTH": story["width"], "HEIGHT": story["height"], "FPS": story["fps"], "DURATION": story["duration"], "PALETTE": story["palette"]}
    for key, val in values.items():
        html = html.replace(f"__{key}__", str(val))
        attr = "colorset" if key == "PALETTE" else key.lower()
        html = re.sub(rf'(data-{attr}=")[^"]*(")', lambda m: m[1] + str(val) + m[2], html)
    index.write_text(html, encoding="utf-8")
    if story.get("mode") == "atlas":
        inventory = coverage(story)
        write_json(project / "timing.json", {"duration": story["duration"], "fps": story["fps"], "beats": story["beats"], "focusWindows": []})
        write_json(project / "coverage.json", inventory)
        write_json(project / "selection.json", {"dataStatus": story["dataStatus"], "unit": story["unit"], "palette": story["palette"], "paletteReason": story["paletteReason"], "contextLabels": story["presentation"]["contextLabels"], "visibleHeadingsByDefault": False, "layout": "full-frame-partitions", "audio": "silent", "coverage": inventory})
        return {"ok": True, "project": str(project), "duration": story["duration"], "frameCount": round(story["duration"]*story["fps"]), "palette": story["palette"], "mermaidFamilies": len(inventory["mermaidFamilies"]), "d3Forms": len(inventory["d3Forms"])}
    compare = next(b for b in story["beats"] if b["id"] == "compare")
    span = (compare["duration"] - 2) / len(story["rows"])
    focus = [{"rowId": row["id"], "start": compare["start"] + 2 + i * span, "end": compare["start"] + 2 + (i + 1) * span, "before": row["before"], "after": row["after"]} for i, row in enumerate(story["rows"])]
    write_json(project / "timing.json", {"duration": story["duration"], "fps": story["fps"], "beats": story["beats"], "focusWindows": focus})
    write_json(project / "selection.json", {"dataStatus": story["dataStatus"], "unit": story["unit"], "palette": story["palette"], "paletteReason": story.get("paletteReason"), "question": "How do paired values and histories differ by entity?", "views": ["source-table", "fixed-domain-paired-bars", "fixed-domain-histories", "proportional-partition"], "contextLabels": story["presentation"]["contextLabels"], "visibleHeadingsByDefault": False, "diagramProducer": "Mermaid" if diagram else "Original SVG fallback", "audio": "silent"})
    return {"ok": True, "project": str(project), "duration": story["duration"], "frameCount": round(story["duration"] * story["fps"]), "palette": story["palette"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "build", "validate", "update"))
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--story", type=Path)
    parser.add_argument("--patch", type=Path, help="JSON merge patch for update; arrays replace complete arrays.")
    parser.add_argument("--layout", choices=("linked", "atlas"), default="linked", help="Choose the linked-data starter or the full-frame multi-view atlas.")
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        if args.command=='update':
            if not args.patch:raise ValueError('update requires --patch.')
            print(json.dumps(update(project,json.loads(args.patch.read_text(encoding='utf-8-sig'))),ensure_ascii=False));return 0
        if args.command == "init":
            raw = json.loads(args.story.read_text(encoding="utf-8-sig")) if args.story else (DEFAULT_ATLAS if args.layout == "atlas" else DEFAULT)
            validate(raw)
            if project.exists() and any(project.iterdir()):
                raise ValueError("Refusing to replace a nonempty project; use build for existing projects.")
            project.mkdir(parents=True, exist_ok=True)
            for name in ("index.html", "preview.html", "scene.js"):
                source_name = "atlas-scene.js" if name == "scene.js" and raw.get("mode") == "atlas" else name
                shutil.copyfile(SKILL / "assets/templates" / source_name, project / name)
            for name in ("vendor", "fonts", "icons", "palettes", "runtime"):
                shutil.copytree(SKILL / "assets" / name, project / "assets" / name)
            if raw.get("mode") == "atlas":
                shutil.copytree(SKILL / "assets/diagrams", project / "assets/diagrams")
            (project / "scripts").mkdir()
            for name in ("hf.ts", "local-runtime.ts"):
                shutil.copyfile(SKILL / "assets/templates" / name, project / "scripts" / name)
            for source, destination in (("line_world.py", "story.py"), ("atlas_story.py", "atlas_story.py"), ("attention_contract.py", "attention_contract.py"), ("video_edit.py", "video_edit.py")):
                shutil.copyfile(SKILL / "scripts" / source, project / "scripts" / destination)
            write_json(project / "story.json", raw)
            write_json(project / "package.json", {"name": "line-world-film", "private": True, "type": "module", "dependencies": {"hyperframes": "0.8.111"}})
        if args.command == "validate":
            story = validate(json.loads((project / "story.json").read_text(encoding="utf-8-sig")))
            result = {"ok": True, "duration": story["duration"], "rows": len(story["rows"])}
        else:
            result = build(project)
            if args.command=='init':setup_editing(project)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
