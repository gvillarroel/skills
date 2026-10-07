#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record current inspector inventories for deliberately narrow SVG feature probes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    script = args.repository / "skills/lucidchart-svg/scripts/inspect_svg.py"
    spec = importlib.util.spec_from_file_location("current_svg_inspector", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    cases = {
        "inherited-style": '<g fill="#ffeecc" stroke="#333333" font-size="18"><rect x="5" y="10" width="20" height="30"/><text x="15" y="25">Inherited</text></g>',
        "css-paint-override": '<style>#a{fill:#00ff00}</style><rect id="a" x="5" y="10" width="20" height="30" fill="#ff0000"/>',
        "css-geometry-override": '<style>#a{x:40px;width:80px}</style><rect id="a" x="5" y="10" width="20" height="30"/>',
        "hidden-definition-labels": '<defs><text id="template">Template</text></defs><g display="none"><text>Ghost</text></g><text>Visible</text>',
        "internal-use": '<defs><rect id="template" width="20" height="30"/></defs><g data-node-id="node"><use href="#template" x="5" y="10"/></g>',
        "multiple-primitives-one-node": '<g data-node-id="node"><rect width="80" height="40"/><circle cx="10" cy="10" r="5"/><text>Compound</text></g>',
        "unstroked-semantic-edge": '<path id="e" data-source="a" data-target="b" d="M10 10 L30 10"/>',
        "none-paints": '<rect width="20" height="30" fill="none" stroke="none"/>',
        "alpha-paints": '<rect width="20" height="30" fill="#ff0000" fill-opacity="0.4" opacity="0.5"/>',
        "dashed-stroke": '<path d="M0 0L20 0" fill="none" stroke="#000000" stroke-dasharray="4 2" stroke-width="3"/>',
        "internal-marker": '<defs><marker id="arrow" viewBox="0 0 10 10"><path d="M0 0L10 5L0 10Z"/></marker></defs><path d="M0 0L20 0" stroke="#000000" marker-end="url(#arrow)"/>',
        "gradient-fill": '<defs><linearGradient id="g"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#000000"/></linearGradient></defs><rect width="20" height="30" fill="url(#g)"/>',
        "outline-only-label": '<path data-label="Outlined" d="M0 0L5 10L10 0Z"/>',
        "text-span-whitespace": '<text xml:space="preserve">  First<tspan x="0" dy="20">Second</tspan>  </text>',
        "css-animation": '<style>@keyframes shift{to{transform:translateX(10px)}}.a{animation:shift 1s infinite}</style><rect class="a" width="20" height="30"/>',
        "malformed-path-data": '<path d="this is not path data"/>',
        "negative-primitive-dimension": '<rect width="-20" height="30"/>',
        "unresolved-use": '<use href="#missing"/>',
        "cyclic-use": '<defs><g id="loop"><use href="#loop"/></g></defs><use href="#loop"/>',
        "foreign-namespace-geometry": '<other:rect xmlns:other="urn:other" width="20" height="30"/>',
    }
    outer = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{}</svg>'
    complete_cases = {key: outer.format(value) for key, value in cases.items()}
    complete_cases["viewport-scale-align"] = '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 100 100"><rect x="5" y="10" width="20" height="30"/></svg>'
    complete_cases["nested-viewport"] = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"><svg x="20" y="30" width="100" height="50" viewBox="0 0 20 10"><rect width="10" height="5"/></svg></svg>'
    for name in ("naturalistic", "generalization"):
        prompt = args.repository / f"evaluations/pi-prompts/lucidchart-svg-{name}.md"
        match = re.search(r"```xml\s*\n(.*?)\n```", prompt.read_text(encoding="utf-8"), re.S)
        assert match is not None
        complete_cases[f"fixture-{name}"] = match[1]
    args.output.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, content in complete_cases.items():
        path = args.output / f"{name}.svg"
        path.write_text(content + "\n", encoding="utf-8")
        _, report = module.inspect(path)
        (args.output / f"{name}.inspection.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary.append({
            "case": name,
            "ready_for_upload": report["ready_for_upload"],
            "labels": report["labels"],
            "vector_element_count": report["vector_element_count"],
            "blocking_flags": report["blocking_flags"],
            "portability_warnings": report["portability_warnings"],
            "element_counts": report["element_counts"],
        })
    result = {"inspector_sha256": hashlib.sha256(script.read_bytes()).hexdigest(), "probe_count": len(summary), "cases": summary}
    (args.output / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"probe_count": len(summary), "ready_count": sum(item["ready_for_upload"] for item in summary), "inspector_sha256": result["inspector_sha256"], "summary": str(args.output / "summary.json")}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
