#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Realize a prose-only mutation from retained development evidence."""
from pathlib import Path
import hashlib,json,shutil
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
parent=STUDY/'candidates/visual-grammar/svg-brief-design'
child=STUDY/'candidates/semantic-structure/svg-brief-design'
shutil.copytree(parent,child)
path=child/'SKILL.md';text=path.read_text(encoding='utf-8')
text=text.replace('## Construct the drawing\n', '''## Preserve the subject while simplifying

Give the main structure the proportions implied by the brief. When the request
emphasizes a horizontal strip or compact label, keep its contents in a shallow
band rather than expanding it into a dashboard panel. For a simple frame,
prefer one clear contour to nested borders and decorative bevels.

Keep the subject's identifying features stronger than secondary decoration.
Check for unintended readings such as extra eye-like openings, merged limbs,
or a diagram that looks like an unrelated symbol. Do not carve objects meant
to read as solid or dark merely to add visual interest.

## Construct the drawing
''')
text=text.replace('Use compound paths or masks for transparent cutouts;\nwhite paint is not transparency.', 'Use compound paths or masks for transparent cutouts when the subject needs\nthem; white paint is not transparency. Specify fill deliberately, and use no\nfill for open line work so inherited fills do not close or darken it.')
text=text.replace('or label decorative codes as machine-readable without implementing them.', '''or label decorative codes as machine-readable without implementing them.
For a periodic waveform, repeat a coherent amplitude and period. Unless an
offset is specified, place its excursions on both sides of the baseline.
An old drawing style may change line character without changing the diagram's
meaning or disconnecting its axes.

When the brief asks for text, use real readable words or conventional diagram
letters. Editable SVG text is vector content: use text elements with a generic
font fallback. Do not replace information with rows of random strokes or invent
polygon glyphs that only resemble writing. Keep labels short and meaningful;
make illustrative metadata clearly generic rather than asserting facts.''')
path.write_text(text,encoding='utf-8',newline='\n')
proposal={'candidate':'semantic-structure','parents':['visual-grammar','baseline'],'parent_skill_sha256':hashlib.sha256((parent/'SKILL.md').read_bytes()).hexdigest(),'candidate_skill_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'evidence':'search/development/generation-000/pareto-archive.json and review/comparison.jpg','observations':['The first guide improves frame and label similarity but still adds nested contours.','Generated label contains no SVG text nodes and visually substitutes invented glyphs and strokes for information.','Waveform remains above its baseline; a dark central object receives unrequested cutouts.','Face silhouette similarity declines while style proxy improves, showing a semantic/composition tradeoff.'],'mutation':'Add transferable semantic-structure and legibility checks. Keep palette, task instructions, renderer, reward weights, and resources unchanged.','artwork_transferred':False,'private_feedback_used':False}
(STUDY/'semantic-structure-proposal.json').write_text(json.dumps(proposal,indent=2))
print(json.dumps({'candidate':str(child),'lines':len(text.splitlines()),'artwork_transferred':False}))
