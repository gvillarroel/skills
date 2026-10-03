#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Create a compact priority-ordered prose candidate; retain unavailable evidence."""
from pathlib import Path
import hashlib,json,shutil
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
parent=STUDY/'candidates/visual-grammar/svg-brief-design'
child=STUDY/'candidates/graphic-economy/svg-brief-design'
shutil.copytree(parent,child)
front=(parent/'SKILL.md').read_text(encoding='utf-8').split('---',2)[1]
body='''# SVG Brief Design

Create original geometry for the current brief. Preserve its subject, mood,
palette, proportions, and exact output path. Keep this skill read-only.

## Prioritize recognition and composition

First decide what must be recognizable, whether the composition is radial,
vertical, or horizontal, and whether it is primarily line art or filled art.
Resolve those decisions before adding decoration. Keep a compact horizontal
design shallow; do not turn every frame or label into a dashboard panel.

Use a small number of purposeful shapes. Give the subject's identifying
features more importance than ornamental detail. Avoid duplicate outlines,
extra borders, fake bevels, random micro-marks, and symmetry that the brief
does not call for. A simple clear contour is usually stronger than several
nearly parallel ones. Leave room for the interior to read.

## Make the geometry intentional

Match line weight to the requested character: strong graphic contrast should
not become uniformly faint hairlines. Keep related lines consistent, with
secondary detail quieter than the main structure. Use smooth curves for
curved forms and deliberate corners for angular forms.

In filled artwork, separate meaningful parts with clear openings. Check the
combined silhouette after overlapping shapes: eyes, joints, or inner channels
must not disappear. Avoid extra eye-like holes or cutouts that change the
subject. Keep intentionally solid objects solid. Use real transparent holes
when needed, rather than painting the background color over the artwork.

For a diagram, preserve the relationship it communicates. A periodic wave
should repeat coherently and, when no offset is specified, oscillate around
its baseline. Connect axes and endpoints deliberately. A vintage character
can affect line quality without changing the underlying geometry.

## Preserve readable information

Use real short words or conventional letters when text is requested. SVG text
elements are valid editable vector content; use a generic font fallback.
Do not simulate labels with arbitrary strokes or invented outline glyphs.
Keep illustrative metadata generic, and do not claim decorative codes scan.

## Deliver and review

Write a self-contained editable SVG with a valid viewBox. Set fill and stroke
explicitly; open line work should not inherit a solid fill. Honor transparency
and the requested palette. Add no unrequested background, shadow, or object.

Check the subject at thumbnail size, then check the focal details, interior
openings, stroke consistency, text, and cropping. Render when tools permit;
with writing-only tools, review geometry and stacking without claiming a
rendered inspection. Remove details that weaken the result.

Consult [SVG mechanics](references/svg-mechanics.md) for technical questions.
This bundle contains general guidance and documentation references only, with
no reference artwork, stored path data, or reconstruction recipes.
'''
path=child/'SKILL.md';path.write_text('---'+front+'---\n\n'+body,encoding='utf-8',newline='\n')
proposal={'candidate':'graphic-economy','parents':['visual-grammar','baseline'],'parent_skill_sha256':hashlib.sha256((parent/'SKILL.md').read_bytes()).hexdigest(),'candidate_skill_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'evidence':'Only complete generation-000 development evidence; no private evidence and no fitness from the unavailable semantic-structure branch.','observations':['The first guide increases mean similarity slightly but keeps layered contours and introduces pseudo-text.','It improves style features more reliably than semantic structure.','Long unprioritized guidance can leave conflicts between decorative cutouts and the requested subject unresolved.'],'mutation':'Replace the longer checklist with a compact priority order: subject and composition, deliberate geometry, readable text, then review. Reduce ornamental expansion. This tests instruction organization and economy rather than copying any scene.','unavailable_sibling':'semantic-structure: five exact WebSocket closed 1011 provider errors; the sole evaluable case is retained but not used to select or mutate this sibling.','artwork_transferred':False,'private_feedback_used':False}
(STUDY/'graphic-economy-proposal.json').write_text(json.dumps(proposal,indent=2))
print(json.dumps({'candidate':str(child),'lines':len(path.read_text().splitlines()),'artwork_transferred':False}))
