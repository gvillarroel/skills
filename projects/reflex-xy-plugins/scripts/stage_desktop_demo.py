#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stage both desktop adapters and a repository-local marketplace without global writes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def relative_plugin_paths(value: object) -> object:
    """Avoid a placeholder that the observed Codex 0.145 loader leaves literal."""
    if isinstance(value, str):
        if value == "${PLUGIN_ROOT}":
            return "./"
        if value.startswith("${PLUGIN_ROOT}/"):
            return value[len("${PLUGIN_ROOT}/"):]
        if "${PLUGIN_ROOT}" in value:
            raise ValueError("PLUGIN_ROOT must be a complete path prefix")
        return value
    if isinstance(value, list):
        return [relative_plugin_paths(item) for item in value]
    if isinstance(value, dict):
        return {key: relative_plugin_paths(item) for key, item in value.items()}
    return value


def inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Path must stay inside {root}")
    return resolved


def verify_source(root: Path) -> None:
    if root.is_symlink():
        raise ValueError("Package root must not be a symbolic link")
    bundle = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
    actual = set()
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise ValueError(f"Linked package member: {candidate.relative_to(root)}")
        if candidate.is_file():
            actual.add(candidate.relative_to(root).as_posix())
    expected = {entry["path"] for entry in bundle["files"]} | {"bundle.json"}
    if actual != expected:
        raise ValueError("Package members differ from the declared inventory")
    for entry in bundle["files"]:
        file = inside(root / entry["path"], root)
        if not file.is_file():
            raise ValueError(f"Missing or linked package file: {entry['path']}")
        if hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Package source changed: {entry['path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--workspace-dir", type=Path)
    args = parser.parse_args()
    releases = inside(args.release_dir, PROJECT / "artifacts")
    release = json.loads((releases / "release.json").read_text(encoding="utf-8"))
    target = inside(args.workspace_dir or PROJECT / "artifacts" / f"desktop-demo-{release['version']}", PROJECT / "artifacts")
    if target.exists():
        parser.error("Workspace already exists; preserve it and choose a new --workspace-dir")
    source = releases / "reflex-xy-chatgpt-desktop"
    code_source = releases / "reflex-xy-claude-code"
    verify_source(source)
    verify_source(code_source)
    node = shutil.which("node")
    uv = shutil.which("uv")
    if not node or not uv:
        parser.error("Install Node.js and uv before staging the desktop adapters")

    marketplace_path = inside(REPO / ".agents/plugins/marketplace.json", REPO)
    if marketplace_path.exists():
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        if any(entry.get("name") == "reflex-xy" for entry in marketplace.get("plugins", [])):
            parser.error("A reflex-xy marketplace entry already exists; preserve it and review before restaging")
    else:
        marketplace = {"name": "xy-desktop-local", "interface": {"displayName": "XY Desktop Local"}, "plugins": []}

    desktop = target / "chatgpt-plugin"
    code_workspace = target / "claude-workspace"
    code = code_workspace / ".claude/skills/reflex-xy"
    shutil.copytree(source, desktop)
    shutil.copytree(code_source, code)
    configured = []
    for name in ("mcp.json", ".mcp.json"):
        file = desktop / name
        value = relative_plugin_paths(json.loads(file.read_text(encoding="utf-8")))
        server = value["mcpServers"]["xy"]
        server["command"] = node
        server.setdefault("env", {}).update({
            "XY_UV_BINARY": uv,
            "XY_RUNTIME_DIR": str(target / "charts"),
            "UV_CACHE_DIR": str(PROJECT / "cache/uv"),
        })
        write_json(file, value)
        configured.append(name)

    marketplace_label = marketplace.get("interface", {}).get("displayName", marketplace["name"])
    marketplace["plugins"].append({
        "name": "reflex-xy",
        "source": {"source": "local", "path": "./" + desktop.relative_to(REPO).as_posix()},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    })
    write_json(marketplace_path, marketplace)
    (code_workspace / "DEMO.txt").write_text(
        "Open this exact folder in Claude Desktop's local Code tab.\n"
        "Run /xy-chart line to open the native chart pane without a model turn.\n"
        "Colorset 1 is the default. Use More options for optional controls.\n"
        "Complete sign-in and workspace trust manually if requested.\n",
        encoding="utf-8",
    )
    report = {
        "version": release["version"], "global_files_written": False,
        "marketplace": str(marketplace_path), "marketplace_name": marketplace["name"],
        "chatgpt_plugin": str(desktop), "claude_workspace": str(code_workspace),
        "configured_package_files": configured, "node": node, "uv": uv,
        "scope": "Prepared local sources; application installation and inline/native painting are untested.",
        "next_steps": [f"Restart ChatGPT Desktop, choose {marketplace_label} in Plugins, then review installation.",
                       "Open the Claude workspace in a local Code session and invoke /xy-chart line."],
    }
    write_json(target / "staging.json", report)
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
