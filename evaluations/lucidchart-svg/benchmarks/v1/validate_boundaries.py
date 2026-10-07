#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent artifact oracle for blocked-resource and ambiguous-topology cases."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

SOURCES = {
    "boundary": '''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="260" viewBox="0 0 480 260" onload="void(0)">
  <script>/* source fragment only */</script>
  <image id="brand" href="https://example.invalid/brand.svg" x="10" y="10" width="60" height="30"/>
  <g data-node-id="review"><rect x="100" y="70" width="160" height="60" fill="#ffffff" stroke="#222222"/></g>
  <foreignObject x="100" y="70" width="160" height="60"><div xmlns="http://www.w3.org/1999/xhtml">Review &amp; release</div></foreignObject>
</svg>
''',
    "ambiguity": '''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="180" viewBox="0 0 360 180">
  <rect id="left-box" x="20" y="60" width="90" height="50" fill="#dce8f7" stroke="#223344"/>
  <text x="35" y="90" font-family="Arial" font-size="12" fill="#223344">Queue &amp; sort</text>
  <rect id="right-box" x="250" y="60" width="90" height="50" fill="#f7e6dc" stroke="#443322"/>
  <text x="265" y="90" font-family="Arial" font-size="12" fill="#443322">Release</text>
  <path id="stroke-a" d="M110 60 L250 110" fill="none" stroke="#555555"/>
  <path id="stroke-b" d="M110 110 L250 60" fill="none" stroke="#777777"/>
</svg>
''',
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"Nonfinite JSON constant: {value}")
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_pairs,
                      parse_constant=reject_constant)


def validate(case: str, workspace: Path) -> dict:
    source_path = "input/received.svg" if case == "boundary" else "source/sketch.svg"
    raw = (workspace / source_path).read_bytes()
    require(raw == SOURCES[case].encode("utf-8"), "Supplied source bytes differ")
    root = ET.fromstring(raw)
    require(root.tag == "{http://www.w3.org/2000/svg}svg", "Source is not SVG")
    out = workspace / "out" / case
    note = out / "notes.md"
    require(note.is_file() and bool(note.read_text(encoding="utf-8").strip()), "Status note missing")
    report = load(out / "inspection.json")
    require(report.get("sha256") == hashlib.sha256(raw).hexdigest(), "Inspection source hash differs")
    require(report.get("bytes") == len(raw) and report.get("valid_svg") is True, "Inspection byte/XML identity differs")
    require(report.get("unresolved_fragment_references") == [], "Unexpected fragment references")
    checks = ["exact source bytes", "source-bound inspection", "required status note"]
    if case == "boundary":
        require(report.get("blocking_flags") == ["event-handler", "external-resource", "foreignObject-needs-review", "script"], "Blocker inventory differs")
        require(report.get("external_resources") == ["https://example.invalid/brand.svg"], "External resource inventory differs")
        require(report.get("ready_for_upload") is False and report.get("safe_to_render_offline") is False, "Blocked source marked eligible")
        require(report.get("view_box") == [0, 0, 480, 260], "Viewport differs")
        require(report.get("vector_element_count") == 1, "Foreign/image content miscounted as native vector")
        require(report.get("labels") == [], "XHTML text miscounted as SVG text")
        checks.append("exact resource/active-content blockers and namespace inventory")
    else:
        require(report.get("blocking_flags") == [] and report.get("external_resources") == [], "Self-contained source incorrectly blocked")
        require(report.get("ready_for_upload") is True and report.get("safe_to_render_offline") is True, "Visual asset readiness differs")
        require(report.get("view_box") == [0, 0, 360, 180], "Viewport differs")
        require(report.get("vector_element_count") == 6, "Literal vector count differs")
        require(report.get("labels") == ["Queue & sort", "Release"], "Literal labels differ")
        require((out / "visual.svg").read_bytes() == raw, "Visual fallback changes source bytes")
        checks.append("byte-identical eligible visual fallback and literal inventory")
    for path in workspace.rglob("*"):
        if not path.is_file() or "skills" in path.relative_to(workspace).parts:
            continue
        require(path.suffix.lower() not in {".lucid", ".zip"}, "Native or remote package invented")
        if path.suffix.lower() == ".svg":
            allowed = {source_path} if case == "boundary" else {source_path, "out/ambiguity/visual.svg"}
            require(path.relative_to(workspace).as_posix() in allowed, "Additional SVG falsely prepared/exported")
        if path.suffix.lower() == ".json":
            value = load(path)
            if isinstance(value, dict):
                require(not any(isinstance(value.get(key), (list, dict)) for key in
                                ("nodes", "edges", "shapes", "lines", "pages", "collections", "dataBackedShapes")),
                        "Native diagram fabricated from incomplete input")
            if isinstance(value, list):
                require(not any(isinstance(item, dict) and any(key in item for key in
                                                              ("type", "shapeType", "position", "source", "target")) for item in value),
                        "Native objects fabricated from incomplete input")
    checks.append("no invented native graph/package or remote export")
    return {"passed": True, "case": case, "checks": checks,
            "manual_review_required": ["actual operation status", "missing prerequisites", "topology/visual editability", "no live acceptance or fidelity claim"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=tuple(SOURCES))
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    require(not args.report.resolve().is_relative_to(args.workspace.resolve()), "Evaluator report must remain outside the candidate workspace")
    try:
        result = validate(args.case, args.workspace)
    except (ValueError, OSError, ET.ParseError) as error:
        result = {"passed": False, "case": args.case, "error": str(error)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
