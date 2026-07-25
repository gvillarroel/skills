#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0.2",
# ]
# ///

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


ROOT_IGNORE_DIRS = {
    ".agents",
    ".git",
    ".github",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "docs",
    "evaluations",
    "examples",
    "node_modules",
    "output",
    "results",
    "scripts",
    "videos",
}
SKILL_ALLOWED_DIRS = {"agents", "assets", "references", "scripts"}
DISALLOWED_SKILL_DOCS = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXAMPLE_ID_RE = SKILL_NAME_RE
MAX_SKILL_NAME_LENGTH = 64
INDEPENDENCE_TEXT_SUFFIXES = {".md", ".py", ".ts", ".js", ".mjs", ".cjs", ".json", ".yaml", ".yml", ".toml"}
INDEPENDENCE_IGNORED_DIRS = {"__pycache__", "node_modules"}
DIRECT_SKILL_PATH_RE = re.compile(
    r"(?i)(?P<prefix>(?<![.a-z0-9_-])skills)[\\/](?P<skill>[a-z0-9]+(?:-[a-z0-9]+)*)"
)
SCRIPT_ROOT_ESCAPE_RE = re.compile(
    r"Path\(\s*__file__\s*\)\.resolve\(\)\.parents\[(?P<level>\d+)\]"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\((?P<target><[^>]+>|[^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
LOCAL_RESOURCE_PATH_RE = re.compile(
    r"`(?P<target>(?:assets|references|scripts)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*/?)`"
)
FIXTURE_EXTERNAL_SCRIPT_RE = re.compile(
    r"(?i)(?:\.\.[\\/])*(?:projects)[\\/][^\"'\s]+[\\/]scripts[\\/]"
)


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
    validate_script_tree(skill_dir / "scripts", root, findings, dependency_root=skill_dir)
    validate_skill_independence(skill_dir, root, findings)


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


def validate_typescript_script(script: Path, dependency_root: Path, findings: list[Finding]) -> None:
    content = script.read_text(encoding="utf-8")
    lines = content.splitlines()
    first_line = lines[0] if lines else ""
    has_runner = first_line.startswith("#!") and ("tsx" in first_line or "ts-node" in first_line)
    has_run_comment = re.search(r"^//\s*Run:\s*", content, re.MULTILINE) is not None
    has_dependencies = has_nearby_package_json(script, dependency_root) or re.search(r"^//\s*Dependencies:\s*", content, re.MULTILINE) is not None

    if not has_runner and not has_run_comment:
        add(findings, script, "TypeScript scripts must include a tsx/ts-node shebang or // Run: header")
    if not has_dependencies:
        add(findings, script, "TypeScript script dependencies must be declared in package.json or a // Dependencies: header")


def validate_script_tree(
    script_dir: Path,
    root: Path,
    findings: list[Finding],
    *,
    dependency_root: Path | None = None,
) -> None:
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
            validate_typescript_script(script, dependency_root or root, findings)
        else:
            add(findings, script, "scripts must be TypeScript (.ts) or uv Python (.py)")


def is_runtime_independence_file(path: Path, skill_dir: Path) -> bool:
    relative_path = path.relative_to(skill_dir)
    if any(part in INDEPENDENCE_IGNORED_DIRS for part in relative_path.parts):
        return False
    if relative_path.parts[:2] == ("assets", "examples"):
        return False
    return path.is_file() and path.suffix.lower() in INDEPENDENCE_TEXT_SUFFIXES


def markdown_target_path(target: str) -> str | None:
    value = target.strip().strip("<>")
    if not value or value.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", value, flags=re.IGNORECASE):
        return None
    value = value.split("#", 1)[0].split("?", 1)[0]
    if not value or "<" in value or ">" in value:
        return None
    return value


def validate_markdown_links(path: Path, skill_dir: Path, content: str, findings: list[Finding]) -> None:
    prose = re.sub(r"^\s*```.*?^\s*```\s*$", "", content, flags=re.MULTILINE | re.DOTALL)
    for match in MARKDOWN_LINK_RE.finditer(prose):
        target = markdown_target_path(match.group("target"))
        if target is None:
            continue
        candidate = (path.parent / target.replace("\\", "/")).resolve()
        try:
            candidate.relative_to(skill_dir.resolve())
        except ValueError:
            add(findings, path, f"Markdown link must stay inside the skill bundle: {target}")
            continue
        if not candidate.exists():
            add(findings, path, f"Markdown link target does not exist inside the skill bundle: {target}")


def validate_local_resource_paths(path: Path, skill_dir: Path, content: str, findings: list[Finding]) -> None:
    for match in LOCAL_RESOURCE_PATH_RE.finditer(content):
        target = match.group("target")
        candidate = skill_dir / target
        if not candidate.exists():
            add(findings, path, f"referenced local resource does not exist inside the skill bundle: {target}")


def validate_skill_independence(skill_dir: Path, root: Path, findings: list[Finding]) -> None:
    skill_name = skill_dir.name
    known_skill_names = {path.name for path in skill_dir.parent.iterdir() if path.is_dir()}
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            try:
                path.resolve().relative_to(skill_dir.resolve())
            except ValueError:
                add(findings, path, "symbolic link must resolve inside its owning skill bundle")
                continue
        relative_path = path.relative_to(skill_dir)
        if path.is_file() and path.name == "package.json" and relative_path.parts[:2] == ("assets", "examples"):
            try:
                fixture_manifest = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                fixture_manifest = ""
            if FIXTURE_EXTERNAL_SCRIPT_RE.search(fixture_manifest):
                add(
                    findings,
                    path,
                    "acceptance fixture package scripts must not execute project-level scripts outside the skill bundle",
                )
        if not is_runtime_independence_file(path, skill_dir):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for match in DIRECT_SKILL_PATH_RE.finditer(content):
            target_skill = match.group("skill")
            if target_skill != skill_name and target_skill in known_skill_names:
                add(
                    findings,
                    path,
                    f"runtime payload must not use a direct path to sibling skill '{target_skill}'",
                )

        if skill_dir / "scripts" in path.parents:
            for match in SCRIPT_ROOT_ESCAPE_RE.finditer(content):
                level = int(match.group("level"))
                if level >= 2:
                    add(
                        findings,
                        path,
                        "skill script derives a path above its own bundle from __file__; use the skill root, cwd, or an explicit input",
                    )

        if path.suffix.lower() == ".md":
            validate_markdown_links(path, skill_dir, content, findings)
            validate_local_resource_paths(path, skill_dir, content, findings)


def load_build_pages_module(root: Path):
    script = root / "scripts" / "build-pages.py"
    if not script.exists():
        return None, "scripts/build-pages.py is required"

    spec = importlib.util.spec_from_file_location("skills_repo_build_pages", script)
    if spec is None or spec.loader is None:
        return None, "could not load scripts/build-pages.py"

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        return None, f"could not import scripts/build-pages.py: {error}"
    return module, None


def validate_pattern_id_registry(root: Path, findings: list[Finding]) -> None:
    script = root / "scripts" / "validate-pattern-ids.py"
    if not script.exists():
        add(findings, script, "scripts/validate-pattern-ids.py is required")
        return

    spec = importlib.util.spec_from_file_location("skills_repo_pattern_ids", script)
    if spec is None or spec.loader is None:
        add(findings, script, "could not load scripts/validate-pattern-ids.py")
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        pattern_findings, _ = module.validate_pattern_ids(root)
    except Exception as error:
        add(findings, script, f"could not validate pattern IDs: {error}")
        return
    finally:
        sys.modules.pop(spec.name, None)

    for finding in pattern_findings:
        add(findings, finding.path, finding.message)


def validate_example_catalog(root: Path, findings: list[Finding]) -> None:
    build_pages, error = load_build_pages_module(root)
    script = root / "scripts" / "build-pages.py"
    if error:
        add(findings, script, error)
        return

    sources = getattr(build_pages, "EXAMPLE_SOURCES", None)
    published = getattr(build_pages, "PUBLISHED_EXAMPLE_SETS", None)
    unlisted = getattr(build_pages, "UNLISTED_EXAMPLE_SOURCES", set())

    if not isinstance(sources, dict):
        add(findings, script, "EXAMPLE_SOURCES must be a mapping")
        return
    if not isinstance(published, list):
        add(findings, script, "PUBLISHED_EXAMPLE_SETS must be a list")
        return
    if not isinstance(unlisted, set):
        add(findings, script, "UNLISTED_EXAMPLE_SOURCES must be a set")
        return

    source_names = set(sources)
    published_ids: set[str] = set()
    published_sources: set[str] = set()
    published_hrefs: set[str] = set()
    required_fields = {"id", "source", "title", "href", "kind", "description"}

    for index, card in enumerate(published, start=1):
        if not isinstance(card, dict):
            add(findings, script, f"PUBLISHED_EXAMPLE_SETS entry {index} must be a mapping")
            continue

        missing = sorted(required_fields - set(card))
        if missing:
            add(findings, script, f"PUBLISHED_EXAMPLE_SETS entry {index} is missing: {', '.join(missing)}")
            continue

        example_id = card.get("id")
        source = card.get("source")
        href = card.get("href")
        title = card.get("title")
        kind = card.get("kind")
        description = card.get("description")

        if not isinstance(example_id, str) or not EXAMPLE_ID_RE.fullmatch(example_id):
            add(findings, script, f"PUBLISHED_EXAMPLE_SETS entry {index} id must be lowercase hyphen-case")
        elif example_id in published_ids:
            add(findings, script, f"duplicate published example id: {example_id}")
        else:
            published_ids.add(example_id)

        if not isinstance(source, str) or source not in sources:
            add(findings, script, f"PUBLISHED_EXAMPLE_SETS entry {index} source must match EXAMPLE_SOURCES")
        else:
            published_sources.add(source)
            source_path = sources[source]
            if not isinstance(source_path, Path):
                add(findings, script, f"EXAMPLE_SOURCES['{source}'] must be a Path")
            elif not source_path.exists():
                add(findings, source_path, "published example source path does not exist")

        if not isinstance(href, str) or not href.startswith("examples/") or not href.endswith("/"):
            add(findings, script, f"PUBLISHED_EXAMPLE_SETS entry {index} href must be an examples/.../ directory URL")
        elif href in published_hrefs:
            add(findings, script, f"duplicate published example href: {href}")
        else:
            published_hrefs.add(href)

        for field_name, value in {"title": title, "kind": kind, "description": description}.items():
            if not isinstance(value, str) or not value.strip():
                add(findings, script, f"PUBLISHED_EXAMPLE_SETS entry {index} {field_name} must be a non-empty string")

    unknown_unlisted = sorted(unlisted - source_names)
    if unknown_unlisted:
        add(findings, script, f"UNLISTED_EXAMPLE_SOURCES contains unknown sources: {', '.join(unknown_unlisted)}")

    missing_from_main_page = sorted(source_names - published_sources - unlisted)
    if missing_from_main_page:
        add(
            findings,
            script,
            "publishable example sources must be listed in PUBLISHED_EXAMPLE_SETS: "
            + ", ".join(missing_from_main_page),
        )


def skills_root(root: Path) -> Path:
    return root / "skills"


def skill_directories(root: Path) -> Iterable[Path]:
    container = skills_root(root)
    if not container.exists():
        return
    for child in sorted(container.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            yield child


def validate_repo(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    if not (root / "AGENTS.md").exists():
        add(findings, root / "AGENTS.md", "AGENTS.md is required")
    if not (root / "SKILLS.md").exists():
        add(findings, root / "SKILLS.md", "SKILLS.md backlog is required")
    if not skills_root(root).exists():
        add(findings, skills_root(root), "skills root skills is required")

    validate_script_tree(root / "scripts", root, findings)
    validate_example_catalog(root, findings)
    validate_pattern_id_registry(root, findings)

    for child in root.iterdir():
        if child.is_dir() and (child / "SKILL.md").exists():
            add(findings, child, "skill directories must live under skills")

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
