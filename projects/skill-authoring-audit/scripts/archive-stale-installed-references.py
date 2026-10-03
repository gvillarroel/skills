#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Preserve retired, invalid local references outside the canonical installation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RETIRED = (
    "plantuml-colorset-renderer/references/code-assistant-logo-sources.md",
    "plantuml-colorset-renderer/references/logo-variants.md",
    "slidev-echarts/references/video-generation.md",
    "video/references/manim-composition-config.md",
    "video/references/manim-svg-import.md",
    "video/references/manim-visual-tokens.md",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    archive = ROOT / "projects/skill-authoring-audit/artifacts/installation-archive/20261002"
    records = []
    spec = importlib.util.spec_from_file_location("installed_reference_checker", ROOT / "skills/repository-reviewer-creator/scripts/check_skill_authoring.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    retired = set(RETIRED)
    for skill in sorted((ROOT / ".agents/skills").iterdir()):
        if not skill.is_dir() or not (ROOT / "skills" / skill.name / "SKILL.md").is_file():
            continue
        for issue in checker.check_skill(skill)["issues"]:
            relative = f"{skill.name}/{issue['path']}"
            if issue["code"] == "reference-route" and not (ROOT / "skills" / relative).exists():
                retired.add(relative)
    for relative in sorted(retired):
        source = ROOT / ".agents/skills" / relative
        target = archive / relative
        if not source.exists():
            continue
        if not source.resolve().is_relative_to(ROOT) or not target.resolve().is_relative_to(ROOT):
            raise ValueError("Archive paths must remain inside the authorized workspace")
        if (ROOT / "skills" / relative).exists():
            raise ValueError(f"Reference is still canonical: {relative}")
        original_hash = digest(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != original_hash:
            raise ValueError(f"Archive collision: {relative}")
        shutil.copy2(source, target)
        if digest(target) != original_hash:
            raise ValueError(f"Archive integrity failed: {relative}")
        if (ROOT / "skills" / relative).exists() or digest(source) != original_hash:
            raise ValueError(f"Installation or canonical source changed during archive: {relative}")
        source.unlink()
        records.append({"path": relative, "sha256": original_hash, "archive": target.relative_to(ROOT).as_posix(), "reason": "Retired noncanonical reference fails direct runtime navigation; original bytes preserved."})
    archive.mkdir(parents=True, exist_ok=True)
    manifest = archive / "manifest.json"
    previous = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    manifest.write_text(json.dumps(previous + records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"archivedReferences": len(records), "records": records}, indent=2))


if __name__ == "__main__":
    main()
