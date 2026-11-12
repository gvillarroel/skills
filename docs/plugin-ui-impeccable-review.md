# Impeccable lessons for agent micro UIs

Reviewed the primary source of [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
at commit [`b4bff1626c344067788c2679f048a20057c7cc5a`](https://github.com/pbakaus/impeccable/tree/b4bff1626c344067788c2679f048a20057c7cc5a),
committed November 11 and reviewed November 12, 2026. This is a selective source
review and independent paraphrase. No upstream code, binaries, installers or
command implementation is included in the skills.

## Lessons and their limits

| Source | Transferable lesson | Application to an agent decision |
| --- | --- | --- |
| [Distill](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/distill.md) | Remove redundant content and structure while retaining the information needed to complete the goal. | Keep one question, comparable options and relevant evidence; reduce repeated labels and containers. |
| [Colorize](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/colorize.md) | Assign stable roles to color and validate computed contrast in real states. | Separate subject/data emphasis from selection, action and status; preserve native theme roles and non-color cues. |
| [Typeset](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/typeset.md) | Build a deliberate hierarchy and stress actual text, widths and scaling. | Use browser-relative reading size, measured dense graph labels, and an equivalent text tree when enlarged labels no longer fit. |
| [Layout](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/layout.md) | Group by meaning before adding frames; choose density and adaptation deliberately. | Bounded radio choices remain useful click areas; avoid extra nested UI cards. Preserve DOM/focus order as options stack. |
| [Clarify](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/clarify.md) | Action labels should communicate their outcome and keep terminology stable. | After selection, name the chosen parent on the action instead of leaving an ambiguous generic label. |
| [Critique](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/critique.md) and [Polish](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/polish.md) | Assess design intent before mechanical findings; rank consequential failures before cosmetics and fix narrowly. | Review the decision path and hierarchy, then geometry/contrast/focus, then reconcile. A clean scan is evidence for its rules, not a UX certification. |

The upstream material also distinguishes work/reading surfaces from persuasive
or experiential pages. Apply that distinction without importing a full product
shell into a micro UI. Preserve familiar host controls. A decorative signature,
unusual typography, additional navigation or new context-file system needs a
task-specific reason. Font/card/color heuristics cannot override a valid host
convention or semantic diagram geometry.

## Concrete refinement

The [taxonomy choice example](plugin-ui-micro-decisions.md) had the same strong
red fill on the disputed concept and the action, with selected-state red added
again. The refined version uses bold ink and an outline for the concept; red
identifies selection and the enabled action. Unavailable actions stay neutral
and readable. Pointer selection avoids the additional keyboard focus frame,
while real keyboard navigation keeps it.

Reading text now uses the browser's base size (16px in the tested environment),
with explicit relative type roles. Reasons remain a justified dense 14px role;
graph labels are measured at 12px in the default state. With enlarged user text,
the same parent/sibling/concept relationship becomes a readable text tree rather
than shrinking labels. This is the same decision and information, with no extra
navigation. The primary action changes to `Use Data integration` or the other
chosen parent.

## Evidence

The existing browser/MCP/SDK suite passes 25/25 after the changes. A targeted
quality audit passes 14/14, including computed enabled/disabled contrast,
large radio-label hit areas, pointer and keyboard focus, contextual action copy,
and 200% root-font scaling at 542 and 320 CSS pixels. Root-font scaling is not a
claim of browser UI zoom. Actual integrated-browser screenshots at 542x767
verify the final color/type hierarchy and action label. Native Pi code did not
change; its earlier terminal evidence remains separately scoped.

This was not an execution of Impeccable's formal critique command or detector.
The source's ideas informed a scoped local review and independently implemented
checks. Raw source snapshots, screenshots and browser reports remain under
`projects/plugin-ui-impeccable-review/artifacts/`, outside Git. The seven host
bundles keep their own compact guidance in `references/micro-decisions.md`.
See [validation evidence](../evaluations/desktop-plugin-ui/impeccable-20261112.md).
