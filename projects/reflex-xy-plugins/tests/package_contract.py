#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit an XY plugin ZIP without trusting its own package manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile


def require(value: object, message: str) -> None:
    if not value:
        raise AssertionError(message)


def inspect(archive: Path, extracted_root: Path | None = None) -> dict:
    with zipfile.ZipFile(archive) as package:
        entries = [entry for entry in package.infolist() if not entry.is_dir()]
        names = [entry.filename.replace("\\", "/") for entry in entries]
        require(len(set(names)) == len(names), "Duplicate ZIP member names")
        forbidden_parts = {"node_modules", "__pycache__", ".venv", ".git", ".env", "artifacts", "evaluations"}
        for entry, name in zip(entries, names):
            path = PurePosixPath(name)
            require(not path.is_absolute() and ".." not in path.parts and ":" not in name,
                    f"Unsafe ZIP member {name}")
            require(not set(path.parts) & forbidden_parts, f"Dependency, cache, secret, or artifact in ZIP: {name}")
            require(not re.search(r"(?:^|/)assets/examples(?:/|$)", name), f"Acceptance gallery in runtime ZIP: {name}")
            mode = entry.external_attr >> 16
            require(not stat.S_ISLNK(mode), f"ZIP contains a symbolic link: {name}")
            require(entry.file_size < 20 * 1024 * 1024, f"Oversize runtime member: {name}")
        skill_files = [name for name in names if name.endswith("reflex-xy/SKILL.md")]
        require(skill_files, "The canonical reflex-xy skill is missing from the distribution")
        link_count = 0
        for skill_file in skill_files:
            root = PurePosixPath(skill_file).parent
            skill_names = {name for name in names if name.startswith(str(root) + "/")}
            require(any(name.endswith("scripts/xy_colorsets.py") for name in skill_names), "Skill palette helper missing")
            require(any(name.endswith("assets/palettes/colorsets.json") for name in skill_names), "Skill palette contract missing")
            for name in sorted(skill_names):
                if not name.endswith(".md"):
                    continue
                text = package.read(name).decode("utf-8")
                require("C:/Users/" not in text and "C:\\Users\\" not in text, "Machine-specific runtime documentation")
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                    target = target.strip().strip("<>").split("#", 1)[0]
                    if not target or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                        continue
                    parts = list(PurePosixPath(name).parent.parts)
                    for part in PurePosixPath(target).parts:
                        if part == "..":
                            require(parts, f"Markdown path escaped archive: {target}")
                            parts.pop()
                        elif part != ".":
                            parts.append(part)
                    resolved = "/".join(parts)
                    require(resolved.startswith(str(root) + "/"), f"Skill Markdown depends outside its bundle: {name}: {target}")
                    require(resolved in names, f"Broken packaged skill link: {name}: {target}")
                    link_count += 1
        integrity = None
        if extracted_root:
            observed = {file.relative_to(extracted_root).as_posix() for file in extracted_root.rglob("*") if file.is_file()}
            require(observed == set(names), "Extracted runtime file inventory changed during validation")
            require(all((extracted_root / name).read_bytes() == package.read(name) for name in names),
                    "Extracted runtime bytes changed during validation")
            integrity = True
        return {"archive": archive.name, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "members": len(names), "bytes": sum(entry.file_size for entry in entries),
                "skill_roots": [str(PurePosixPath(name).parent) for name in skill_files],
                "skill_local_links": link_count, "extracted_payload_unchanged": integrity, "passed": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--extracted-root", type=Path)
    args = parser.parse_args()
    report = inspect(args.archive, args.extracted_root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
