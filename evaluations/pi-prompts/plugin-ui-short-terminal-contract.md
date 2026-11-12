# Short-terminal skill contract

Use only the copied pi-extension-ui skill and normal tools. Read the task prompt
first. Keep the skill read-only; do not read installed Pi documentation or any
file outside this isolated workspace.

Read the skill's rich-interface reference. Produce `short-terminal-review.json`
with these keys:

- `case`: `short-terminal-contract`.
- `mode`: exactly the JSON string `tui`.
- `heightBudget`: a concise explanation of reserving host and component rows.
- `pageControls`: supported primary and alternate page controls.
- `resizePolicy`: what happens to a current page after a resize.
- `selectionPolicy`: what happens when the selected entity changes.
- `coverageCheck`: how to verify all 24 exact hourly observations remain reachable
  in a 60-column, 16-row terminal, including backward navigation and page bounds.
- `evidenceBoundary`: distinguish actual terminal process/cell screenshots,
  RPC/JSON checks and Desktop frontend acceptance.

Also create `pager.mjs`, a standalone deterministic `pageRows(records, page,
capacity)` export. It returns `{page, pages, records}` for a zero-based page,
clamps out-of-range pages, uses at least one page even for an empty collection,
and rejects a nonpositive/noninteger capacity. It must never discard records
from the input. Keep it independent of the Pi API and return a new page array.

This is a focused instruction/algorithm contract, not a claim of native UI
paint. Do not install packages, call a model, build a browser mock or claim a
terminal interaction occurred.
