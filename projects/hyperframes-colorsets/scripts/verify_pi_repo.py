#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify direct-repository Pi installation with native package location and discovery."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from verify_pi import (
    EXPECTED_SKILLS as PLUGIN_SKILLS,
    EXPECTED_VERSION,
    NativeRun,
    PROJECT,
    digest,
    parse_json,
    require,
    resolve_pi_host,
    save_json,
    snapshot_global_settings,
    snapshot_source,
)


REPOSITORY = PROJECT.parents[1]
PLUGIN_RELATIVE = Path("projects/hyperframes-colorsets/plugin")
SDK_HELPER = Path(__file__).with_name("discover_pi_repo.ts")
DEFAULT_SOURCE = "git:github.com/gvillarroel/skills"
EXPECTED_SKILL_DECLARATION = ["./skills", "./projects/hyperframes-colorsets/plugin/skills"]


def source_snapshot() -> dict:
    return {"project": snapshot_source(),
            "rootManifest": digest(REPOSITORY / "package.json") if (REPOSITORY / "package.json").is_file() else None}


def skill_names(root: Path) -> set[str]:
    names = set()
    for file in sorted(root.glob("*/SKILL.md")):
        match = re.search(r"^name:\s*[\"']?([a-z0-9-]+)[\"']?\s*(?:#.*)?$",
                          file.read_text(encoding="utf-8"), re.MULTILINE)
        require(match, f"Cannot read native skill name from {file}")
        require(match.group(1) not in names, f"Duplicate source skill name: {match.group(1)}")
        names.add(match.group(1))
    return names


def payload_snapshot(root: Path) -> dict[str, str]:
    files = [root / "package.json"]
    for directory in (root / "skills", root / PLUGIN_RELATIVE):
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and not {".git", "node_modules", "__pycache__"}.intersection(path.relative_to(root).parts))
    paths = sorted(files)
    with ThreadPoolExecutor(max_workers=8) as pool:
        hashes = pool.map(digest, paths)
        return {path.relative_to(root).as_posix(): value for path, value in zip(paths, hashes)}


def sdk_probe(run: NativeRun, node: str, host: Path, mode: str, label: str) -> dict:
    output = run.command(label, [node, "--experimental-strip-types", str(SDK_HELPER), str(host),
                                 str(run.workspace), str(run.agent_dir), mode]).stdout
    result = parse_json(output)
    require(isinstance(result, dict), f"{label} did not return an object")
    return result


def verify(run: NativeRun, source: str, expected_head: str | None) -> dict:
    node, cli, wrapper = resolve_pi_host()
    host = cli.parents[2]
    node_version = run.command("node-version", [node, "--version"]).stdout.strip()
    require(node_version.startswith("v24."), f"Node.js 24 is required: {node_version}")
    version = run.command("pi-version", [node, str(cli), "--version"]).stdout.strip()
    require(version == "1.4.0", f"Unexpected Pi version: {version}")
    run.command("pi-install-repo", [node, str(cli), "install", "--local", source, "--approve"], timeout=900)
    listing = run.command("pi-list", [node, str(cli), "list", "--approve"]).stdout
    location = sdk_probe(run, node, host, "locate", "pi-package-location")
    installed_root = Path(location["installedPath"]).resolve()
    configured = location.get("configuredPackages", [])
    require(len(configured) == 1 and configured[0].get("scope") == "project", "Unexpected native package scope")
    require(str(installed_root) in listing or installed_root.as_posix() in listing,
            "Native pi list did not show the resolved installed package")
    local_source = not source.startswith("git:")
    if local_source:
        require(installed_root == Path(source).expanduser().resolve(), "Native Pi resolved a different local source")
    else:
        require(installed_root.is_relative_to(run.root), "Native Git install escaped the isolated run")
        require((installed_root / ".git").exists(), "Native Git installation has no Git metadata")
    manifest_file = installed_root / "package.json"
    require(manifest_file.is_file(), "Installed repository lacks its native Pi root manifest")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    require(manifest.get("pi", {}).get("skills") == EXPECTED_SKILL_DECLARATION,
            "Installed root manifest does not expose both canonical and HyperFrames skills")
    for kind in ("extensions", "prompts", "themes"):
        require(manifest.get("pi", {}).get(kind) == [], f"Unexpected executable or ambient Pi resource: {kind}")
    canonical = skill_names(installed_root / "skills")
    git = shutil.which("git")
    require(git, "Git is not installed")
    tracked = run.command("source-committed-skills", [git, "-C", str(REPOSITORY), "ls-tree", "-d",
                                                     "--name-only", "HEAD:skills"]).stdout.splitlines()
    # Ignore unrelated untracked skill drafts in the author's working tree.
    expected_canonical = {name for name in tracked if (REPOSITORY / "skills" / name / "SKILL.md").is_file()}
    require(expected_canonical, "The committed canonical skill baseline is empty")
    require(canonical == expected_canonical,
            f"Canonical skills changed: missing={sorted(expected_canonical-canonical)}, extra={sorted(canonical-expected_canonical)}")
    plugin_root = installed_root / PLUGIN_RELATIVE
    require(skill_names(plugin_root / "skills") == PLUGIN_SKILLS, "Installed repository is missing plugin skills")
    before_payload = payload_snapshot(installed_root)
    run.command("pi-reinstall-repo", [node, str(cli), "install", "--local", source, "--approve"], timeout=900)
    repeated_location = sdk_probe(run, node, host, "locate", "pi-reinstalled-package-location")
    require(repeated_location["configuredPackages"] == configured and
            Path(repeated_location["installedPath"]).resolve() == installed_root,
            "Native reinstall duplicated or changed the configured package")
    discovery = sdk_probe(run, node, host, "discover", "pi-sdk-discovery")
    skills = discovery.get("skills", [])
    expected_names = canonical | PLUGIN_SKILLS
    require(len(skills) == len(expected_names) and {item["name"] for item in skills} == expected_names,
            "Native Pi did not discover all canonical and HyperFrames skills exactly once")
    for field in ("diagnostics", "extensionErrors", "promptDiagnostics", "themeDiagnostics"):
        require(discovery.get(field) == [], f"Native Pi reported resource diagnostics: {field}")
    for field in ("extensionCount", "promptCount", "themeCount", "contextFileCount"):
        require(discovery.get(field) == 0, f"Native Pi loaded ambient resources: {field}")
    plugin_skill_root = plugin_root / "skills"
    canonical_skill_root = installed_root / "skills"
    for item in skills:
        path = Path(item["filePath"]).resolve()
        expected_root = plugin_skill_root if item["name"] in PLUGIN_SKILLS else canonical_skill_root
        require(path.is_relative_to(expected_root) and path.is_file(), "Native Pi loaded a skill outside its declared bundle")
        relative = path.relative_to(installed_root)
        require(relative.as_posix() in before_payload and digest(path) == before_payload[relative.as_posix()],
                "Native Pi changed a discovered skill")
    runner = plugin_root / "skills" / "hyperframes" / "scripts" / "plugin-cli.mjs"
    require(runner.is_file() and digest(runner) == digest(PROJECT / "plugin" / runner.relative_to(plugin_root)),
            "Installed original HyperFrames launcher differs from the source bundle")
    runtime_version = run.command("installed-runner-version", [node, str(runner), "--version"], timeout=240).stdout.strip()
    require(runtime_version == EXPECTED_VERSION, f"Installed launcher resolved a different release: {runtime_version}")
    presets = []
    for mode, filename in (("colorset1", "colorset1.yml"), ("colorset2", "colorset2.yaml")):
        for leaf in ("FRAME.md", filename):
            relative = Path("skills/colorsets/assets") / mode / leaf
            copied = plugin_root / relative
            require(copied.is_file() and digest(copied) == digest(PROJECT / "plugin" / relative),
                    f"Installed style resource differs: {relative}")
            presets.append({"path": (PLUGIN_RELATIVE / relative).as_posix(), "sha256": digest(copied)})
    git_evidence = None
    if not local_source:
        commit = run.command("installed-git-head", [git, "-C", str(installed_root), "rev-parse", "HEAD"]).stdout.strip()
        origin = run.command("installed-git-origin", [git, "-C", str(installed_root), "remote", "get-url", "origin"]).stdout.strip()
        require(re.fullmatch(r"[0-9a-f]{40}", commit), "Native clone did not expose a full Git commit")
        require("github.com/gvillarroel/skills" in origin.replace(":gvillarroel", "/gvillarroel"),
                f"Native Git clone has an unexpected remote: {origin}")
        if expected_head:
            require(commit == expected_head, "Native clone resolved a different Git commit")
        git_evidence = {"head": commit, "origin": origin}
    require(payload_snapshot(installed_root) == before_payload, "Installed payload changed after discovery or launcher execution")
    return {"source": source, "sourceKind": "local-prepush" if local_source else "native-git",
            "piVersion": version, "nodeVersion": node_version, "hyperframesVersion": runtime_version,
            "piHostRoot": str(host), "piCli": str(cli), "piWrapper": str(wrapper),
            "packageRoot": str(installed_root), "installedRoot": str(plugin_root),
            "configuredPackages": configured, "canonicalSkillCount": len(canonical),
            "canonicalSkills": sorted(canonical), "pluginSkills": sorted(PLUGIN_SKILLS),
            "discovery": discovery, "installedPayloadUnchanged": True, "installedPayloadFileCount": len(before_payload),
            "git": git_evidence, "presets": presets, "modelCalls": 0, "skillCommand": "/skill:colorsets",
            "limitations": ["Discovery uses the native SDK on the package located by the native settings and package manager.",
                            "No agent session, auth store or model call is constructed; video quality is not evaluated."] +
                           (["This local-source run does not prove remote Git installation; run the default source after publication."]
                            if local_source else [])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_SOURCE,
                        help="Native Pi source; default is git:github.com/gvillarroel/skills; local paths support prepush checks")
    parser.add_argument("--expected-head", help="Optional full commit required from the native remote clone")
    parser.add_argument("--output-dir", type=Path, default=PROJECT / "artifacts" / "pi-repo")
    args = parser.parse_args(argv)
    output = args.output_dir.expanduser().resolve()
    require(output.is_relative_to(REPOSITORY), "Evidence must remain inside the repository")
    source = args.source if args.source.startswith("git:") else str(Path(args.source).expanduser().resolve())
    if args.expected_head:
        require(re.fullmatch(r"[0-9a-f]{40}", args.expected_head), "--expected-head requires a full commit SHA")
    before_source = source_snapshot()
    before_settings = snapshot_global_settings()
    run = NativeRun(output)
    run.env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never", GIT_CONFIG_NOSYSTEM="1",
                   GIT_CONFIG_GLOBAL=str(run.root / "gitconfig"))
    git_config = "[core]\n\tlongpaths = true\n" if os.name == "nt" else ""
    (run.root / "gitconfig").write_text(git_config, encoding="utf-8")
    report = {"ok": False, "source": source, "runDirectory": str(run.root),
              "agentDirectory": str(run.agent_dir), "workspace": str(run.workspace), "modelCalls": 0}
    try:
        report.update(verify(run, source, args.expected_head))
        report["ok"] = True
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        report["error"] = str(error)
    finally:
        report["sourceBundleUnchanged"] = source_snapshot() == before_source
        report["globalPiSettingsUnchanged"] = snapshot_global_settings() == before_settings
        if not report["sourceBundleUnchanged"] or not report["globalPiSettingsUnchanged"]:
            report["ok"] = False
            report["integrityError"] = "Source bundle or global Pi settings changed during verification"
        report["commands"] = run.commands
        save_json(run.root / "report.json", report)
    print(json.dumps({"ok": report["ok"], "report": str(run.root / "report.json"),
                      "sourceKind": report.get("sourceKind"), "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
