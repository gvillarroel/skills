#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package the independent MCP App and read-only Pi adapter for local review."""
import hashlib
import json
from pathlib import Path
import zipfile

PROJECT = Path(__file__).resolve().parents[1]

def main():
    output = PROJECT / "artifacts/packages"
    package = output / "incident-analysis"
    rows = []
    for name, files in {
        "incident-analysis.zip": [(p, p.relative_to(package).as_posix()) for p in sorted(package.rglob("*")) if p.is_file()],
        "incident-analysis-pi.zip": [(PROJECT / "model.mjs", "model.mjs"), (PROJECT / "pi/incident.ts", "pi/incident.ts")],
    }.items():
        target = output / name
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source, member in files:
                archive.write(source, member)
        rows.append({"path": target.relative_to(PROJECT).as_posix(), "files": len(files), "bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    (output / "package-manifest.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows))

if __name__ == "__main__":
    main()
