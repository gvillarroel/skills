# English component and display-copy contract

Date: October 25, 2026, America/New_York.

## Requested behavior and frozen subject

The user clarified that every generated component and all content it displays
must be English. An English SKILL document alone did not explicitly impose
that rule on later UI generation. This update adds an authored component-copy
contract to `SKILL.md`, `references/usability-and-color.md` and the invocation
prompt in `agents/openai.yaml`.

The final source/runtime/full subject has **19 files**, SHA-256
`565602a9d166c18e15f07dce0a47c2a8587089085159572ca0094084886471ba`.
The 42 interaction patterns, ten Nielsen principles and exact ColorSets remain
in place. Older design and cross-assistant subjects are retained separately.

The rule covers titles, navigation, controls, placeholders, tooltips, chart
labels, sample display data, help, validation, notifications, feedback states,
accessible names/live announcements, exports and native/terminal/text fallback
copy. Translate legacy display wording; preserve identifiers, protocol values,
proper names and original source records. Set authored HTML to `lang="en"`.
Inspect runtime states and accessible text rather than treating a declaration
or English source file as proof of displayed-language coverage.

Host-owned chrome, permission dialogs and operating-system controls remain
under the host's locale. Do not impersonate, recolor or translate those controls
or change account/OS language settings. Raw protocol identifiers and source
records are distinct from authored human-language messages. No such locale
or account changes were made.

## Existing component source and browser checks

The independent [component-copy audit](component-copy-audit-20261025.md)
inventories 25 source/config files across MCP Apps, Claude native fixtures,
Copilot terminal/webview fixtures and Codex protocol fixtures. It found no
non-English authored UI literals. It identified unbounded raw error forwarding
as a future display-language risk.

Current project corrections:

- Declare English on the MCP probe view and synthetic wrapper, live view,
  Codex HTML resource and all three VS Code webview templates.
- Use a fixed English retry message for widget connection errors; retain
  original diagnostic details in the console rather than the visible message.
- Use English rejection/action-recovery messages in the live widget while
  preserving its last value. Keep raw error diagnostics separate from UI copy.
- Add an English-language assertion and visible/accessibility-copy capture
  to the existing browser probe. Allow a distinct artifact output so the
  earlier empirical reports and screenshots remain unchanged.

The final existing MCP SDK/browser fixture passes **26/26** checks. It paints
English labels, expanded file-input help and error feedback, records an
English accessibility tree, and verifies narrow layout. Screenshots and raw
copy records are under
`projects/desktop-plugin-ui/artifacts/component-language-20261025/browser-final/`.
This is synthetic browser evidence, not installed-assistant acceptance. The
Codex fixture parses and declares English; the webview test source passes
`node --check`. No new Codex/Copilot/Claude host painting is claimed.

```powershell
$env:UI_PROBE_ARTIFACTS = '<absolute-project-artifacts>/component-language-20261025/browser-final'
# Run from projects/desktop-plugin-ui/mcp-probe:
npm run probe
```

The additional `language-probe.ts` browser check passes **27/27** on its first
attempt. It compiles the current widgets into their actual source templates
and uses a local synthetic MCP Apps host. Quoted foreign error fixtures exercise
failed initialization, invalid server results and a thrown display-mode request.
Visible recovery is English and the last value remains 8. Six captured states
include expanded capabilities/help and 360px layouts, with English visible and
accessibility snapshots and no foreign test-message leakage. All page network
requests are blocked; none occurred. There are zero page errors and three
expected console diagnostics. Component sources remain unchanged during tests.

Raw results and six screenshots are retained under
`projects/desktop-plugin-ui/artifacts/component-language-20261025/live-browser/run-001/`.
The exact command, run from the existing task package, is:

```powershell
npx --no-install tsx language-probe.ts
```

## Isolated language-selection study

The prompts provide clearly quoted Spanish legacy-copy fixtures as required
source/test data inside English task instructions. They request adaptation to
the loaded skill without supplying the required output language. Original
identifiers and codes must retain their exact spelling. Generated UI display
copy must follow the bundled language contract.

| Case | Prompt SHA-256 | Exact artifacts |
| --- | --- | --- |
| Contract smoke | `e85274ad991972fc26b1d26ec37955fd6e77634f0da7377a9a4535b9d7011b69` | `audit/language-contract.md`, `audit/language-contract.json` |
| Naturalistic component, three repetitions | `53a03c1e58adf321341c959be448d6d7ba2aa368c6a6ff381aee9cd30bf5d988` | `ui/status-panel.html`, `ui/component-copy.json` |

Use the existing deliberate `openai-codex/gpt-5.6-luna` exception after the
earlier Spark account rejection. All runs use JSON strict mode, exact-output
gates, false current-host/testing flags, clean read surfaces and unchanged
payloads. No additional provider calls, network, installs, host/account operation or locale
changes are permitted inside the cases. Any local browser preview remains
fixture evidence. This update consumes no Claude or Copilot inference.

The one contract and three naturalistic runs pass strict execution **4/4** and
the scoped authored-English criterion **4/4**. All retained outputs are first
attempts, with no reviewer repair, reroll or payload change.

| Case | Strict | Scoped English result | Bounded evidence |
| --- | --- | --- | --- |
| Contract smoke | 1/1 | 1/1 | Fourteen concrete copy categories, translated sample content, exact identifiers and honest host-locale boundaries; no source fixture echo. |
| Naturalistic component | 3/3 | 3/3 | All six artifacts inspected; English UI/accessibility/state/sample/native/TUI copy, `lang="en"` and preserved source identifiers. Spanish appears only in clearly source-only JSON legacy records in runs 1-2, not the rendered HTML. |

See the [contract review](english-contract-v1-luna-1.md) and
[naturalistic source/trace review](english-components-v1-luna.md) for exact
commands, run IDs, hashes, language selection and read surfaces. The contract
reads only its prompt, SKILL and report checker. All four runs observe Luna,
zero tool errors, exact outputs, false case-level host/testing booleans and
unchanged frozen 19-file bundles. Report checkers return no findings but check
zero citations here; they are not language classifiers.

Independent Playwright review of the generated HTML passes the scoped English
criterion for all three components at 1100px and 360px. It retains **91 actual
state captures** with visible text, accessible snapshots and screenshots,
including busy, invalid, error, cancelled, empty, saved, help/fallback and
available tooltip/export/explain states. No source artifact is modified. There
are zero page errors or page network requests. Raw evidence is under
`projects/desktop-plugin-ui/artifacts/component-language-20261025/generated-browser/`.
The [browser review](english-components-browser-20261025.md) distinguishes
inspected states from missing or blocked actions.

English acceptance is not full UI-quality acceptance. Preserve unrelated
findings: run 1's optional contrast numbers are inaccurate and its narrow table
scrolls; run 2 includes a decorative alpha shadow and omits an Explain action;
run 3 has a weak identifying border and unassociated tooltip description, with
its narrow tooltip intercepting an Explain click after export. No forced click
or DOM repair was used to turn that failure into a pass. These findings do not
clear the broader skill's validation gate.

## Repository and release boundary

The 20-check design verifier, pattern IDs, skill validator, independence and
payload checks pass. The scoped authoring audit passes matching 19-file
source/runtime/full profiles. Local sync/check passes all 19 final files.
The source/report helpers are unchanged by this language update; their earlier
53/53 and 33/33 script results are retained, not presented as new language
classifiers. They do not validate natural language, actual paint or usability.

Keep overall status **validating**. This scoped language change does not erase
the earlier exact-token-path error, cross-assistant factual/evidence-label
failures or pending real-host checks. See the
[Nielsen/ColorSet study](nielsen-colorsets-20261025.md) and
[cross-assistant report](cross-assistant-validation-20261024.md).
