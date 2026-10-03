#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11.0.0", "playwright>=1.52.0"]
# ///
"""Check D3's data-driven builders, starters, recreation and dither routes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills/d3/scripts"
sys.path.insert(0, str(SCRIPTS))
from check_palette_contract import validate_artifact
from create_d3_svg_starter import STARTER_DATA
from check_self_contained_html import check_file
import dither_d3_output as dither
import prepare_svg_recreation_templates as recreation

OUT = ROOT / "projects/colorset-audit/artifacts"
results = []


def run(script, arguments, output=None, colorset="colorset1", expect_failure=False):
    command = [sys.executable, str(SCRIPTS / script), *map(str, arguments)]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if expect_failure:
        assert process.returncode != 0, command
    else:
        assert process.returncode == 0, (command, process.stderr)
        if output:
            assert validate_artifact(output, colorset=colorset)["ok"], output
    results.append({"script": script, "colorset": colorset, "rejection": expect_failure, "passed": True})


for active in ("colorset1", "colorset2"):
    for pattern in STARTER_DATA:
        folder = OUT / "html" / f"starter-{pattern}-{active}"
        run("create_d3_svg_starter.py", ["--pattern", pattern, "--out", folder, "--colorset", active, "--force"], folder / "index.html", active)
        assert validate_artifact(folder / "styles.css", colorset=active, require_metadata=False)["ok"]
    for script in ("build_kinetic_type.py", "build_logo_studio.py"):
        output = OUT / "html" / f"{Path(script).stem}-{active}.html"
        flags = [output] if script == "build_kinetic_type.py" else ["--output", output]
        run(script, [*flags, "--colorset", active], output, active)
    for kind in ("bar", "lollipop", "network", "flow", "logo"):
        output = OUT / "html" / f"contract-{kind}-{active}.html"
        specific = {
            "bar": ["--item", "Alpha=2", "--item", "Beta=5"],
            "lollipop": ["--item", "Alpha=2", "--item", "Beta=5"],
            "network": ["--node", "Alpha=primary", "--node", "Beta=neutral", "--link", "Alpha->Beta"],
            "flow": ["--flow-node", "Alpha", "--flow-node", "Beta", "--link", "Alpha->Beta", "--link-value", "2"],
            "logo": ["--brand", "Atlas", "--tagline", "Signal roles"],
        }[kind]
        run("build_contract_artifact.py", ["--kind", kind, "--output", output, "--decision-output", output.with_suffix(".json"), "--title", "Palette audit", "--description", "Explicit roles", "--route", "creation", "--colorset", active, "--pattern-id", f"d3-audit-{kind}", "--svg-id", "audit", "--reason", "Exact palette output", "--force", *specific], output, active)

source = OUT / "svgs" / "recreation-original.svg"
source.parent.mkdir(parents=True, exist_ok=True)
source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 80"><title>Source title</title><desc>Animation lifetime regression</desc><path d="M0 0L140 80" stroke="#abcdef"><animate attributeName="x" fill="freeze" values="0;10"/></path><text x="3" y="30" fill="#007298">Source title</text></svg>', encoding="utf-8")
digest = hashlib.sha256(source.read_bytes()).hexdigest()
for active in ("colorset1", "colorset2"):
    folder = OUT / "html" / f"recreation-{active}"
    expected = OUT / "svgs" / f"recreation-{active}"
    run("prepare_svg_recreation_templates.py", [source, "--template-dir", folder, "--expected-dir", expected, "--colorset", active], folder / "recreation-original.seed.svg", active)
    assert validate_artifact(expected / source.name, colorset=active)["ok"]
    assert not check_file(folder / "recreation-original.template.html")
    run("compare_svg_style_signatures.py", ["--pair", f"{folder / 'recreation-original.seed.svg'}={expected / source.name}"], colorset=active)
    assert (folder / "recreation-original.source-signature.json").exists()
assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
source.write_text(source.read_text().replace('#abcdef', 'tomato'), encoding="utf-8")
run("prepare_svg_recreation_templates.py", [source, "--template-dir", OUT / "tmp/rejected-seed", "--expected-dir", OUT / "tmp/rejected-expected"], expect_failure=True)

for active, palette in (("colorset1", "#000000,#9e1b32"), ("colorset2", "#000000,#007298")):
    colors = dither.parse_palette(palette)
    args = dict(width=2, height=1, cell_size=1, indices=[[0, 1]], alphas=[[255, 255]], palette=colors, alpha_threshold=24, algorithm="nearest", matrix_size=4, source="fixture", selector="svg", title="Dither test", animate=True, duration=1, colorset=active)
    markup, runs = dither.build_svg(**args)
    output = OUT / "svgs" / f"d3-dither-direct-{active}.svg"
    output.write_text(markup, encoding="utf-8")
    assert validate_artifact(output, colorset=active)["ok"]
    image = dither.build_preview([[0, 1]], [[255, 255]], colors, 2, 1, 24, active)
    assert set(image.getdata()) == {(*color, 255) for color in colors}
    results.append({"route": "dither-direct-svg-and-preview", "colorset": active, "passed": True})
for palette in ("#000000,#123456", "#000000,#007298"):
    try:
        dither.validate_palette_contract(dither.parse_palette(palette), "colorset1")
    except ValueError:
        results.append({"route": "dither-palette-rejection", "palette": palette, "passed": True})
    else:
        raise AssertionError(palette)

report = OUT / "data/d3-additional-route-coverage.json"
report.write_text(json.dumps({"ok": True, "caseCount": len(results), "results": results}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"ok": True, "caseCount": len(results), "report": str(report)}))
