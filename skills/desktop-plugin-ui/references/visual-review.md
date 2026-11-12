# Compare and critique plugin UI with vision

## Contents

- [Fair comparisons](#make-the-comparison-fair)
- [Visual and behavioral checks](#inspect-the-decision-not-just-the-decoration)
- [Reachable states](#exercise-reachable-states)
- [Verdicts and repairs](#record-a-bounded-verdict-and-repair)

Use for requested design exploration, screenshot critique or a meaningful
layout change. This is a heuristic and implementation review, not a user study.
Read [ui-composition.md](ui-composition.md) for combinations and
[usability-and-color.md](usability-and-color.md) for H1-H10 and exact tokens.

## Make the comparison fair

Name the task, data, selected record, state and intended outcome. Compare
alternatives with the same viewport and information. Preserve an existing UI
as the baseline when available. Otherwise label the baseline as proposed;
do not present an intentionally poor mockup as an actual product defect.

Inspect actual screenshots with vision. Code inspection, DOM geometry,
contrast ratios and accessibility trees supplement vision; they do not replace
it. A vision tool must actually receive the pixels before claiming a visual
inspection. If no image viewer is available, report that gap and complete the
available behavioral checks. Render static/local prototypes when host access
is unavailable, with a visible prototype label and a named evidence layer.
Keep screenshots out of the runtime skill and generated files outside the
copied bundle. A runtime task must not read a large acceptance gallery.

Use representative samples, adjusted to the host: authored web UI around
320/360, 768 and 1280 px; Pi around 60/80/120 visible terminal columns and a
short height. Include actual container dimensions, zoom/theme and a focused
state when relevant. Browser pixels are not terminal columns. Do not force a
terminal preview to satisfy a mobile browser layout contract or infer terminal
paint from an HTML simulation.

## Inspect the decision, not just the decoration

| Look at the pixels for | Exercise separately |
| --- | --- |
| Task, identity, current value, completion and next action remain apparent | Selection updates the correct authoritative record and cancel does not commit. |
| Clear primary/secondary hierarchy; enough whitespace for the task | Deterministic controls do not trigger an unnecessary model turn. |
| No clipped labels, hidden errors, unreadable logs or trapped nested scrolling | Keyboard-only operation reaches every task action and returns focus on close. |
| Visible focus and readable selected/disabled/invalid states | Focus order, accessible names, state announcements and native key conventions. |
| Status has words/symbols as well as color; contrast remains sufficient | Resize/theme/forced colors do not leave cached or stale paint. |
| Compact status leaves room for transcript/editor; preview has useful detail | Second plugin's status, notifications, keys and render-site content still work. |

One visually dominant action is useful per decision, but a long inline form
may need more than one legitimate control. A smaller control count is not a
win when essential context or recovery disappears. Likewise a table and chart
work well together when each answers a different question; duplicating every
value continuously can worsen the comparison.

## Exercise reachable states

Cover initial/empty, selected/draft, busy, success, invalid/error/retry and
cancel/close when the task reaches them. If progress cannot be measured, show
a truthful busy state rather than a fabricated percentage. Preserve drafts
on failure; prevent duplicate effects and verify late results cannot revive a
closed view. Reopen/reload only when persistence is part of the task.

Check real Tab/Shift+Tab, Enter/Space and Escape behavior as supported by the
named control and surface; take a focused
screenshot. A click test does not establish keyboard operation. Keep required
actions visible or discoverable in the narrow state and check both collapsed
and expanded details. A screenshot cannot prove live region announcements,
consent, bridge calls, persistence or model-call counts.

Check that action labels describe their actual effects: displaying a path is
not copying it, and opening diagnostics is not inspecting artifact content.
In multi-panel views, scope Escape and other handlers to the surface that owns
focus; a hidden or neighboring busy card must not steal an unrelated action.
Test cancel/back on a reopened selector and restore the committed selection.
Exercise long record names and paths; readable wrapping matters even when the
document itself has no horizontal overflow.

## Record a bounded verdict and repair

For each material finding record: scenario ID, host/prototype layer,
viewport/state, screenshot, visible defect, consequence for this task,
severity, fix and executed recheck. Use H1-H10 where relevant; mark unperformed
checks untested. Prefer task blockers, then likely errors, then friction.

Compare values only where measured: initially visible controls, required
decisions/inputs, steps to completion, space left for task content, clipped
regions and actual setup/inference cost. For example, "the focused screenshot
keeps the export result and next action visible at 360 px" is bounded evidence;
"users prefer it" needs user testing. Do not claim superiority merely because
you designed one alternative to fail.

Repair a real defect, recapture that state and re-exercise the affected path.
Retain the earlier finding and failed evidence. Promote the transferable
mechanism into a small runtime reference; keep task data, screenshots and
full prototype source in the project. Stop when the requested path and
recovery work, blockers are fixed and remaining host/user checks are explicit.

Report visual appearance, behavior, interoperability and host acceptance as
separate conclusions. A well-rendered prototype can justify a layout decision
while its actual host adapter remains untested.
