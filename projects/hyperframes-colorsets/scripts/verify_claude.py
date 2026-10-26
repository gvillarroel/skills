#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify native Claude plugin installation with isolated state and no model calls."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid


PROJECT = Path(__file__).resolve().parents[1]
PLUGIN = PROJECT / "plugin"
MARKETPLACE = PROJECT / ".claude-plugin" / "marketplace.json"
PLUGIN_ID = "hyperframes@hyperframes-colorsets-local"
EXPECTED_VERSION = "0.8.199"
EXPECTED_SKILLS = {"colorsets", "hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_snapshot() -> dict[str, str]:
    return {path.relative_to(PLUGIN).as_posix(): digest(path)
            for path in sorted(PLUGIN.rglob("*")) if path.is_file()}


def global_state_snapshot() -> dict[str, str | None]:
    """Hash state files without recording account contents in the evidence."""
    home = Path.home()
    candidates = [home / ".claude.json", home / ".claude" / "settings.json",
                  home / ".claude" / "settings.local.json", home / ".claude" / ".credentials.json",
                  home / ".claude" / "plugins" / "installed_plugins.json",
                  home / ".claude" / "plugins" / "known_marketplaces.json"]
    return {str(path): digest(path) if path.is_file() else None for path in candidates}


def save_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_json_output(text: str) -> object:
    """Accept an entire JSON document or the CLI's final JSON result line."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise RuntimeError("Native command did not return parseable JSON")


def walk_objects(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


def require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class NativeRun:
    def __init__(self, destination: Path, claude: str):
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.root = destination / f"{stamp}-{uuid.uuid4().hex[:8]}"
        self.config = self.root / "config"
        self.workspace = self.root / "workspace"
        self.config.mkdir(parents=True)
        self.workspace.mkdir()
        self.claude = claude
        self.commands: list[dict] = []
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=str(self.config), DISABLE_AUTOUPDATER="1",
                        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1", DO_NOT_TRACK="1",
                        npm_config_cache=str(self.root / "npm-cache"))
        require(Path(self.env["CLAUDE_CONFIG_DIR"]).resolve() == self.config.resolve(),
                "Claude config isolation is unavailable")

    def command(self, label: str, arguments: list[str], *, native: bool = True,
                timeout: int = 120) -> subprocess.CompletedProcess:
        argv = [self.claude, "--setting-sources", "user", *arguments] if native else arguments
        entry = {"label": label, "argv": argv, "cwd": str(self.workspace),
                 "claudeConfigDir": str(self.config)}
        prefix = f"{len(self.commands) + 1:02d}-{label}"
        self.commands.append(entry)
        started = time.monotonic()
        try:
            result = subprocess.run(argv, cwd=self.workspace, env=self.env, shell=False,
                                    capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired as error:
            entry.update(exitCode=None, elapsedSeconds=round(time.monotonic() - started, 3),
                         error="Command timed out")
            stdout = error.stdout or b""
            stderr = error.stderr or b""
            for stream_name, stream in (("stdout", stdout), ("stderr", stderr)):
                if isinstance(stream, bytes):
                    stream = stream.decode("utf-8", errors="replace")
                (self.root / f"{prefix}.{stream_name}.log").write_text(stream, encoding="utf-8")
            save_json(self.root / f"{prefix}.command.json", entry)
            raise RuntimeError(f"{label} timed out; inspect its logs") from error
        entry.update(exitCode=result.returncode, elapsedSeconds=round(time.monotonic() - started, 3))
        (self.root / f"{prefix}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (self.root / f"{prefix}.stderr.log").write_text(result.stderr, encoding="utf-8")
        save_json(self.root / f"{prefix}.command.json", entry)
        require(result.returncode == 0, f"{label} failed with exit code {result.returncode}; inspect its logs")
        return result

    def validate(self, label: str, path: Path, *, plugin: bool) -> dict:
        result = self.command(label, ["plugin", "validate", str(path), "--json", "--strict"])
        parsed = parse_json_output(result.stdout)
        require(isinstance(parsed, dict), f"{label} returned a non-object report")
        require(parsed.get("success") is True, f"{label} did not confirm success")
        require(parsed.get("strict") is True, f"{label} did not confirm strict validation")
        manifest = parsed.get("manifest")
        require(isinstance(manifest, dict), f"{label} returned no manifest")
        require(manifest.get("type") == ("plugin" if plugin else "marketplace"),
                f"{label} discovered an unexpected manifest type")
        require(manifest.get("errors") == [] and manifest.get("warnings") == [],
                f"{label} reported manifest errors or warnings")
        # Claude 2.1.302 reports contents=[] for valid plugin manifests.
        # Discover actual skills through installed native details below.
        return parsed


def installed_entry(payload: object) -> dict:
    matches = []
    for item in walk_objects(payload):
        identity = item.get("id") or item.get("pluginId") or item.get("name")
        if identity == PLUGIN_ID:
            matches.append(item)
    require(matches, "Installed plugin list does not include HyperFrames")
    candidates = [item for item in matches if item.get("enabled") is True]
    require(candidates, "Installed plugin list does not confirm enabled=true")
    require(candidates[0].get("version") == EXPECTED_VERSION,
            "Installed plugin list reports a different release version")
    return candidates[0]


def installed_path(entry: dict, config: Path) -> Path:
    raw = next((entry.get(key) for key in ("installPath", "path", "installedPath", "cachePath")
                if isinstance(entry.get(key), str)), None)
    require(raw, "Native installed plugin list did not expose an installation path")
    path = Path(raw).resolve()
    require(path.is_relative_to(config.resolve()), "Native install escaped the isolated config directory")
    require(path.is_dir() and path != PLUGIN.resolve(), "Native cache installation does not exist")
    return path


def inventory_from_details(output: str) -> set[str]:
    """Read the native skills section, refusing a name-only display as evidence."""
    row = re.search(r"^\s*Skills\s*\((\d+)\)\s+(.+)$", output, re.MULTILINE)
    require(row, "Native details did not expose a skills inventory")
    found = {name.strip() for name in row.group(2).split(",")}
    require(int(row.group(1)) == len(found) == len(EXPECTED_SKILLS),
            "Native details reports an unexpected skill count")
    require(found == EXPECTED_SKILLS,
            f"Native skills inventory is incomplete: missing {sorted(EXPECTED_SKILLS - found)}")
    return found


def isolated_state_evidence(config: Path) -> dict:
    marketplace_state = config / "plugins" / "known_marketplaces.json"
    install_state = config / "plugins" / "installed_plugins.json"
    require(marketplace_state.is_file() and install_state.is_file(),
            "CLAUDE_CONFIG_DIR isolation was not confirmed by native state files")
    require("hyperframes-colorsets-local" in marketplace_state.read_text(encoding="utf-8"),
            "Isolated marketplace registration was not persisted")
    require(PLUGIN_ID in install_state.read_text(encoding="utf-8"),
            "Isolated plugin installation was not persisted")
    return {"marketplaceState": str(marketplace_state), "installState": str(install_state)}


def verify(run: NativeRun) -> dict:
    require((PLUGIN / ".claude-plugin" / "plugin.json").is_file(), "Claude plugin manifest is missing")
    require(MARKETPLACE.is_file(), "Claude marketplace manifest is missing")
    expected_files = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
    require(expected_files == EXPECTED_SKILLS, f"Unexpected source skill inventory: {sorted(expected_files)}")
    version = run.command("claude-version", ["--version"]).stdout.strip()
    require("2.1.302" in version, f"Unexpected Claude CLI version: {version}")
    plugin_validation = run.validate("validate-plugin", PLUGIN, plugin=True)
    marketplace_validation = run.validate("validate-marketplace", PROJECT, plugin=False)
    added = run.command("marketplace-add", ["plugin", "marketplace", "add", str(PROJECT), "--json"])
    added_payload = parse_json_output(added.stdout)
    installed = run.command("plugin-install", ["plugin", "install", PLUGIN_ID, "--json"])
    install_payload = parse_json_output(installed.stdout)
    listed = run.command("plugin-list", ["plugin", "list", "--json"])
    entry = installed_entry(parse_json_output(listed.stdout))
    cache = installed_path(entry, run.config)
    details = run.command("plugin-details", ["plugin", "details", PLUGIN_ID])
    skills = inventory_from_details(details.stdout)
    state = isolated_state_evidence(run.config)
    node = shutil.which("node")
    require(node, "Node.js is not installed")
    runner = cache / "skills" / "hyperframes" / "scripts" / "plugin-cli.mjs"
    require(runner.is_file(), "The original plugin CLI runner is absent from the installed cache")
    require(digest(runner) == digest(PLUGIN / "skills" / "hyperframes" / "scripts" / "plugin-cli.mjs"),
            "The installed plugin CLI differs from the source bundle")
    runtime_version = run.command("installed-runner-version", [node, str(runner), "--version"],
                                  native=False, timeout=240).stdout.strip()
    require(re.search(r"(?<!\d)0\.8\.199(?!\d)", runtime_version),
            f"Installed runner resolved a different HyperFrames release: {runtime_version}")
    presets = []
    for mode, filename in (("colorset1", "colorset1.yml"), ("colorset2", "colorset2.yaml")):
        for leaf in ("FRAME.md", filename):
            relative = Path("skills") / "colorsets" / "assets" / mode / leaf
            target = cache / relative
            require(target.is_file(), f"Installed preset resource is missing: {relative}")
            source_hash = digest(PLUGIN / relative)
            require(digest(target) == source_hash, f"Installed preset resource changed: {relative}")
            presets.append({"path": relative.as_posix(), "sha256": source_hash})
    return {"claudeVersion": version, "hyperframesVersion": runtime_version,
            "pluginValidation": plugin_validation, "marketplaceValidation": marketplace_validation,
            "marketplaceAdd": added_payload, "pluginInstall": install_payload,
            "installedEntry": entry, "installedRoot": str(cache),
            "nativeSkills": sorted(skills), "isolatedState": state, "presets": presets,
            "modelCalls": 0,
            "limitations": ["This verifies native import, installation and resource discovery without running a model.",
                            "It does not evaluate generated video quality or model adherence to the colorset instructions."]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT / "artifacts" / "claude",
                        help="Evidence parent directory; each invocation creates a fresh run")
    args = parser.parse_args(argv)
    destination = args.output_dir.expanduser().resolve()
    require(destination.is_relative_to(PROJECT.parents[1]), "Evidence must stay inside the repository")
    claude = shutil.which("claude")
    require(claude, "Claude Code CLI is not installed")
    before_source = source_snapshot()
    before_global = global_state_snapshot()
    run = NativeRun(destination, claude)
    report = {"ok": False, "runDirectory": str(run.root), "configDirectory": str(run.config),
              "workspace": str(run.workspace)}
    try:
        report.update(verify(run))
        report["ok"] = True
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        report["error"] = str(error)
    finally:
        report["sourceBundleUnchanged"] = source_snapshot() == before_source
        report["globalClaudeStateUnchanged"] = global_state_snapshot() == before_global
        if not report["sourceBundleUnchanged"] or not report["globalClaudeStateUnchanged"]:
            report["ok"] = False
            report["integrityError"] = "Source bundle or global Claude state changed during the native test"
        report["commands"] = run.commands
        save_json(run.root / "report.json", report)
    print(json.dumps({"ok": report["ok"], "report": str(run.root / "report.json"),
                      "error": report.get("error"), "nativeSkills": report.get("nativeSkills")},
                     ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
