#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise the bundled static checker with legal and invalid Slidev inputs."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
CHECKERS = [ROOT / "skills" / skill / "scripts/check_mermaid_deck.py" for skill in ("slidev-echarts", "slidev-animejs")]
assert CHECKERS[0].read_bytes() == CHECKERS[1].read_bytes(), "Bundled static checkers differ."
ARTIFACTS = ROOT / "projects/slidev-diagram-defaults/artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
assert ARTIFACTS.resolve().is_relative_to(ROOT)
HEAD = "---\ntheme: default\nfonts:\n  sans: Open Sans\n---\n\n"
BLOCK = "```mermaid\nflowchart LR\n  A --> B\n```\n"
LEGAL = HEAD + "# First\n\n" + BLOCK + "\n---\n\n# Second\n\n" + BLOCK + "\n---\n\n# Third\n\n" + BLOCK


def snapshot(deck: Path) -> dict[str, bytes]:
    return {str(file.relative_to(deck)): file.read_bytes() for file in deck.rglob("*") if file.is_file()}


def verify(deck: Path, expected: bool) -> dict[str, object]:
    before = snapshot(deck)
    process = subprocess.run([sys.executable, str(CHECKERS[0]), "--deck", str(deck), "--plain-mermaid", "--expect-blocks", "3"], capture_output=True, text=True, check=False)
    report = json.loads(process.stdout)
    assert report["passed"] is expected, report
    assert (process.returncode == 0) is expected, (process.returncode, report)
    assert snapshot(deck) == before, "Checker modified the target deck."
    return report


with tempfile.TemporaryDirectory(prefix="static-deck-check-", dir=ARTIFACTS) as temporary:
    deck = Path(temporary).resolve()
    assert deck.is_relative_to(ARTIFACTS.resolve())
    for relative in ("diagram-style.mjs", "setup/mermaid.ts", "setup/mermaid-renderer.ts"):
        destination = deck / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("// Runtime presence fixture.\n", encoding="utf-8")
    (deck / "style.css").write_text(".slidev-layout { padding: 1rem; }\n", encoding="utf-8")
    (deck / "package.json").write_text(json.dumps({"devDependencies": {"@slidev/cli": "52.16.0"}, "dependencies": {"@slidev/theme-default": "0.25.0"}}), encoding="utf-8")
    (deck / "slides.md").write_text(LEGAL, encoding="utf-8")
    valid = verify(deck, True)
    assert valid["mermaidBlocks"] == 3

    missing = deck / "setup/mermaid-renderer.ts"
    missing.unlink()
    verify(deck, False)
    missing.write_text("", encoding="utf-8")
    verify(deck, False)
    missing.write_text("// Runtime presence fixture.\n", encoding="utf-8")

    negative_sources = {
        "unclosed-fence": LEGAL.rsplit("```", 1)[0],
        "fence-theme": LEGAL.replace("```mermaid", "```mermaid {theme: 'forest'}", 1),
        "diagram-theme": LEGAL.replace("```mermaid\n", "```mermaid\n---\nconfig:\n  theme: forest\n---\n", 1),
        "class-definition": LEGAL.replace("  A --> B", "  A --> B\n  classDef default fill:#007298", 1),
        "init-directive": LEGAL.replace("```mermaid\n", '```mermaid\n%%{init: {"theme": "forest"}}%%\n', 1),
    }
    for source in negative_sources.values():
        (deck / "slides.md").write_text(source, encoding="utf-8")
        verify(deck, False)

print("Passed: legal Slidev headmatter with three plain Mermaid blocks and extra CSS; missing or empty runtime, malformed fences, per-diagram themes, class definitions, and init directives reject; target files remain unchanged.")
