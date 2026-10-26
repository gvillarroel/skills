# Nielsen review and exact ColorSets

Use this contract for UI recommendations, implementations and audits across
the assistant surfaces. Snapshot: October 25, 2026. Apply it to the existing
42 interaction patterns; a usability principle does not grant a host API.

## Contents

- [Ten usability checks](#ten-usability-checks)
- [Author English component copy](#author-english-component-copy)
- [Choose and bind a palette](#choose-and-bind-a-palette)
- [Respect the styling owner](#respect-the-styling-owner)
- [Check contrast and state](#check-contrast-and-state)
- [Record and verify](#record-and-verify)

## Ten usability checks

The following short labels map H1-H10 to
[Nielsen's ten heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).
The checks operationalize them for plugin interactions.

For implementation decisions and iterations, use
[interaction-quality.md](interaction-quality.md): define the task and state
contract, select the simplest adequate controls, exercise recovery, and compare
complexity without mistaking fewer clicks for successful task completion.

| ID | Principle | Check |
| --- | --- | --- |
| H1 | Visible status | Show connecting, ready, busy, complete and failed states; never fabricate progress. |
| H2 | Familiar concepts | Use task vocabulary, units and ordering; keep protocol details behind diagnostics. |
| H3 | Control and exits | Provide Cancel, Back and safe retry; distinguish cancellation from acceptance. |
| H4 | Consistent conventions | Keep action names, keyboard behavior and component meaning consistent with the host. |
| H5 | Prevent mistakes | Validate inputs and risky defaults; review high-cost or irreversible changes when appropriate using supported host flows. |
| H6 | Recognition cues | Expose labels, choices, current selection and needed context beside the control. |
| H7 | Efficient paths | Offer supported shortcuts and reusable selections while preserving a discoverable basic path. |
| H8 | Minimal content | Prioritize the task and primary action; reveal advanced details on demand. |
| H9 | Useful errors | Explain the problem and recovery, preserve drafts and avoid raw error codes alone. |
| H10 | Contextual help | Provide concise task instructions and explain unavailable capabilities at the relevant action. |

Inspect each heuristic against a concrete interaction: opening a result,
selecting/editing, waiting, invalid input, cancelling, recovery, and leaving.
For an inapplicable check, state the reason rather than fabricating a feature.
Separate an inspection from a test with representative users; see
[NN/G's evaluation method](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/).
When an output contract requests these IDs and short labels, preserve them
verbatim. Explain full principle names separately when useful.

## Author English component copy

Write all generated components and their authored display content in English,
even when a brief or legacy interface uses another language. Cover headings,
buttons, field labels, placeholders, tooltips, accessible names/descriptions,
chart titles/axes/legends, sample rows, help, validation, notifications, loading,
empty, saved, failed and cancelled states. Apply the same rule to native/TUI
prompts, text fallbacks and exported summaries. Retain exact protocol tokens,
IDs and proper names; preserve original source records separately from any
translated display text. Do not use a raw localized error as the only authored
recovery message.

Declare `lang="en"` on authored HTML and the equivalent document language when
supported elsewhere. Inspect actual rendered states, expanded regions, hover
help, validation errors and accessible names; a source-language declaration
alone does not verify the text. Keep third-party host chrome/dialog locale
outside authored-copy acceptance and report it separately. Do not recolor,
translate or impersonate host-owned permission controls or change OS/account
language settings. Record inspected states and remaining checks honestly.

## Choose and bind a palette

Use the self-contained snapshots:

- [colorset1.yml](../assets/palettes/colorset1.yml): red, black, white and
  neutrals; **default for each new deliverable**.
- [colorset2.yaml](../assets/palettes/colorset2.yaml): extended hues and the
  same neutrals; use only when explicitly selected for this deliverable.

Multiple categories, a dark theme, a previous CS2 artifact or a preference for
green success messages does not select CS2 automatically. Record the choice
and its source. Use one active set; do not import CS2-only hues into CS1.
Runtime work must read these bundled copies, not repository or sibling files.

Resolve claimed token paths and compute published ratios with the bundled
[design_values.py](../scripts/design_values.py):

```bash
uv run --script scripts/design_values.py --palette colorset1 --resolve colors.red.status --resolve interface.text.primary.value --contrast '#333e48' '#ffffff'
```

Run from the skill bundle, or use its absolute script path. Use `--list-tokens`
when a path is unknown; do not invent a prefix or publish hand-estimated ratios.
Inspect `passed` for valid inputs and the relevant
`contrast[].requirements` decision for ordinary/large text or essential non-text.
Valid computation is not contrast approval. Use diagnostic defaults while
repairing paths; reserve `--fail-on-findings` for clean CI. Keep full precision
for threshold decisions and derive any formatted number from that result.

Map semantic roles to exact values before drawing. The table is a starting
mapping, not a blanket contrast approval for every combination or state.

| Role | ColorSet 1 | ColorSet 2 |
| --- | --- | --- |
| Primary action | `#9e1b32` | `#9e1b32` |
| Primary hover/pressed | `#6d1222` | `#6d1222` |
| Body/helper text on a light surface | `#333e48` / `#696969` | `#333e48` / `#696969` |
| Page/surface | `#f7f7f7` / `#ffffff` | `#f7f7f7` / `#ffffff` |
| Link | `#9e1b32`, underlined | `#007298`, underlined |
| Selected surface | `#ffccd5` | `#cdf3ff` |
| Error accent | `#e8002a` plus label/icon | `#e8002a` plus label/icon |
| Success | Neutral confirmation text plus checkmark | `#45842a` accent plus confirmation text/checkmark |
| Custom focus on white | `#9e1b32` or `#333e48` | `#9e1b32`, `#007298` or `#333e48` |

Keep category-to-token mappings stable across filtering, panes and exports.
Distinguish categories with labels or shapes when color capacity is exhausted.
Preserve exact color tokens; choose another token/role when a pair fails rather
than inventing a lighter/darker hex. Avoid blended decorative layers that create
unlisted colors. Mandatory accessibility overrides take precedence.

Use Open Sans when available and permitted, then Arial/sans-serif as bundled.
Use a permitted icon source or labeled native icon; do not assume the icon font
is installed. Avoid an undeclared font/CDN request. Terminal/native typography
follows the host's documented restrictions.

## Respect the styling owner

| Surface | Application of this contract |
| --- | --- |
| Authored MCP App HTML/SVG/canvas or extension webview | Bind authored paint and state tokens to the selected palette. Test layout, focus, theme and contrast in the actual container. |
| Claude native nodes or Copilot terminal controls | Use only supported props and host theme roles. Exact color/font control may be unavailable or remapped; retain labels, symbols and keyboard usability. Never assume HTML/CSS or ANSI truecolor. |
| Host elicitation, MCPB settings, permission dialog or app chrome | Host owns paint. Improve supported labels, order, validation, defaults, help and cancellation. Do not inject CSS or recolor consent controls. |
| Forced colors, high contrast or mandatory host styling | Preserve the override and semantic roles. Document the exception; do not claim exact palette pixels on host-owned paint. |
| Text-only or unsupported UI | Apply the ten checks to the text workflow; provide a meaningful monochrome alternative. |

A custom iframe following ColorSet 1 does not make the surrounding host chrome
ColorSet 1. A host theme token is not evidence of an exact hex result. Use
`exact`, `host-mapped`, `host-owned` or `accessibility-override` to describe the
styling scope in a report, with an explanation of unverified paint.
For an MCP App, split the authored iframe's paint from the host-owned frame,
dialogs and chrome in separate records. Host-provided theme context alone does
not make the entire authored iframe `host-mapped`.

## Check contrast and state

Measure each actual foreground/background pair after theme and compositing.
Target at least **4.5:1 for ordinary text**, **3:1 for large text** (18 pt,
or 14 pt bold), and **3:1 against adjacent colors for essential authored
control/state indicators**. Compare unrounded ratios; sufficient color
membership is not sufficient contrast. These thresholds do not constitute a
complete accessibility audit.
[Text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html),
[non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

Known traps in the exact palette definitions:

- `#cfcfcf` on white is about **1.558:1**: insufficient for an authored focus
  indicator requiring 3:1. Choose a darker allowed token and preserve focus.
- `#9c9c9c` on white is about **2.745:1**: insufficient when that border is
  the required means of identifying the control. Decorative borders differ.
- Error text `#e8002a` on `#ffccd5` is about **3.326:1**: insufficient for
  ordinary text. Use `#333e48` or `#9e1b32` for the text; retain a labeled
  error accent. Canonical role suggestions are not automatic compliance.

Use text, icons, shape or pattern alongside status/category color; a red versus
green difference alone is insufficient. Underline links or supply another
visible action cue. [Color redundancy](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).
Check default, hover, keyboard focus, selected, busy, invalid, empty, disabled,
cancelled and recovery states. Honor each host's accessible control behavior.
Review shadows and whole-element opacity after compositing, including selected
helper text and required borders; choose another allowed token when they fail.

Associate noninteractive tooltip help with its trigger, support dismissal,
prevent pointer interception and keep it inside the viewport. Test the actual
sequence from export to an adjacent action with ordinary pointer and keyboard
input. Treat interactive popovers separately. Match requested actions to real
controls and reachable states; a translated copy list does not prove an action
exists. For a narrow table, expose an equivalent accessible representation with
every field and selection state, keep one representation active, and test focus
and wrapping at 320px and a nearby width.

## Record and verify

Before implementation, record `palette`, `selection_source`, semantic role
mapping, styling owner, permitted overrides and H1-H10 checks. For every
heuristic record `pass`, `issue`, `not-applicable` or `untested`, the affected
interaction, evidence and proposed fix. A planned check has no observed result.

For an implementation, inspect keyboard navigation and visible focus, readable
labels, cancel/error recovery, narrow layout, theme and palette/contrast in the
rendered container. Verify the returned authoritative state and any claimed
host effect. For a recommendation, give an executable acceptance plan and
keep UI/user testing and host acceptance unverified. Never convert an
unperformed check into `observed-failed` to satisfy report syntax.

Report the selected set, authored versus host-owned scope, heuristic findings,
contrast measurements, remaining tests and actual evidence layer. A color
audit or heuristic checklist alone proves neither usability nor host support.
