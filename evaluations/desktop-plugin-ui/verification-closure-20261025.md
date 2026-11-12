# Local component verification closure

Date: 2026-10-25. Corrected **project copies of three HTML/JSON pairs** now
pass the scoped local checks below. The original isolated-run outputs,
generation hashes, language-study results and retained failures were not
edited or replaced. This is a new local correction subject, not a reroll or a
retroactive pass for any prior skill cohort. Overall skill status remains
`validating`; no canonical skill or backlog change is made by this report.

## Corrected copies

The new sources are under
[`projects/desktop-plugin-ui/verification-20261025/`](../../projects/desktop-plugin-ui/verification-20261025/),
with `status-panel.html` and `component-copy.json` in `component-1/`,
`component-2/` and `component-3/`.
[`provenance.json`](../../projects/desktop-plugin-ui/verification-20261025/provenance.json)
binds all six original and corrected hashes. The generator verifies the
historical sources before/after; the browser verifier verifies them again.
Copied historical task flags retain their original-generation meaning,
explicitly explained by `revision_provenance`; new empirical evidence is here.

| Copy | Corrections |
| --- | --- |
| 1 | Recompute all optional contrast values; add verified exact palette-token paths. Retain the desktop table and show an accessible named list of selection buttons below 650px, with all ID/subject/priority/status values and preserved selection/focus. Hide the inactive representation from the accessibility tree. Replace the native-title-only export tooltip with an associated authored description. |
| 2 | Remove the decorative alpha shadow; strengthen the row-border token; restore **Explain selection**, showing the current saved request/priority/status and preserving the existing busy-state behavior. Update equivalent copy in the JSON. |
| 3 | Use `#696969` for identifying control borders, remove whole-editor opacity, and darken selected-row helper text. Associate export help with `aria-describedby`. Use ordinary named-list buttons with `aria-pressed` rather than incomplete listbox-option semantics. |
| All | Use opaque CS1 tokens; tooltips remain noninteractive, do not intercept pointer actions, dismiss with Escape, and clamp within the viewport. Preserve English display/accessibility copy and exact source identifiers. |

The source-file paths in these three palette declarations were already correct;
the corrected copies now additionally bind each CSS variable to an actual
token path and value, such as `interface.text.primary.value`,
`interface.border.dark.value` and `interface.state.selected.value`. Each path
is resolved independently against the current bundled YAML. This does not
repair or erase the earlier design-contract cohort's unrelated token-path error.

## Observed gates

The final independent headless Edge **156.0.4314.42** / Playwright **1.64.1**
run passes **22 source/provenance checks and 108 browser checks**, covering
three copies at **1100×820, 360×780 and 320×780**. It retains **135 state
captures**, accessible snapshots, computed geometry, local CSV bytes,
contrast records and **63 screenshots**. All nine contexts have zero page
errors and zero HTTP(S) requests. Existing project dependencies were reused;
no installation, service, provider call, account, foreground GUI or host/OS
configuration change occurred.

The checks exercise search/selection, busy refresh, invalid save with focus,
cancel without changing saved data, retained data after refresh failure,
successful retry, empty recovery with search focus, local save, later draft
cancellation, tooltip focus/Escape/description, CSV export followed by an
ordinary **Explain selection** click, keyboard Explain and visible focus.
There are no forced clicks or runtime DOM repairs. The responsive table
fallback has no exposed narrow table or nested horizontal scroller.

Independent numeric results include:

- `#333e48`/white and inverse: **10.9182386444:1**.
- `#696969`/white: **5.4898145574:1**.
- `#333e48`/`#ffccd5`: **7.7207365400:1**.
- Identifying search borders: **5.4898145574:1** against white in every context.
- The final populated states' measured visible text pairs have a minimum
  **5.1244065316:1**, above the applicable ordinary/large-text thresholds.

Numerical metadata uses unrounded values; formatted values are derived from
them. Computed browser text/essential-border contrast is measured in the final
populated state; the source-pair checks also cover header, selected/error,
tooltip and primary-action colors. This is not an exhaustive all-state,
native-control, forced-colors or screen-reader accessibility audit.

Manual screenshot review covered the desktop table, desktop refresh failure,
narrow cards and Explain result, plus narrow/minimum tooltips. Labels and
records are readable; the tooltip remains transient and dismissible. These
observations support bounded Nielsen checks for visible state, cancel/retry,
validation, consistent controls, recognition, efficient selection, disclosure,
error recovery and contextual help. Terminology and usability with
representative support users remain untested.

## Commands and retained evidence

```powershell
uv run --script projects/desktop-plugin-ui/verification-20261025/prepare-copies.py
node projects/desktop-plugin-ui/mcp-probe/node_modules/tsx/dist/cli.mjs projects/desktop-plugin-ui/verification-20261025/verify-components.ts
```

The verifier's default output is
`projects/desktop-plugin-ui/artifacts/verification-closure-20261025/run-002/`.
Its `report.json` SHA-256 is
`cd1e968ffa6ec8dc2622f2e4250ce885549bd706f971107be838fa4e8cbdd370`.
The verifier SHA-256 is
`3d4b6c2c691441053a05743537102a7bea7b9bc84c1856fb6761ed6a347bbdb8`.
Pass a new `UI_VERIFICATION_RUN=run-NNN` when retaining another run; do not
overwrite completed evidence.

`run-001/` is retained as failed local evidence: it exposed a clipped tooltip
in copy 1 at 360px and a probe-side TSX `__name` serialization error that
prevented rendered-contrast measurement. The tooltip now clamps to the viewport;
the measurement callback is transported as plain browser JavaScript. An initial
validator startup also required the new project's explicit ESM package scope;
no component checks ran during that startup failure. These repairs are separate
from immutable historical model outputs.

## Small reusable guidance proposed to the owning skill

1. Derive published ratios from unrounded luminance calculations and resolve
   every claimed source-token path against the actual palette. Token membership
   alone does not prove contrast.
2. Review shadows **and whole-element opacity** for composited paint. Use a
   darker permitted token when an identifying border or selected helper text
   otherwise fails its contrast threshold.
3. For noninteractive tooltips, associate the trigger/description, provide
   dismissal, prevent pointer interception, and measure viewport bounds. Test
   the real sequence **export → adjacent action** with ordinary clicks and
   keyboard focus; treat interactive popovers as a different control pattern.
4. Compare the requested action inventory with actual controls and exercised
   states. A translated copy list does not prove an Explain action exists.
5. When a narrow table cannot remain readable, retain an equivalent accessible
   representation with every field and selection state. Expose one active
   representation and test focus/selection at 320px and a nearby wrap width.

## Remaining boundaries

These are standalone local fixtures, with synthetic state and local CSV
downloads. They do not establish MCP registration, assistant-host painting,
server authority, durable storage, authorization, OS delivery or real
screen-reader announcement timing. No representative-user study, installed
assistant acceptance or new isolated skill evaluation was performed in this
closure pass. Earlier factual/evidence-label failures and pending host gates
remain intact. The parent workflow owns canonical promotion and subsequent
isolated validation.
