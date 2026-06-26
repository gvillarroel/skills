---
name: d3-composition-evaluator
description: Evaluate D3 or SVG composition quality using dynamic symmetry, balance, reading path, label clearance, visible SVG previews, and stable composition IDs. Use when a user asks what is missing or wrong in a D3/SVG pattern, gallery card, composition sheet, or generated visual example.
---

# D3 Composition Evaluator

## Workflow

1. Identify the artifact, SVG selector, visible screenshot, and intended composition: balance, diagonal, proportional split, grid, radial, flow, or dense-label lanes.
   - If the user names an exact output file or path, write that exact path. Do not replace it with a conversational-only response.
   - In skill-only or isolated validation, treat the prompt as complete unless it names a local artifact to inspect. Do not search parent repositories, sibling skills, evaluation prompt folders, or gallery fixtures for extra context.
2. Render or inspect the actual SVG before judging it. Prefer a browser screenshot or SVG export when local tooling is available; do not evaluate only from source text when the request is visual.
3. Check the contract first: every evaluated pattern should have a visible nonblank SVG, `title` and `desc`, stable IDs, and enough attributes to connect the composition variant back to the source pattern.
4. Evaluate the composition with the rubric in `references/evaluation-rubric.md`. Treat data truth as a constraint: improve placement, grouping, guides, labels, and hierarchy without falsifying quantitative geometry.
5. Report concrete findings first. Reference exact selectors, IDs, files, or card names when available, then list the minimum fixes required.
6. When the pattern needs to be reimagined into a different composition instead of only critiqued, hand off to `$d3-composition-recomposer`.

## Output Shape

- Start with what is missing or wrong.
- Separate composition issues from implementation contract issues.
- Include validation commands or browser checks when the artifact lives in a runnable project.
- Avoid broad style advice unless it changes readability, data integrity, or composition strength.

## Progressive Disclosure

Read `references/evaluation-rubric.md` when the task involves scoring, comparing multiple variants, auditing dynamic-symmetry alignment, or deciding whether a variant is good enough to publish.
