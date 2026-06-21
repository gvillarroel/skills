#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0.2",
# ]
# ///

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


ROOT_IGNORE_DIRS = {
    ".git",
    ".github",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "docs",
    "examples",
    "node_modules",
    "output",
    "scripts",
}
SKILL_ALLOWED_DIRS = {"agents", "assets", "references", "scripts"}
DISALLOWED_SKILL_DOCS = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_SKILL_NAME_LENGTH = 64


@dataclass
class Finding:
    path: Path
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def add(findings: list[Finding], path: Path, message: str) -> None:
    findings.append(Finding(path=path, message=message))


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, object] | None, str | None]:
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return None, "SKILL.md must start with YAML frontmatter"

    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
    if not match:
        return None, "SKILL.md frontmatter must be closed with ---"

    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return None, f"SKILL.md frontmatter is invalid YAML: {error}"

    if not isinstance(parsed, dict):
        return None, "SKILL.md frontmatter must be a YAML mapping"

    return parsed, None


def validate_skill_dir(skill_dir: Path, root: Path, findings: list[Finding]) -> None:
    skill_name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not SKILL_NAME_RE.fullmatch(skill_name):
        add(findings, skill_dir, "skill directory name must be lowercase hyphen-case")
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        add(findings, skill_dir, f"skill name must be {MAX_SKILL_NAME_LENGTH} characters or fewer")

    if not skill_md.exists():
        add(findings, skill_dir, "skill directory must contain SKILL.md")
        return

    frontmatter, error = parse_frontmatter(skill_md)
    if error:
        add(findings, skill_md, error)
        return

    assert frontmatter is not None
    allowed_keys = {"name", "description"}
    unexpected = sorted(set(frontmatter) - allowed_keys)
    if unexpected:
        add(findings, skill_md, f"frontmatter must contain only name and description; unexpected: {', '.join(unexpected)}")

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if name != skill_name:
        add(findings, skill_md, f"frontmatter name must match directory name '{skill_name}'")
    if not isinstance(description, str) or not description.strip():
        add(findings, skill_md, "description must be a non-empty string")
    elif len(description.strip()) > 1024:
        add(findings, skill_md, "description must be 1024 characters or fewer")
    elif "<" in description or ">" in description:
        add(findings, skill_md, "description must not contain angle brackets")

    for child in skill_dir.iterdir():
        if child.is_dir() and child.name not in SKILL_ALLOWED_DIRS:
            add(findings, child, "unexpected top-level directory inside skill")
        if child.is_file() and child.name in DISALLOWED_SKILL_DOCS:
            add(findings, child, "auxiliary documentation is not allowed inside skill directories")

    validate_agents_metadata(skill_dir, root, findings)
    validate_script_tree(skill_dir / "scripts", root, findings)


def validate_agents_metadata(skill_dir: Path, root: Path, findings: list[Finding]) -> None:
    metadata = skill_dir / "agents" / "openai.yaml"
    if not metadata.exists():
        return

    try:
        parsed = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        add(findings, metadata, f"agents/openai.yaml is invalid YAML: {error}")
        return

    if not isinstance(parsed, dict):
        add(findings, metadata, "agents/openai.yaml must be a YAML mapping")
        return

    interface = parsed.get("interface")
    if not isinstance(interface, dict):
        return

    default_prompt = interface.get("default_prompt")
    if isinstance(default_prompt, str) and f"${skill_dir.name}" not in default_prompt:
        add(findings, metadata, "interface.default_prompt should mention the skill as $skill-name")

    short_description = interface.get("short_description")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        add(findings, metadata, "interface.short_description should be 25 to 64 characters")


def validate_python_script(script: Path, findings: list[Finding]) -> None:
    content = script.read_text(encoding="utf-8")
    lines = content.splitlines()
    if not lines or lines[0] != "#!/usr/bin/env -S uv run --script":
        add(findings, script, "Python scripts must start with '#!/usr/bin/env -S uv run --script'")
    if "# /// script" not in lines or "# ///" not in lines:
        add(findings, script, "Python scripts must include uv PEP 723 script metadata")
    if "dependencies = [" not in content:
        add(findings, script, "Python scripts must declare dependencies in uv script metadata")


def has_nearby_package_json(script: Path, root: Path) -> bool:
    for directory in [script.parent, *script.parents]:
        if (directory / "package.json").exists():
            return True
        if directory == root:
            return False
    return False


def validate_typescript_script(script: Path, root: Path, findings: list[Finding]) -> None:
    content = script.read_text(encoding="utf-8")
    lines = content.splitlines()
    first_line = lines[0] if lines else ""
    has_runner = first_line.startswith("#!") and ("tsx" in first_line or "ts-node" in first_line)
    has_run_comment = re.search(r"^//\s*Run:\s*", content, re.MULTILINE) is not None
    has_dependencies = has_nearby_package_json(script, root) or re.search(r"^//\s*Dependencies:\s*", content, re.MULTILINE) is not None

    if not has_runner and not has_run_comment:
        add(findings, script, "TypeScript scripts must include a tsx/ts-node shebang or // Run: header")
    if not has_dependencies:
        add(findings, script, "TypeScript script dependencies must be declared in package.json or a // Dependencies: header")


def validate_script_tree(script_dir: Path, root: Path, findings: list[Finding]) -> None:
    if not script_dir.exists():
        return

    for script in script_dir.rglob("*"):
        if "__pycache__" in script.parts:
            continue
        if not script.is_file():
            continue
        if script.suffix == ".py":
            validate_python_script(script, findings)
        elif script.suffix == ".ts":
            validate_typescript_script(script, root, findings)
        else:
            add(findings, script, "scripts must be TypeScript (.ts) or uv Python (.py)")


def skill_directories(root: Path) -> Iterable[Path]:
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name not in ROOT_IGNORE_DIRS and not child.name.startswith("."):
            yield child


def validate_repo(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    if not (root / "AGENTS.md").exists():
        add(findings, root / "AGENTS.md", "AGENTS.md is required")
    if not (root / "SKILLS.md").exists():
        add(findings, root / "SKILLS.md", "SKILLS.md backlog is required")

    validate_script_tree(root / "scripts", root, findings)

    for skill_dir in skill_directories(root):
        validate_skill_dir(skill_dir, root, findings)

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate this skills repository.")
    parser.add_argument("--root", type=Path, default=repo_root(), help="Repository root to validate.")
    args = parser.parse_args()

    root = args.root.resolve()
    findings = validate_repo(root)

    if findings:
        print(f"Validation failed with {len(findings)} finding(s):")
        for finding in findings:
            print(f"- {relative(finding.path, root)}: {finding.message}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
