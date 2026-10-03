#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit text/source-only packaging and exact long development-path reuse."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def audit(skill, references=None):
    files = {p.relative_to(skill).as_posix(): p for p in skill.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert files and "SKILL.md" in files
    assert all(p.suffix in {".md", ".yaml", ".py"} and not p.is_symlink() for p in files.values())
    text = "\n".join(p.read_text(encoding="utf-8") for p in files.values())
    assert not re.search(r"data:image|base64,|vector-\d{3}|p\d{2}-s\d{3}|Fox Rockett|account\.foxrockett", text, re.I)
    tokens = re.sub(r"\s+", " ", text)
    compared, sources = set(), set()
    if references:
        for source in references.glob("*/tests/reference.svg"):
            raw = source.read_bytes()
            sources.add(hashlib.sha256(raw).hexdigest())
            for element in ET.fromstring(raw).iter():
                d = re.sub(r"\s+", " ", element.get("d", "")).strip()
                if len(d) >= 80:
                    assert d not in tokens, "A long original reference path is present in the bundle"
                    compared.add(hashlib.sha256(d.encode()).hexdigest())
    return {"passed": True, "file_count": len(files),
            "files": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(files.items())},
            "stored_artwork_files": 0, "unique_development_references": len(sources), "long_paths_compared": len(compared),
            "scope": "Exact textual long-path matches, forbidden payloads and packaged assets. Mathematical generators are allowed. This cannot establish independent creation or rule out every transformed reconstruction; human source review remains required."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path)
    parser.add_argument("--development-references", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.skill, args.development_references)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
