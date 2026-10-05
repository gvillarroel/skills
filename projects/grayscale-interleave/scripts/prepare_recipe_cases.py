#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Make the boundary allocation recipe explicit without providing gray hex order."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'evaluations/grayscale-interleave'
cases = json.loads((HERE/'cases-contrast.json').read_bytes())
for skill, case in cases.items():
    source = HERE/case['naturalistic']['prompt']
    prompt = source.read_text(encoding='utf-8') + (
        '\nUse this allocation recipe for the boundary case: filter the actual canvas token from the bundled '
        '`solidSequence`; assign categories 0 through capacity minus one directly from that list. '
        'The next category reuses the first fill, with its contrasting border chosen from that fill\'s '
        '`textOnFill` value. That precomputed black/white choice maximizes contrast against the fill. '
        'Read the fill values from the bundled JSON rather than guessing them. Keep the supplied numeric ramp separate.\n'
    )
    target=HERE/f'prompts/{skill}-naturalistic-recipe.md'
    target.write_text(prompt,encoding='utf-8')
    case['naturalistic']['prompt']=target.relative_to(HERE).as_posix()
(HERE/'cases-recipe.json').write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8')
print('Prepared recipe-guided boundary forwards; original cohorts and strict/native gates are unchanged.')
