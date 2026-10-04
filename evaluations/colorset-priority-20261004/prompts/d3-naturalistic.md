Create an offline D3 catalogue for eighteen delivery groups on a white canvas.
Use Colorset 1 and the skill's normal categorical styling. The ordered group
labels are Capture, Triage, Review, Plan, Build, Test, Package, Approve,
Release, Observe, Support, Archive, Audit, Train, Renew, Retire, Recover,
and Reconcile. Give each a separate equal-size filled tile with its label
inside. Preserve that reading order in a compact grid with direct labels;
color should distinguish the groups rather than encode a numeric magnitude.

Save exact `priority.html` and `priority.svg`. The HTML must run offline,
retain editable D3-generated geometry, and show a readable resting state on
desktop and a 390-pixel mobile viewport. Expose each rendered tile with
`data-category-index` equal to its zero-based reading-order position. Export
the actual rendered SVG rather than drawing an unrelated second copy.
Save exact `allocation.json` with `canvas`, `labels`, and `styles`: an array
of eighteen actual tile styles containing `fill`, `text`, `stroke`,
`strokeWidth`, and `opacity`. Derive the record from the rendered tiles.

Use only the current workspace, the copied skill, and normal local tools.
Treat `skills/d3/` as read-only. Do not read acceptance examples, sibling
skills, parent run records, repository context, or outside sources. Write
all generated task files outside the copied skill directory. Read the
entry point and the focused categorical styling guidance before authoring.
