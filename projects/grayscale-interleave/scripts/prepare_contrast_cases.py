#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Clarify rendering criteria for a fresh cohort without changing old prompts."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "evaluations/grayscale-interleave"
cases = json.loads((HERE / "cases.json").read_bytes())
for skill, case in cases.items():
    source = HERE / case['naturalistic']['prompt']
    revised = source.read_text(encoding='utf-8') + (
        "\nRendering criteria for this case: read the actual bundled palette JSON before assigning fills; "
        "use its `solidSequence`, not the allowed-token membership list or semantic role map. "
        "Keep all category and quantitative marks and labels fully visible and opaque. Paint the actual canvas white. "
        "For the first overflow category, choose an allowed border with at least 3:1 contrast against its fill. "
        "For every label, evaluate contrast against the surface actually behind that text: at least 4.5:1. "
        "A quantitative caption may sit outside its swatch when it remains clear and associated with that swatch.\n"
    )
    target = HERE / f'prompts/{skill}-naturalistic-contrast.md'
    target.write_text(revised, encoding='utf-8')
    case['naturalistic']['prompt'] = target.relative_to(HERE).as_posix()
(HERE / 'cases-contrast.json').write_text(json.dumps(cases, indent=2) + '\n', encoding='utf-8')
print('Prepared fresh contrast-clarified prompts; original prompts and every attempt remain unchanged.')
