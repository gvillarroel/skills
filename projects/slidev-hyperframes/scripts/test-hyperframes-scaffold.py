#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic, isolated scaffold and boundary regressions; no dependency installs."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/slidev-hyperframes/artifacts/scaffold-tests"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file()}


def main():
    checks = []
    canonical = ROOT / "skills/slidev-echarts"
    companion = ROOT / "skills/slidev-animejs"
    for relative in ("assets/templates/slidev-hyperframes/components/HyperframePreview.vue",
                     "assets/templates/slidev-hyperframes-starter", "scripts/scaffold_hyperframes_deck.py"):
        left, right = canonical / relative, companion / relative
        assert snapshot(left) == snapshot(right) if left.is_dir() else left.read_bytes() == right.read_bytes()
    checks.append("Both standalone scaffold resource copies are byte-identical")
    with tempfile.TemporaryDirectory(prefix="isolated-", dir=ARTIFACTS) as temporary:
        workspace = Path(temporary)
        skill = workspace / "skills/slidev-echarts"
        for relative in ("assets/templates/slidev-hyperframes", "assets/templates/slidev-hyperframes-starter",
                         "assets/templates/slidev-layouts", "assets/templates/slidev-diagram-style"):
            shutil.copytree(canonical / relative, skill / relative)
        (skill / "scripts").mkdir(parents=True)
        for name in ("scaffold_hyperframes_deck.py", "check_hyperframes_deck.py", "check_layout_deck.py"):
            shutil.copyfile(canonical / "scripts" / name, skill / "scripts" / name)
        before_skill = snapshot(skill)

        def run(deck="deck", config=None, success=True, review=None):
            command = [sys.executable, str(skill / "scripts/scaffold_hyperframes_deck.py"), "--deck", deck]
            if config is not None:
                (workspace / "config.json").write_text(json.dumps(config), encoding="utf-8")
                command += ["--config", "config.json"]
            if review:
                command += ["--review", review]
            result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", check=False)
            data = json.loads(result.stdout)
            assert (result.returncode == 0) == success, result.stdout + result.stderr
            assert data["accepted"] == success
            return data

        result = run()
        assert not result["installed"] and not result["built"] and not result["browserQualified"]
        required = ("slides.md", "package.json", "components/HyperframeStory.vue", "data/hyperframes-story.json",
                    "components/HyperframeSlide.vue", "lib/hyperframes.js", "public/hyperframes/starter.html", "public/hyperframes/scene.js")
        assert all((workspace / "deck" / name).is_file() for name in required)
        assert (workspace / "deliverables/hyperframes-review.md").is_file()
        checks.append("Exact requested paths and both bundled static checks pass without install/build")
        first = snapshot(workspace / "deck")
        run()
        assert first == snapshot(workspace / "deck")
        checks.append("Same-input generation is idempotent")
        run("fresh/deck")
        assert first == snapshot(workspace / "fresh/deck")
        checks.append("Identical inputs produce byte-identical decks in different directories")

        copied = workspace / "copied/deck"
        for name in ("slidev-hyperframes", "slidev-layouts"):
            shutil.copytree(skill / "assets/templates" / name, copied, dirs_exist_ok=True)
        (copied / "custom.txt").write_text("Preserve unrelated authored content", encoding="utf-8")
        run("copied/deck")
        assert (copied / "custom.txt").read_text() == "Preserve unrelated authored content"
        checks.append("Byte-identical pre-copied packs and unrelated authored files are preserved")

        config = {"titles": {"hero": "Water & energy <flow>"}, "cueTimes": [0, 3, 9], "colorset": "colorset2",
                  "compactLayout": {"mode": "masonry-columns", "columns": 1}}
        run("custom/deck", config)
        custom = json.loads((workspace / "custom/deck/data/hyperframes-story.json").read_text())
        assert custom["titles"]["hero"] == config["titles"]["hero"] and custom["cueTimes"] == [0, 3, 9]
        assert custom["colorset"] == "colorset2" and custom["compactLayout"]["columns"] == 1
        assert "{{ story.titles[variant] }}" in (workspace / "custom/deck/components/HyperframeStory.vue").read_text()
        assert config["titles"]["hero"] not in (workspace / "custom/deck/slides.md").read_text()
        assert "mermaidColorsetConfig(story.colorset)" in (workspace / "custom/deck/setup/mermaid.ts").read_text()
        checks.append("Editable JSON deep-merges; Vue renders titles as text and wires shared Mermaid defaults")

        for config in ({"colorset": "unknown"}, {"cueTimes": []}, {"cueTimes": [float("nan")]},
                       {"cueTimes": [True]}, {"titles": 5}, {"compactLayout": {"columns": 3}},
                       {"compactLayout": {"playerHeight": 151}}, {"compactLayout": {"minItemHeight": 200}},
                       {"unknown": 3}):
            run("invalid/deck", config, success=False)
            assert not (workspace / "invalid").exists()
        checks.append("Nine invalid schema/readability cases fail before writes")

        conflict = workspace / "conflict/deck"
        conflict.mkdir(parents=True)
        (conflict / "slides.md").write_text("Keep my presentation", encoding="utf-8")
        conflict_before = snapshot(conflict)
        run("conflict/deck", success=False)
        assert conflict_before == snapshot(conflict) and not (workspace / "conflict/deliverables").exists()
        checks.append("Differing authored file fails all-target preflight without partial copies")

        runtime_conflict = workspace / "runtime-conflict/deck/components"
        runtime_conflict.mkdir(parents=True)
        (runtime_conflict / "HyperframeSlide.vue").write_text("Customized existing player", encoding="utf-8")
        run("runtime-conflict/deck", success=False)
        assert snapshot(runtime_conflict.parent) == {"components/HyperframeSlide.vue": hashlib.sha256(b"Customized existing player").hexdigest()}
        checks.append("Differing existing core resource is preserved")

        run(str(workspace.parent / "outside-deck"), success=False)
        run("skills/slidev-echarts/output", success=False)
        checks.append("Outside-workspace and in-skill outputs are rejected")
        outside_config = workspace.parent / "never-read.json"
        command = [sys.executable, str(skill / "scripts/scaffold_hyperframes_deck.py"), "--deck", "outside-input/deck", "--config", str(outside_config)]
        result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", check=False)
        assert result.returncode == 2 and "leaves the current workspace" in result.stdout
        checks.append("Outside configuration path is rejected before reading")
        command += ["--review", str(workspace.parent / "outside-review.md")]
        result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", check=False)
        assert result.returncode == 2 and not (workspace / "outside-input").exists()
        checks.append("Outside review path is rejected before writes")
        assert snapshot(skill) == before_skill
        checks.append("Isolated owning bundle remains read-only and needs no sibling/repository files")

    report = {"passed": True, "checks": len(checks), "cases": checks}
    (ARTIFACTS / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
