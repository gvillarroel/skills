#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extend a retained development chronology with a concrete illustration brief."""

from pathlib import Path

root=Path(__file__).resolve().parents[3]
original=(root/'evaluations/pi-prompts/usefulcharts-mixed-chronology.md').read_text(encoding='utf-8')
original=original.replace('# Naturalistic case: mixed duration treatments','# Naturalistic case: contextual illustration composition')
original=original.replace('and a contextual illustration for the clockmaking event.',
    'and three contextual drawings: a clock mechanism for the clockmaking schools, a bridge for the road survey, and a stagecoach beside the discussion of winter roads. Identify these as explanatory images rather than evidence of the invented events. Let the images form readable local groups with their notes; use at least two different relative placements, including one beside its prose. Keep complete image silhouettes at a useful size.')
original+='\nKeep `skills/usefulcharts-style/` read-only. Write all generated files inside this workspace. Use the bundled resources without network research or repository discovery.\n'
target=root/'evaluations/pi-prompts/usefulcharts-contextual-art.md';target.write_text(original,encoding='utf-8')
print('Wrote the contextual-art development prompt without changing its supplied history.')
