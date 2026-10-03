#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record owned source touches and the standalone runtime dependency closure."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evaluations/colorset-audit/compositions-20261002.json"
data = json.loads(DEST.read_text())
touched = {entry["path"] for entry in json.loads((ROOT / "projects/compositions-colorset-audit/artifacts/manifests/token-migration.json").read_text())}
names = ["compose-synchronized-svg", "diagram-composition", "hierarchy-lens", "usefulcharts-style", "video", "manim-svg-video"]
for name in names:
    touched |= {f"skills/{name}/{path}" for path in ["SKILL.md", "references/palette-policy.md", "assets/palettes/colorsets.json"]}
for name in names:
    if name != "hierarchy-lens":
        touched.add(f"skills/{name}/scripts/palette_contract.py")
manual = {
    "compose-synchronized-svg": [
        "scripts/compile_synchronized_svg_plan.py", "scripts/theme_contract.py", "scripts/scaffold_synchronized_svg.py",
        "scripts/compose_synchronized_svg.py", "scripts/replace_svg_module.py", "scripts/validate_synchronized_svg.py",
        "scripts/test_synchronized_svg_tools.py", "scripts/test_theme_contract.py", "scripts/test_svg_themes.py", "scripts/test_svg_text_pairs.py",
        "references/color-and-visual-quality.md", "references/spatial-world-and-camera.md",
        "assets/examples/compose-synchronized-svg/index.html", "assets/examples/compose-synchronized-svg/inference-pulse.svg", "assets/examples/compose-synchronized-svg/heatwave-tree.svg",
    ],
    "diagram-composition": ["scripts/compose_diagram.py", "scripts/build_panels.py", "scripts/visual_quality.py"],
    "hierarchy-lens": ["assets/templates/explorer.html", "assets/templates/pixels.html", "assets/templates/decision-ui.js", "scripts/audit_decisions.py", "scripts/audit_pixels.py",
        "assets/examples/hierarchy-lens/index.html", "assets/examples/hierarchy-lens/analytical.html", "assets/examples/hierarchy-lens/radial.html", "assets/examples/hierarchy-lens/organic.html"],
    "usefulcharts-style": ["scripts/render_chart.py", "scripts/create_panel_poster.py", "scripts/editorial_art.py", "scripts/editorial_poster.py", "assets/examples/usefulcharts-style/poster_briefs.py", "assets/examples/usefulcharts-style/index.html"],
    "video": ["scripts/validate_scene_contract.py", "assets/examples/ai-concept-videos/index.html", "assets/examples/ai-concept-videos/renderer.js", "assets/examples/ai-concept-videos/scenes/llm-mechanism.js"],
    "manim-svg-video": ["scripts/compose_svg_video.py", "references/composition-config.md"],
}
for name, paths in manual.items():
    touched |= {f"skills/{name}/{path}" for path in paths}
for name in ["diagram-composition", "usefulcharts-style", "video"]:
    touched |= {path.relative_to(ROOT).as_posix() for path in (ROOT / "skills" / name / "scripts").glob("test_*.py")}
for path in (ROOT / "skills/usefulcharts-style/assets/templates").glob("*.json"):
    if json.loads(path.read_text()).get("groups"):
        touched.add(path.relative_to(ROOT).as_posix())
for stem in ["atlas-of-inquiry", "aurelian-families", "five-regional-histories"]:
    touched |= {f"skills/usefulcharts-style/assets/examples/usefulcharts-style/{stem}.{extension}" for extension in ["svg", "html", "json"]}
touched.add("skills/usefulcharts-style/assets/examples/usefulcharts-style/manifest.json")
touched = {path for path in touched if (ROOT / path).is_file()}
for entry in data["skills"]:
    prefix = f"skills/{entry['skill']}/"
    entry["touchedPaths"] = sorted(path for path in touched if path.startswith(prefix))
    bundle = ROOT / "skills" / entry["skill"]
    entry["runtimeDependencyClosure"] = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path.read_bytes()).hexdigest()}
        for path in sorted(bundle.rglob("*")) if path.is_file()
        and not any(part in {"node_modules", "__pycache__", ".venv", "examples"} for part in path.relative_to(bundle).parts)
        and (path.relative_to(bundle).parts[0] in {"agents", "references", "scripts", "assets"} or path.name == "SKILL.md")
    ]
data["touchedPaths"] = sorted(touched)
data["touchedPathsNote"] = "Explicit canonical source files edited by this audit, including test-fixture rewrite sweeps that can leave identical bytes. These files can also contain pre-existing uncommitted authoring work; this list does not claim exclusive diff ownership. No Hyperframes source mutation was required."
data["dependencyClosureNote"] = "Exact standalone runtime payload paths and hashes; excludes assets/examples, node_modules, __pycache__ and environment folders. Copy these dependencies explicitly if the detached release checkout lacks pre-existing uncommitted runtime resources. No sibling bundle or repository-root runtime reading is required."
data["durableAuditPaths"] = ["evaluations/colorset-audit/compositions-20261002.md", "evaluations/colorset-audit/compositions-20261002.json"] + sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "evaluations/colorset-audit/prompts").glob("*.md"))
DEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"manifest": str(DEST), "touchedPaths": len(touched), "runtimeClosureFiles": {entry["skill"]: len(entry["runtimeDependencyClosure"]) for entry in data["skills"]}}, indent=2))
