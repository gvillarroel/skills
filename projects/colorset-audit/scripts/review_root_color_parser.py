#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent probes of root paint parser; store reproducible audit evidence."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("root_color_parser", ROOT / "scripts/validate-colorsets.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
folder = ROOT / "projects/colorset-audit/artifacts/tmp/root-color-parser"
folder.mkdir(parents=True, exist_ok=True)
cases = {
    "inline-html-paint": ('html', '<html><body data-colorset="colorset1"><svg><rect fill="red"/></svg></body></html>'),
    "inline-html-gradient-stop": ('html', '<html><body data-colorset="colorset1"><svg><linearGradient><stop stop-color="#abcdef"/></linearGradient></svg></body></html>'),
    "custom-property-named-paint": ('svg', '<svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset1"><style>:root{--ink:tomato}.x{fill:var(--ink)}</style><rect class="x"/></svg>'),
    "nested-gradient-functional-stop": ('svg', '<svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset1"><style>.x{background:linear-gradient(to right,rgb(255,0,0),black)}</style></svg>'),
    "smil-lifecycle": ('svg', '<svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset1"><rect fill="#9e1b32"><animate attributeName="x" fill="freeze" values="1;2"/></rect></svg>'),
    "canonical-percent-rgb": ('svg', '<svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset1"><rect fill="rgb(100% 100% 100% / 50%)"/></svg>'),
}
results = []
for name, (suffix, content) in cases.items():
    path = folder / f"{name}.{suffix}"
    path.write_text(content, encoding="utf-8")
    result = module.validate(ROOT, [path], "colorset1")
    results.append({"case": name, "expectedPass": name in {"smil-lifecycle", "canonical-percent-rgb"}, "actualPass": result["ok"], "findings": result["findings"]})
report = ROOT / "projects/colorset-audit/artifacts/data/root-color-parser-review.json"
report.write_text(json.dumps({"results": results}, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
