#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reproduce three evaluator fixtures locally before isolated forward trials."""

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "projects/lucid-svg-best-practices/artifacts/data/smoke-lf"
SKILL = ROOT / "skills/lucidchart-svg/scripts"
for case in ("contract", "naturalistic", "generalization"):
    prompt = (ROOT / f"evaluations/pi-prompts/lucidchart-svg-best-practices-{case}.md").read_text(encoding="utf-8")
    language = "xml" if case == "naturalistic" else "json"
    content = re.search(rf"```{language}\n(.*?)\n```", prompt, re.S).group(1) + "\n"
    workspace = BASE / case
    (workspace / "input").mkdir(parents=True, exist_ok=True)
    (workspace / "out").mkdir(exist_ok=True)
    filename = {"contract": "graph.json", "naturalistic": "source.svg", "generalization": "layout.json"}[case]
    source = workspace / "input" / filename
    source.write_bytes(content.encode("utf-8"))
    if case == "naturalistic":
        subprocess.run([sys.executable, str(SKILL / "inspect_svg.py"), "inspect", str(source), "--report", str(workspace / "out/inspection.json"), "--overwrite"], check=True)
        subprocess.run([sys.executable, str(SKILL / "extract_native.py"), str(source), "--coordinates", "viewport-pixels", "--output", str(workspace / "out/graph.json"), "--report", str(workspace / "out/mapping.json"), "--overwrite"], check=True)
        source = workspace / "out/graph.json"
    driver = "build_generated.py" if case == "generalization" else "build_native.py"
    report = "layout-report.json" if case == "generalization" else "native-report.json"
    subprocess.run([sys.executable, str(SKILL / driver), str(source), "--output", str(workspace / "out/diagram.lucid"), "--document-json", str(workspace / "out/document.json"), "--report", str(workspace / "out" / report)], check=True)
    print(f"Fixture package passed: {case}")
