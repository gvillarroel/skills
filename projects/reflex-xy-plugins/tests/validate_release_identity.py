#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare extracted XY distributions with their canonical and adapter sources."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def require(value: object, message: str) -> None:
    if not value:
        raise AssertionError(message)


def files(root: Path) -> dict[str, bytes]:
    return {file.relative_to(root).as_posix(): file.read_bytes() for file in root.rglob("*")
        if file.is_file() and not {"node_modules", "__pycache__", ".venv", ".git"} & set(file.relative_to(root).parts)
        and file.relative_to(root).parts[:2] != ("assets", "examples")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--canonical-skill", type=Path, required=True)
    parser.add_argument("--source-project", type=Path, required=True)
    parser.add_argument("--app-dist", type=Path, help="Validated application build directory; defaults to source-project/chatgpt/dist")
    parser.add_argument("--version", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    app_dist = args.app_dist or args.source_project / "chatgpt/dist"
    canonical = files(args.canonical_skill)
    report = {"passed": False, "version": args.version, "canonical_runtime_files": len(canonical), "distributions": {}}
    distributions = {"claude": "reflex-xy-claude-code", "chatgpt": "reflex-xy-chatgpt", "desktop": "reflex-xy-claude-desktop"}
    if (args.extracted_root / "reflex-xy-chatgpt-desktop").is_dir():
        distributions["portable"] = "reflex-xy-chatgpt-desktop"
    for name, directory in distributions.items():
        root = args.extracted_root / directory
        if not root.is_dir():
            root = args.extracted_root / name
        skill = root / ("skills/reflex-xy" if name in {"claude", "portable"} else "runtime/skill/reflex-xy")
        packaged = files(skill)
        require(packaged == canonical, f"{name} skill runtime differs from the canonical source")
        manifest = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
        require(manifest["version"] == args.version, "Wrong bundle version")
        sources = {}
        for file in ["render.py", "presets.py"]:
            packaged_source = (root / "runtime" / file).read_bytes()
            require(packaged_source == (args.source_project / "shared" / file).read_bytes(), f"{name} stale {file}")
            sources[file] = hashlib.sha256(packaged_source).hexdigest()
        for file in ["capabilities.json", "contract.json"]:
            capability = json.loads((root / "runtime" / file).read_text(encoding="utf-8"))
            require(capability["default_colorset"] == "colorset1", f"{name} capability default differs")
        if name == "claude":
            for file in ["hooks/register.ts", "hooks/helpers.ts"]:
                require((root / file).read_bytes() == (args.source_project / "claude" / file).read_bytes(), "Stale Claude Mod source")
        else:
            for file in ["server-bundled.js", "widget.html", "THIRD-PARTY-NOTICES.txt"]:
                packed = (root / "chatgpt/dist" / file).read_bytes()
                require(packed == (app_dist / file).read_bytes(), f"Stale {name} {file}")
                sources[file] = hashlib.sha256(packed).hexdigest()
            if name == "portable":
                for file in ["plugin.json", "mcp.json", "assets/icon.svg"]:
                    require((root / file).read_bytes() == (args.source_project / "chatgpt-desktop" / file).read_bytes(), f"Stale portable {file}")
        report["distributions"][name] = {"canonical_runtime_matches": True, "sources": sources}
    report["canonical_files"] = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(canonical.items())}
    report["passed"] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["passed", "version", "canonical_runtime_files"]}))


if __name__ == "__main__":
    main()
