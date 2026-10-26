#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify native Pi package installation and SDK skill discovery without model calls."""

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
import uuid


PROJECT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.8.199"
EXPECTED_SKILLS = {"colorsets", "hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use"}
SDK_HELPER = Path(__file__).with_name("discover_pi.ts")


def require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_source() -> dict[str, str]:
    paths = [PROJECT / "package.json", *(PROJECT / "plugin").rglob("*")]
    return {path.relative_to(PROJECT).as_posix(): digest(path) for path in sorted(paths) if path.is_file()}


def snapshot_global_settings() -> dict[str, str | None]:
    # Do not read or copy auth files. Only settings preservation is measured.
    paths = [Path.home() / ".pi" / "agent" / "settings.json", Path.home() / ".pi" / "settings.json"]
    return {str(path): digest(path) if path.is_file() else None for path in paths}


def save_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_json(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise RuntimeError("Command did not return parseable JSON")


def resolve_pi_host() -> tuple[str, Path, Path | None]:
    """Resolve the installed npm wrapper without executing a shell or the wrapper."""
    wrapper_value = shutil.which("pi")
    require(wrapper_value, "Pi is not installed on PATH")
    wrapper = Path(wrapper_value)
    wrappers = [wrapper, wrapper.with_suffix(".ps1"), wrapper.with_suffix(".cmd")]
    candidates = []
    for candidate in wrappers:
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"(node_modules[/\\]@earendil-works[/\\]pi-coding-agent[/\\]dist[/\\]bundle[/\\]cli\.js)", text)
            if match:
                candidates.append((candidate.parent / match.group(1).replace("\\", "/"), candidate))
    candidates.append((wrapper.parent / "node_modules" / "@earendil-works" / "pi-coding-agent" /
                       "dist" / "bundle" / "cli.js", wrapper))
    for cli, found_wrapper in candidates:
        if cli.is_file():
            host = cli.parents[2]
            manifest = json.loads((host / "package.json").read_text(encoding="utf-8"))
            require(manifest.get("name") == "@earendil-works/pi-coding-agent", "Unexpected Pi host package")
            require(manifest.get("version") == "1.4.0", "This regression requires native Pi 1.4.0")
            node = shutil.which("node")
            require(node, "Node.js is not installed")
            return node, cli.resolve(), found_wrapper
    raise RuntimeError("Could not resolve Pi's installed dist/bundle/cli.js from its npm wrapper")


class NativeRun:
    def __init__(self, output_dir: Path):
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.root = output_dir / f"{stamp}-{uuid.uuid4().hex[:8]}"
        self.agent_dir = self.root / "agent"
        self.workspace = self.root / "workspace"
        self.package = self.root / "package"
        self.agent_dir.mkdir(parents=True)
        self.workspace.mkdir()
        self.package.mkdir()
        self.commands: list[dict] = []
        self.env = dict(os.environ, PI_CODING_AGENT_DIR=str(self.agent_dir), PI_OFFLINE="1",
                        PI_TELEMETRY="0", DO_NOT_TRACK="1", npm_config_cache=str(self.root / "npm-cache"))

    def command(self, label: str, argv: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess:
        entry = {"label": label, "argv": argv, "cwd": str(self.workspace),
                 "piCodingAgentDir": str(self.agent_dir), "piOffline": True}
        self.commands.append(entry)
        prefix = f"{len(self.commands):02d}-{label}"
        try:
            result = subprocess.run(argv, cwd=self.workspace, env=self.env, shell=False,
                                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                                    timeout=timeout)
        except subprocess.TimeoutExpired as error:
            entry.update(exitCode=None, error="Command timed out")
            for stream_name, value in (("stdout", error.stdout), ("stderr", error.stderr)):
                stream = value or ""
                if isinstance(stream, bytes):
                    stream = stream.decode("utf-8", errors="replace")
                (self.root / f"{prefix}.{stream_name}.log").write_text(stream, encoding="utf-8")
            save_json(self.root / f"{prefix}.command.json", entry)
            raise RuntimeError(f"{label} timed out; inspect its logs") from error
        entry["exitCode"] = result.returncode
        (self.root / f"{prefix}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (self.root / f"{prefix}.stderr.log").write_text(result.stderr, encoding="utf-8")
        save_json(self.root / f"{prefix}.command.json", entry)
        require(result.returncode == 0, f"{label} failed with exit code {result.returncode}; inspect its logs")
        return result


def resolve_declared_local_package(settings_file: Path, workspace: Path) -> Path:
    require(settings_file.is_file(), "Native Pi install did not create local .pi/settings.json")
    settings = json.loads(settings_file.read_text(encoding="utf-8"))
    sources = [item if isinstance(item, str) else item.get("source") for item in settings.get("packages", [])]
    require(len(sources) == 1 and isinstance(sources[0], str), "Unexpected native local package declarations")
    path = Path(sources[0])
    # Native Pi stores project-local package paths relative to .pi/settings.json.
    return (path if path.is_absolute() else settings_file.parent / path).resolve()


def verify(run: NativeRun) -> dict:
    source_manifest = PROJECT / "package.json"
    require(source_manifest.is_file(), "Pi package.json is missing")
    manifest = json.loads(source_manifest.read_text(encoding="utf-8"))
    require(manifest.get("name") == "@gvillarroel/hyperframes-colorsets", "Unexpected Pi package identity")
    require(manifest.get("version") == EXPECTED_VERSION, "Unexpected Pi package version")
    require(manifest.get("pi", {}).get("skills") == ["./plugin/skills"], "Pi skill declaration is missing")
    for kind in ("extensions", "prompts", "themes"):
        require(manifest.get("pi", {}).get(kind) == [], f"Unexpected Pi {kind} declaration")
    shutil.copy2(source_manifest, run.package / "package.json")
    shutil.copytree(PROJECT / "plugin", run.package / "plugin")
    require({path.name for path in run.package.iterdir()} == {"package.json", "plugin"},
            "The isolated package copied resources outside its declared bundle")
    node, cli, wrapper = resolve_pi_host()
    host = cli.parents[2]
    node_version = run.command("node-version", [node, "--version"]).stdout.strip()
    require(node_version.startswith("v24."), f"This regression requires Node.js 24: {node_version}")
    pi_version = run.command("pi-version", [node, str(cli), "--version"]).stdout.strip()
    require(re.search(r"(?<!\d)1\.4\.0(?!\d)", pi_version), f"Unexpected native Pi version: {pi_version}")
    run.command("pi-install-local", [node, str(cli), "install", "--local", str(run.package), "--approve"])
    listing = run.command("pi-list", [node, str(cli), "list", "--approve"]).stdout
    declared_root = resolve_declared_local_package(run.workspace / ".pi" / "settings.json", run.workspace)
    require(declared_root == run.package.resolve(), "Native Pi installed a different local package")
    require(str(declared_root) in listing or declared_root.as_posix() in listing,
            "Native pi list did not expose the installed package declaration")
    # Reinstall in the same isolated workspace to verify native declaration idempotence.
    run.command("pi-reinstall-local", [node, str(cli), "install", "--local", str(run.package), "--approve"])
    require(resolve_declared_local_package(run.workspace / ".pi" / "settings.json", run.workspace) == declared_root,
            "Native Pi reinstall changed or duplicated its package declaration")
    discovered = run.command("pi-sdk-discovery", [node, "--experimental-strip-types",
                                                  str(SDK_HELPER), str(host), str(declared_root),
                                                  str(run.workspace), str(run.agent_dir)])
    discovery = parse_json(discovered.stdout)
    require(isinstance(discovery, dict), "Pi SDK discovery returned a non-object result")
    skills = discovery.get("skills", [])
    require(len(skills) == 5 and {item["name"] for item in skills} == EXPECTED_SKILLS,
            "Native Pi SDK did not discover exactly the five packaged skills")
    require(discovery.get("diagnostics") == [] and discovery.get("extensionErrors") == [],
            "Native Pi SDK reported resource diagnostics")
    require(discovery.get("promptDiagnostics") == [] and discovery.get("themeDiagnostics") == [],
            "Native Pi SDK reported prompt or theme diagnostics")
    require(all(discovery.get(key) == 0 for key in ("extensionCount", "promptCount", "themeCount", "contextFileCount")),
            "Pi resource isolation loaded ambient or executable resources")
    for item in skills:
        path = Path(item["filePath"]).resolve()
        require(path.is_relative_to(declared_root / "plugin" / "skills"), "A skill escaped the copied bundle")
        relative = path.relative_to(declared_root)
        require(path.is_file() and digest(path) == digest(PROJECT / relative), "A discovered skill changed")
    runner = declared_root / "plugin" / "skills" / "hyperframes" / "scripts" / "plugin-cli.mjs"
    require(digest(runner) == digest(PROJECT / runner.relative_to(declared_root)), "Original runner changed")
    runtime_version = run.command("installed-runner-version", [node, str(runner), "--version"], timeout=240).stdout.strip()
    require(re.search(r"(?<!\d)0\.8\.199(?!\d)", runtime_version), "Original runner resolved a different release")
    preset_files = []
    for mode, filename in (("colorset1", "colorset1.yml"), ("colorset2", "colorset2.yaml")):
        for leaf in ("FRAME.md", filename):
            relative = Path("plugin") / "skills" / "colorsets" / "assets" / mode / leaf
            target = declared_root / relative
            require(target.is_file() and digest(target) == digest(PROJECT / relative),
                    f"Copied preset resource differs: {relative}")
            preset_files.append({"path": relative.as_posix(), "sha256": digest(target)})
    return {"piVersion": pi_version, "nodeVersion": node_version, "hyperframesVersion": runtime_version,
            "piHostRoot": str(host), "piCli": str(cli), "piWrapper": str(wrapper),
            "piWrapperSha256": digest(wrapper) if wrapper else None, "packageRoot": str(declared_root),
            "installedRoot": str(declared_root / "plugin"), "sourceRoot": str(PROJECT),
            "discovery": discovery, "presets": preset_files, "skillCommand": "/skill:colorsets", "modelCalls": 0,
            "limitations": ["Native install/list and native SDK resource discovery are exercised without an agent session.",
                            "No model inference, video quality assessment or model-adherence evaluation is performed."]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT / "artifacts" / "pi",
                        help="Evidence parent directory; each run creates a fresh isolated workspace")
    args = parser.parse_args(argv)
    output_dir = args.output_dir.expanduser().resolve()
    require(output_dir.is_relative_to(PROJECT.parents[1]), "Evidence must stay inside the repository")
    before_source = snapshot_source()
    before_settings = snapshot_global_settings()
    run = NativeRun(output_dir)
    report = {"ok": False, "runDirectory": str(run.root), "agentDirectory": str(run.agent_dir),
              "workspace": str(run.workspace)}
    try:
        report.update(verify(run))
        report["ok"] = True
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        report["error"] = str(error)
    finally:
        report["sourceBundleUnchanged"] = snapshot_source() == before_source
        report["globalPiSettingsUnchanged"] = snapshot_global_settings() == before_settings
        if not report["sourceBundleUnchanged"] or not report["globalPiSettingsUnchanged"]:
            report["ok"] = False
            report["integrityError"] = "The source bundle or global Pi settings changed during the test"
        report["commands"] = run.commands
        save_json(run.root / "report.json", report)
    print(json.dumps({"ok": report["ok"], "report": str(run.root / "report.json"),
                      "error": report.get("error"), "skillCommand": report.get("skillCommand")}, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
