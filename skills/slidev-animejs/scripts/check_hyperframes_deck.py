#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check local HyperFrames inputs without building, executing, or changing them."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", type=Path, required=True)
    parser.add_argument("--require-bundled-runtime", action="store_true")
    parser.add_argument("--direct-open", action="store_true", help="Require the single-file HTML recipe")
    args = parser.parse_args()
    deck = args.deck.resolve()
    bundle = Path(__file__).resolve().parents[1] / "assets/templates/slidev-hyperframes"
    errors = []
    checked = []
    for source in sorted(bundle.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(bundle)
        target = deck / relative
        if not target.resolve().is_relative_to(deck):
            errors.append(f"Runtime resource leaves deck boundary: {relative.as_posix()}")
            continue
        if not target.is_file() or not target.stat().st_size:
            errors.append(f"Missing or empty runtime resource: {relative.as_posix()}")
            continue
        actual = digest(target)
        checked.append({"path": relative.as_posix(), "sha256": actual})
        if args.require_bundled_runtime and actual != digest(source):
            errors.append(f"Bundled runtime was modified: {relative.as_posix()}")
    package_file = deck / "package.json"
    package = {}
    try:
        if not package_file.resolve().is_relative_to(deck):
            raise ValueError("package.json leaves deck boundary")
        package = json.loads(package_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        errors.append(f"Invalid package.json: {error}")
    dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    if dependencies.get("@hyperframes/player") != "0.8.134":
        errors.append("Declare exact @hyperframes/player dependency 0.8.134")
    for dependency in ("@slidev/cli", "vue"):
        if not dependencies.get(dependency):
            errors.append(f"Declare dependency {dependency}")
    scripts = package.get("scripts", {})
    if not scripts.get("build"):
        errors.append("Declare a native Slidev build script")
    if args.direct_open and (not scripts.get("build:html") or not dependencies.get("vite-plugin-singlefile")):
        errors.append("Declare build:html and vite-plugin-singlefile for the direct-open fallback")
    if package.get("type") != "module":
        errors.append("Declare package type module")
    for name in ("slides.md",):
        target = deck / name
        if not target.is_file() or not target.stat().st_size:
            errors.append(f"Missing or empty deck input: {name}")
        elif not target.resolve().is_relative_to(deck):
            errors.append(f"Deck input leaves deck boundary: {name}")
    if args.direct_open and not any((deck / name).is_file() for name in ("vite.config.ts", "vite.config.js", "vite.config.mjs")):
        errors.append("Declare a Vite config with the single-file HTML plugin")
    slides_file = deck / "slides.md"
    if slides_file.is_file() and slides_file.resolve().is_relative_to(deck):
        slides = slides_file.read_text(encoding="utf-8-sig")
        head = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|$)", slides, re.DOTALL)
        declared = re.search(r"^theme:\s*([^#\r\n]+)", head.group(1), re.MULTILINE) if head else None
        theme = declared.group(1).strip().strip("\"'") if declared else "default"
        candidates = (theme, f"@slidev/theme-{theme}", f"slidev-theme-{theme}")
        if theme != "none" and not theme.startswith(".") and not any(dependencies.get(name) for name in candidates):
            errors.append(f"Declare the selected Slidev theme dependency: {theme}")
    report = {"accepted": not errors, "deck": str(deck), "errors": errors, "runtime": checked,
              "playerVersion": "0.8.134", "coreVersion": "0.8.134"}
    print(json.dumps(report, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
