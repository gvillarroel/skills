# Interaction, styling, and evidence

Define the user's input, task, and visible success before selecting controls.
Implement local selection, validation, filtering, cancellation, and direct
actions without model work unless the task needs interpretation or generation.
Keep authoritative data separate from drafts and presentation state. An old
dialog response must not replace a newer draft or authorize a different action.
Use a shared domain function with a small host adapter; add a service or
framework only when the selected interaction requires it.

## Review the actual interaction

Apply Nielsen H1-H10 to observable behavior, and explain a nonapplicable check:

| ID | Check |
| --- | --- |
| H1 | Show current state, progress, completion, and failure. |
| H2 | Use task language and meaningful labels. |
| H3 | Preserve a safe exit, cancellation, and reversible navigation. |
| H4 | Follow the selected host's control and keyboard conventions. |
| H5 | Constrain invalid input and prevent accidental submission. |
| H6 | Make choices and current values visible without memorization. |
| H7 | Offer useful direct arguments or shortcuts without removing the simple route. |
| H8 | Remove controls and permanent surfaces that do not help the task. |
| H9 | Explain errors, retain input, and provide an actionable recovery. |
| H10 | Put concise help at the point where it is needed. |

Exercise success, empty/error states, invalid input, cancel, retry, reopen,
keyboard navigation, narrow and wide layouts, and delayed responses where
applicable. Fix observed problems and rerun affected checks. Screenshots help
assess appearance; they do not prove behavior or host integration.
[Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).

## Apply the styling boundary

Write authored visible and accessible copy, comments, exports, and reports in
English. Set authored HTML language to `en`. Preserve proper names, API values,
and original source records. Host-owned chrome follows the host locale.

Use bundled colorset1 by default; use colorset2 only when explicitly selected
for this deliverable. Resolve exact tokens instead of guessing shades:

```text
python <bundle>/scripts/design_values.py --palette colorset1 --list-tokens
python <bundle>/scripts/design_values.py --contrast '#333e48' '#ffffff'
```

Replace `<bundle>` with this bundle's actual path. The helper reads its own
[colorset1](../assets/palettes/colorset1.yml) and
[colorset2](../assets/palettes/colorset2.yaml). Inspect `passed` and findings;
use `--fail-on-findings` for a failing CI exit. Bind owned paint to exact tokens,
check actual contrast, and convey status beyond color. Preserve native themes,
accessibility overrides, and host-rendered catalog styles. An authored iframe
and the surrounding host chrome have different styling owners.

## Report the layer actually tested

Record command, environment/build, expected result, actual result, and artifact
for each executed check. Label claims `documented`, `observed-working`,
`observed-failed`, `conditional`, `untested`, or `unsupported`, with their scope.
Use `unsupported` only for an explicit exclusion; an absent check is `untested`.
Keep inherited historical observations separate from current acceptance.

Distinguish schema, protocol, browser fixture, native engine, actual terminal,
and signed-in host paint. A successful lower layer cannot establish a higher
one. Retain failed attempts and identify the first failing layer. Account,
policy, installation, transport, and renderer issues have different causes.
For ordinary builds, provide concise validation notes in the requested schema;
do not manufacture a second evidence report. Deliver runnable artifacts,
setup/test commands, observed behavior, and remaining host checks.
