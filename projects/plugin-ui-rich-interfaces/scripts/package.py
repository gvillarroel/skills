#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package local review artifacts and extract a clean portable MCP canary."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "artifacts/packages"
    definitions = {"service-observatory": output / "service-observatory",
                   "claude-native": ROOT / "claude", "pi-extension": ROOT / "pi",
                   "gemini-payloads": ROOT / "artifacts/payloads/gemini"}
    rows = []
    for name, source in definitions.items():
        target = output / f"{name}.zip"
        files = sorted(p for p in source.rglob("*") if p.is_file() and not any(part in {"node_modules", "__pycache__", ".cache"} for part in p.relative_to(source).parts))
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.relative_to(source).as_posix())
        rows.append({"name": name, "files": len(files), "bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    extract = output / "clean-portable"
    extract.mkdir(exist_ok=True)
    with zipfile.ZipFile(output / "service-observatory.zip") as archive:
        for item in archive.infolist():
            destination = (extract / item.filename).resolve()
            if not destination.is_relative_to(extract.resolve()):
                raise ValueError("Archive member escapes the clean canary.")
        archive.extractall(extract)
    (output / "package-manifest.json").write_text(json.dumps({"packages": rows, "scope": "Local review packages. Gemini contains UI payloads, not a deployed A2A service. Host installation is separate."}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"packages": rows, "cleanCanary": str(extract)}))


if __name__ == "__main__":
    main()
