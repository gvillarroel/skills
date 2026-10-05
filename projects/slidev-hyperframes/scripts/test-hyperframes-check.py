#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run deterministic checks against the shipped HyperFrames deck checker."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills/slidev-echarts"
ARTIFACTS = ROOT / "projects/slidev-hyperframes/artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
tests = []


def run(deck, accepted, *flags):
    process = subprocess.run(["uv", "run", "--script", str(SKILL / "scripts/check_hyperframes_deck.py"), "--deck", str(deck), *flags], text=True, capture_output=True, check=False)
    report = json.loads(process.stdout)
    assert report["accepted"] is accepted, report
    assert process.returncode == (0 if accepted else 2), process
    tests.append({"accepted": accepted, "errors": report["errors"], "flags": flags})


with tempfile.TemporaryDirectory(prefix="checker-", dir=ARTIFACTS) as temporary:
    deck = Path(temporary)
    shutil.copytree(SKILL / "assets/templates/slidev-hyperframes", deck, dirs_exist_ok=True)
    package = {"type": "module", "dependencies": {"@slidev/cli": "52.16.0", "@hyperframes/player": "0.8.134", "vue": "3.5.38", "@slidev/theme-default": "0.25.0"}, "scripts": {"build": "slidev build"}}
    (deck / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (deck / "slides.md").write_text("---\ntheme: default\n---\n\n# Mechanism\n", encoding="utf-8")
    run(deck, True, "--require-bundled-runtime")
    run(deck, False, "--direct-open")
    package["scripts"]["build:html"] = "node scripts/build-hyperframes-html.ts"
    package["devDependencies"] = {"vite-plugin-singlefile": "2.3.3"}
    (deck / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (deck / "vite.config.ts").write_text("import {viteSingleFile} from 'vite-plugin-singlefile'", encoding="utf-8")
    run(deck, True, "--direct-open", "--require-bundled-runtime")
    component = deck / "components/HyperframeSlide.vue"
    original = component.read_bytes()
    component.write_bytes(b"")
    run(deck, False)
    component.write_bytes(original + b"\n")
    run(deck, False, "--require-bundled-runtime")
    component.write_bytes(original)
    package["dependencies"]["@hyperframes/player"] = "^0.8.134"
    (deck / "package.json").write_text(json.dumps(package), encoding="utf-8")
    run(deck, False)
    package["dependencies"]["@hyperframes/player"] = "0.8.134"
    package["dependencies"].pop("@slidev/theme-default")
    package["dependencies"]["slidev-theme-custom"] = "1.0.0"
    (deck / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (deck / "slides.md").write_text("---\ntheme: custom\n---\n\n# Mechanism\n", encoding="utf-8")
    run(deck, True)
    (deck / "slides.md").write_text("---\ntheme: missing\n---\n\n# Mechanism\n", encoding="utf-8")
    run(deck, False)
    (deck / "slides.md").write_text("---\ntheme: none\n---\n\n# Mechanism\n", encoding="utf-8")
    run(deck, True)
    (deck / "package.json").write_text("invalid", encoding="utf-8")
    run(deck, False)

report = {"accepted": True, "tests": len(tests), "cases": tests}
(ARTIFACTS / "checker-tests.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({"accepted": True, "tests": len(tests)}, indent=2))
