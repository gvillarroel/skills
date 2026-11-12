#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build portable XY adapters from canonical sources without modifying skills."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
SKILL = REPO / "skills/reflex-xy"
RELEASE_VERSION = "0.3.2"
MCP_RUNTIME_VERSION = "0.3.1"
EXCLUDED = {"node_modules", "__pycache__", ".venv", ".git", ".runtime", "dist"}


def copy_tree(source, target, *, skill=False):
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if not path.is_file() or any(p in EXCLUDED for p in rel.parts):
            continue
        if skill and rel.parts[:2] == ("assets", "examples"):
            continue
        if path.is_symlink():
            raise ValueError(f"Refusing symbolic link: {path}")
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def capabilities():
    sys.path.insert(0, str(PROJECT / "shared"))
    spec = importlib.util.spec_from_file_location("xy_packaged_renderer", PROJECT / "shared/render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.capabilities()


def runtime(root, skill_dir):
    for name in ("render.py", "presets.py"):
        shutil.copyfile(PROJECT / "shared" / name, root / "runtime" / name)
    manifest = json.dumps(capabilities(), indent=2) + "\n"
    write(root / "runtime/capabilities.json", manifest)
    write(root / "runtime/contract.json", manifest)
    copy_tree(SKILL, skill_dir, skill=True)


def finish(root, extension=".zip"):
    paths = sorted(p for p in root.rglob("*") if p.is_file())
    inventory = [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    write(root / "bundle.json", json.dumps({"name": root.name, "version": RELEASE_VERSION, "xy_version": "0.0.8",
          "mcp_runtime_version": MCP_RUNTIME_VERSION if (root / "chatgpt/dist").is_dir() else None,
          "skill_source": "skills/reflex-xy", "skill_snapshot": "canonical runtime; acceptance examples excluded",
          "files": inventory}, indent=2) + "\n")
    archive = root.with_suffix(extension)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            # MCPB requires manifest.json at archive root. ZIPs also extract
            # directly to a user-selected folder, without a redundant wrapper.
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2026, 10, 24, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, path.read_bytes(), compresslevel=9)
    return {"name": root.name, "archive": str(archive), "directory": str(root),
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "bytes": archive.stat().st_size,
            "files": len(inventory) + 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory inside project artifacts")
    parser.add_argument("--desktop", action="store_true", help="Also build the Claude Desktop MCPB")
    parser.add_argument("--app-dist", type=Path, default=PROJECT / "chatgpt/dist", help="Validated application build directory")
    args = parser.parse_args()
    app_dist = args.app_dist.resolve()
    for filename in ("server.js", "server-bundled.js", "widget.html", "THIRD-PARTY-NOTICES.txt"):
        if not (app_dist / filename).is_file():
            parser.error(f"Application build is incomplete: {filename}")
    output = args.output_dir.resolve()
    if not output.is_relative_to((PROJECT / "artifacts").resolve()):
        parser.error("Output must stay inside this project's artifacts directory")
    if output.exists():
        parser.error("Output already exists; choose a fresh release directory to preserve prior builds")
    output.mkdir(parents=True)
    results = []
    code = output / "reflex-xy-claude-code"
    (code / "runtime").mkdir(parents=True)
    copy_tree(PROJECT / "claude", code)
    runtime(code, code / "skills/reflex-xy")
    write(code / "INSTALL.md", (PROJECT / "packaging/claude-code-install.md").read_text(encoding="utf-8"))
    results.append(finish(code))
    app = output / "reflex-xy-chatgpt"
    (app / "runtime").mkdir(parents=True)
    copy_tree(PROJECT / "chatgpt", app / "chatgpt")
    for file in ("server.js", "server-bundled.js", "widget.html", "THIRD-PARTY-NOTICES.txt"):
        source = app_dist / file
        if not source.is_file():
            raise ValueError("Build chatgpt with npm run build before packaging")
        dest = app / "chatgpt/dist" / file
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    runtime(app, app / "runtime/skill/reflex-xy")
    write(app / "INSTALL.md", (PROJECT / "packaging/chatgpt-install.md").read_text(encoding="utf-8"))
    copy_tree(PROJECT / "notes", app / "notes")
    results.append(finish(app))
    local = output / "reflex-xy-chatgpt-desktop"
    (local / "runtime").mkdir(parents=True)
    runtime(local, local / "skills/reflex-xy")
    copy_tree(PROJECT / "chatgpt-desktop", local)
    manifest = json.loads((local / "plugin.json").read_text(encoding="utf-8"))
    overlay = manifest["extensions"]["com.openai"]
    compatibility = {key: manifest[key] for key in ("name", "version", "description", "author", "homepage", "repository", "keywords")}
    compatibility.update(overlay)
    compatibility.update({"skills": "./skills/", "mcpServers": "./.mcp.json"})
    write(local / ".codex-plugin/plugin.json", json.dumps(compatibility, indent=2) + "\n")
    mcp = json.loads((local / "mcp.json").read_text(encoding="utf-8"))
    write(local / ".mcp.json", json.dumps({"mcpServers": mcp["mcpServers"]}, indent=2) + "\n")
    for name in ("server-bundled.js", "widget.html", "THIRD-PARTY-NOTICES.txt"):
        source = app_dist / name
        if not source.is_file():
            raise ValueError("Build the standalone server before packaging the desktop plugin")
        target = local / "chatgpt/dist" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    write(local / "package.json", json.dumps({"name": "reflex-xy-desktop", "version": RELEASE_VERSION, "private": True, "type": "module"}) + "\n")
    write(local / "INSTALL.md", (PROJECT / "packaging/chatgpt-desktop-install.md").read_text(encoding="utf-8"))
    results.append(finish(local))
    if args.desktop:
        desktop = output / "reflex-xy-claude-desktop"
        (desktop / "runtime").mkdir(parents=True)
        runtime(desktop, desktop / "runtime/skill/reflex-xy")
        for name in ("server-bundled.js", "widget.html", "THIRD-PARTY-NOTICES.txt"):
            source = app_dist / name
            if not source.is_file():
                raise ValueError("Build the standalone Node server before creating the Desktop extension")
            dest = desktop / "chatgpt/dist" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        shutil.copyfile(PROJECT / "claude-desktop/manifest.json", desktop / "manifest.json")
        write(desktop / "package.json", json.dumps({"name": "reflex-xy-desktop", "version": RELEASE_VERSION, "private": True, "type": "module"}) + "\n")
        write(desktop / "INSTALL.md", (PROJECT / "packaging/claude-desktop-install.md").read_text(encoding="utf-8"))
        results.append(finish(desktop, ".mcpb"))
    report = {"version": RELEASE_VERSION, "mcp_runtime_version": MCP_RUNTIME_VERSION,
              "revision": "Installation documentation; adapter runtime unchanged from 0.3.1",
              "distributions": results}
    write(output / "release.json", json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
