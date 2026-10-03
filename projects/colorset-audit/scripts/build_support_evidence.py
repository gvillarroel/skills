#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record exact root-owned source paths and retained isolated evidence."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/colorset-audit/artifacts"
OUT = ROOT / "evaluations/colorset-audit"
OUT.mkdir(parents=True, exist_ok=True)
skills = ["ambientcg-material-search", "animated-svg-to-gif", "asciinema-real-command-video", "destockd-video-search", "harbor-author-evaluation-datasets", "iconify-icon-search", "kenney-asset-search", "one-bit-dither-svg", "pexels-media-search", "pixel-art-image-video", "polyhaven-asset-search", "technical-logo-assets"]
paths = {f"skills/{skill}/SKILL.md" for skill in skills}
for skill in skills:
    palette = ROOT / f"skills/{skill}/assets/palettes/colorsets.json"
    if palette.is_file():
        paths.add(palette.relative_to(ROOT).as_posix())
for skill in ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search"):
    paths.add(f"skills/{skill}/scripts/asset_io.py")
paths.update([
    "skills/animated-svg-to-gif/assets/templates/pulse.animated.svg",
    "skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py",
    "skills/animated-svg-to-gif/scripts/test_capture_colorset.py",
    "skills/asciinema-real-command-video/scripts/terminal_colorsets.py",
    "skills/asciinema-real-command-video/scripts/colorset_contract.py",
    "skills/asciinema-real-command-video/scripts/test_terminal_colorsets.py",
    "skills/asciinema-real-command-video/scripts/asciinema_command_video.py",
    "skills/asciinema-real-command-video/scripts/test_asciinema_command_video.py",
    "skills/asciinema-real-command-video/references/session-plan.md",
    "skills/asciinema-real-command-video/references/interaction-recipes.md",
    "skills/destockd-video-search/scripts/destockd.py",
    "skills/destockd-video-search/scripts/test_destockd.py",
    "skills/harbor-author-evaluation-datasets/scripts/consolidate_harbor_reports.py",
    "skills/harbor-author-evaluation-datasets/scripts/test_consolidate_harbor_reports.py",
    "skills/iconify-icon-search/scripts/iconify.py",
    "skills/iconify-icon-search/scripts/test_iconify.py",
    "skills/technical-logo-assets/scripts/export_logo_asset.py",
    "skills/technical-logo-assets/scripts/test_logo_variants.py",
    "skills/technical-logo-assets/assets/logo-audit.html",
    "skills/technical-logo-assets/references/logo-variants.md",
    "docs/colorsets.json", "docs/colorsets.md",
    "scripts/validate-colorsets.py", "scripts/test-colorsets.py", "scripts/build-pages.py", "scripts/validate-diagram-type-coverage.py", ".gitignore",
])
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "skills/asciinema-real-command-video/assets/templates").glob("*session-plan.json"))
paths.update(p.relative_to(ROOT).as_posix() for skill in ("pixel-art-image-video", "one-bit-dither-svg") for p in (ROOT / f"skills/{skill}").rglob("*") if p.is_file() and not any(part in {"__pycache__", "node_modules"} for part in p.parts))
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "evaluations/pi-prompts").glob("colorset-*.md"))
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "projects/colorset-audit/scripts").glob("*") if p.is_file())
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "projects/compositions-colorset-audit/scripts").glob("*") if p.is_file())
rows = []
for run in sorted((ROOT / "evaluations/runs").iterdir()):
    if "colorset" not in run.name or "20261002" not in run.name:
        continue
    result_path, manifest_path = run / "evaluation-result.json", run / "run-manifest.json"
    if not result_path.is_file() or not manifest_path.is_file():
        continue
    result = json.loads(result_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    if manifest["skill"]["name"] not in skills:
        continue
    artifacts = json.loads((run / "artifact-check.json").read_text())
    rows.append({"runId": run.name, "skill": manifest["skill"]["name"], "model": manifest["pi"]["model"], "payloadSha256": manifest["skill"]["payloadSha256"], "passed": result["passed"], "gates": result["gates"], "outputs": artifacts["outputs"], "command": manifest.get("command"), "durationSeconds": result.get("durationSeconds"), "startedAtUtc": result["startedAtUtc"]})
latest = {}
for row in sorted(rows, key=lambda r: r["startedAtUtc"]):
    latest[row["skill"]] = row
test_result = json.loads((ART / "data/support-tests.json").read_text())
summary = {"schemaVersion": 1, "date": "2026-10-02", "skills": skills, "finalRuns": list(latest.values()), "retainedAttempts": rows, "deterministicTests": test_result, "touchedPaths": sorted(paths), "sharedFilesRequirePaletteOnlyMerge": ["SKILLS.md", "docs/README.md", "scripts/validate-skills.py", ".github/workflows/pages.yml"], "sourceFidelity": "Provider bytes, original logos, recording evidence and explicit preserve RGB remain unchanged; authored chrome and derived paint use exact tokens.", "allFinalStrictPassed": len(latest) == len(skills) and all(row["passed"] for row in latest.values())}
(OUT / "support-20261002.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
(ART / "data/root-publication-paths.json").write_text(json.dumps(sorted(paths), indent=2) + "\n", encoding="utf-8")
print(json.dumps({"skills": len(skills), "attempts": len(rows), "finalPasses": sum(row["passed"] for row in latest.values()), "sourcePaths": len(paths)}))
