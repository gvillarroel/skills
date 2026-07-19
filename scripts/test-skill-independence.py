#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0.2",
# ]
# ///

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def load_validator(repo_root: Path):
    path = repo_root / "scripts" / "validate-skills.py"
    spec = importlib.util.spec_from_file_location("skills_repo_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def messages(findings: list[object]) -> list[str]:
    return [str(getattr(finding, "message")) for finding in findings]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    validator = load_validator(repo_root)

    with tempfile.TemporaryDirectory(prefix="skill-independence-") as temp_dir:
        root = Path(temp_dir)
        skill = root / ".agents" / "skills" / "alpha-skill"
        (root / ".agents" / "skills" / "beta-skill").mkdir(parents=True)
        write(
            skill / "SKILL.md",
            "---\nname: alpha-skill\ndescription: Test fixture.\n---\n\n"
            "Read [local guidance](references/local.md).\n"
            "Run `skills/alpha-skill/scripts/run.py`.\n",
        )
        write(
            skill / "references" / "local.md",
            "# Local guidance\n\n"
            "A plugin may expose conceptual skills/hooks/MCP modules without naming a skill path.\n\n"
            "```js\nconst value = rows.map(d => scales[0](d));\n```\n",
        )
        write(
            skill / "scripts" / "run.py",
            "from pathlib import Path\nSKILL_ROOT = Path(__file__).resolve().parents[1]\n",
        )

        clean_findings: list[object] = []
        validator.validate_skill_independence(skill, root, clean_findings)
        if clean_findings:
            print(f"Clean fixture failed: {messages(clean_findings)}", file=sys.stderr)
            return 1

        write(
            skill / "references" / "bad.md",
            "Use `skills/beta-skill/scripts/run.py`.\n"
            "Read [outside](../../../AGENTS.md), [missing](missing.md), and `assets/missing.json`.\n",
        )
        write(
            skill / "scripts" / "escape.py",
            "from pathlib import Path\nREPO_ROOT = Path(__file__).resolve().parents[4]\n",
        )
        write(
            skill / "assets" / "examples" / "demo" / "package.json",
            '{"scripts":{"render":"node ../../../../../../projects/demo/scripts/render.mjs"}}\n',
        )

        bad_findings: list[object] = []
        validator.validate_skill_independence(skill, root, bad_findings)
        observed = "\n".join(messages(bad_findings))
        expected_fragments = [
            "direct path to sibling skill 'beta-skill'",
            "Markdown link must stay inside the skill bundle",
            "Markdown link target does not exist inside the skill bundle",
            "referenced local resource does not exist inside the skill bundle",
            "derives a path above its own bundle",
            "acceptance fixture package scripts must not execute project-level scripts",
        ]
        missing = [fragment for fragment in expected_fragments if fragment not in observed]
        if missing:
            print(f"Negative fixture missed findings: {missing}\nObserved:\n{observed}", file=sys.stderr)
            return 1

    print("Skill independence validator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
