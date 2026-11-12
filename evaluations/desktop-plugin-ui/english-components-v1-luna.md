# English component-copy naturalistic evaluation, v1

Date: 2026-10-25. Skill: `desktop-plugin-ui`. Three fresh isolated Pi 1.4.0
sessions used the documented `openai-codex/gpt-5.6-luna` exception with high
thinking after the completed static gates. No retry, canonical change or
post-run artifact repair was made. The parent
[English component contract record](english-components-20261025.md) covers the
rule and separate existing-component checks.

## Frozen subject and scoped outcome

All three manifests record the same 19-file source/runtime/full payload:
`565602a9d166c18e15f07dce0a47c2a8587089085159572ca0094084886471ba`.
The unchanged [prompt](../pi-prompts/desktop-plugin-ui-english-components.md)
has SHA-256
`53a03c1e58adf321341c959be448d6d7ba2aa368c6a6ff381aee9cd30bf5d988`.
It supplies quoted Spanish legacy copy and asks adaptation to the loaded skill
contract. It requests `language` without prescribing its value or supplying
expected English answers. The harness gates exact outputs and two false
booleans; no hidden language-value format gate was added.

**Strict harness: 3/3 pass. Required-model trace: 3/3 pass. Manual source
English-copy acceptance: 3/3 pass. Source-identifier preservation: 3/3 pass.**
Every HTML declares `lang="en"` and every JSON independently chooses
`language: "en"`. This scoped language result does not mean all UI quality,
accessibility, contrast or runtime behavior passed. Broader defects and the
separate browser verification boundary remain explicit below.

| Suffix after `20261025-desktop-ui-english-components-v1-` | Strict | Source language | Identifiers | Read calls | Duration |
| --- | --- | --- | --- | --- | --- |
| `luna-1` | Pass | Pass | Pass | 7 | 102.846 s |
| `luna-2` | Pass | Pass | Pass | 5 | 91.649 s |
| `luna-3` | Pass | Pass | Pass | 6 | 86.022 s |

Every run writes the exact nonempty `ui/status-panel.html` and
`ui/component-copy.json`, keeps `host_acceptance_verified` and
`task_empirical_tests_performed` false, and leaves its copied skill unchanged.

## Source and copy review

All six final artifacts were read in full, including inline JavaScript and
dynamic message templates. Review covers headings, labels, buttons,
placeholders, help, tooltips, accessible names, live-region messages, sample
titles and enum labels, default/busy/invalid/error/cancelled/empty/success
states, native-control equivalents and terminal/text fallback strings.
All authored display wording is English. There is no Spanish in any HTML
source or its dynamic message strings.

Run 1 retains the supplied Spanish under `legacy_source_record`, explicitly
marked source material rather than authored display copy. Run 2 retains it
under `source_legacy_copy`, with the same source/display distinction documented
elsewhere in that record. Run 3 omits a duplicate legacy block. Those retained
source records are not language failures and were not modified. Outside the
source-only blocks, the review inspected 290, 219 and 206 JSON string values,
respectively; a contextual Spanish-copy scan found no additional candidates.

All three preserve `T-104`, `high`, `pending`, `queue_update_priority` and
`E_INVALID_PRIORITY` as source/protocol values. Display labels and sample
subjects are adapted separately. None invokes the tool or changes a host's
locale. Browser/OS-owned native control chrome remains outside authored-copy
control; declaring document language is not proof of changing host locale.

Every preview has local handlers for search/selection, staged priority changes,
save/cancel, refresh success/failure, invalid input, empty results and status
feedback. Source reachability is not an execution result. The original Pi
sessions did not open a browser or installed assistant. Independent browser
auditing subsequently adds **3/3 observed English-copy passes across 91 state
captures at 1100px and 360px**, including visible text, accessible trees and
relevant UI attributes. See the separate
[generated-component browser report](english-components-browser-20261025.md).
It retains failed/unavailable actions and does not overwrite the original task
booleans or source artifacts. No assistant-host acceptance follows from the
local browser result.

## Broader quality limits retained

- **Run 1, numeric evidence defect.** Optional JSON contrast approximations at
  `workspace/ui/component-copy.json:233` through the following three entries
  contain four incorrect claims: `#333e48`/white and its inverse are reported
  as 10.44:1 rather than **10.918239:1**; `#696969`/white is 5.74:1 rather than
  **5.489815:1**; `#333e48`/`#ffccd5` is 8.96:1 rather than **7.720737:1**.
  Independent relative-luminance calculations retain those actual values.
  These are agent factual/artifact findings, separate from the passing language
  result. They were not repaired or silently certified by the checker.
- **Run 2, decorative paint caveat.** All authored hex literals belong to CS1,
  but `workspace/ui/status-panel.html:44` adds
  `rgba(0, 0, 0, .08)` as a shadow. This creates composited decorative paint;
  exact base-token membership does not establish exact rendered palette pixels.
  Source review also confirms the legacy Explain action was omitted from the
  generated controls. These are broader styling/completeness limitations, not
  non-English copy.
- **Run 3, accessibility/contrast caveats.** The source uses `#9c9c9c` for input
  borders (`workspace/ui/status-panel.html:71`), whose ratio to white is about
  2.745446:1. If it is the essential identifying boundary, it falls below 3:1.
  Its export tooltip is visually reachable by hover/focus, but the button at
  line 195 has no `aria-describedby` association with the tooltip at line 196.
  The separate browser audit confirms that missing association and retains a
  narrow pointer sequence where the visible tooltip intercepted Explain
  selection after export, causing a timeout. No forced click or repair was used.

The browser audit also retains run 1's 620px table content inside a 306px narrow
container and unverified native tooltip-popup paint. It confirms run 2 has no
Explain selection control. Language success does not clear these layout,
functionality or accessibility limitations.

All base HTML hex literals are CS1 values, and each JSON selects the default
CS1 with host-owned/native/accessibility styling boundaries. That limited
finding is not a full contrast, pixel, responsiveness or accessibility pass.
Source records keep browser fixtures distinct from installed-host rendering,
server authority, persistent storage, permissions and OS file delivery.
No user study or assistant-host acceptance is established.

## Commands and checker limits

The following command ran in three fresh processes, varying suffix 1, 2 and 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-english-components.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-english-components-v1-luna-1 --expect-output ui/status-panel.html --expect-output ui/component-copy.json --expect-output-json-field 'ui/component-copy.json::host_acceptance_verified=false' --expect-output-json-field 'ui/component-copy.json::task_empirical_tests_performed=false'
```

Each required-model trace was separately summarized, varying suffix:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-english-components-v1-luna-1/events.jsonl --output evaluations/runs/20261025-desktop-ui-english-components-v1-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
```

Each agent ran the copied report checker on both final files and inspected its
clean result. An independent rerun also passes for every run:

```bash
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py ui/status-panel.html ui/component-copy.json
```

Each result has zero findings and replacements, **zero official URLs and zero
historical rows checked**. It confirms that its limited contract has no findings;
it does not validate display language, numeric contrast, accessibility or UI
function. Language acceptance comes from the separate full source review.

## Trace, hashes and retained evidence

All strict and required-model summaries pass: only `gpt-5.6-luna`, valid event
JSON, zero runtime tool errors, prompt-first reads, exact files and unchanged
copied payloads. Reads are limited to the prompt, SKILL, selected compact
chat/bridge/design references, active CS1 asset and, where used, the report
helper. There are no examples, sibling skills, repository documents, project
artifacts or external read surfaces. Complete command traces contain only
local inventory, helper help/diagnostics, JSON validation and a scan for network
APIs. No task-level network/provider call, installation, deployment, account,
configuration or installed-assistant operation occurred.

| Run | Input | Output | Cache-read | Total trace tokens |
| --- | --- | --- | --- | --- |
| 1 | 31,632 | 14,179 | 178,560 | 224,371 |
| 2 | 35,236 | 12,851 | 100,608 | 148,695 |
| 3 | 27,309 | 12,332 | 121,216 | 160,857 |

These are OpenAI Pi aggregates; no Claude/Copilot model allowance was consumed.
Final HTML/JSON artifact SHA-256 values are:

| Run | HTML | JSON |
| --- | --- | --- |
| 1 | `215620c71673fa21ced251b2db9b9d6a966e1b7809fb837b01f4a470761291a1` | `bafe0cc97f79ff21bee5a5cb660f1bf0a94870d8b99cacf83751f9cee936a196` |
| 2 | `483a65334c69cf304e160c63e320d66402958638c9036ac9a6d2d919abe76f7c` | `03f139576c9831d9a5929542b924f0b3515ac06ca94df9f88d23d9807221d70f` |
| 3 | `a26fcea22a77c570e9b696936346b274000d3084f00d624ae8116f186f7d0ea9` | `9289330230f236f6506ff8ed467712255dce411b68c3bd8f43531fa885e72df5` |

Raw workspaces, traces, manifests and per-run `independent-source-review.json`
remain under
`evaluations/runs/20261025-desktop-ui-english-components-v1-luna-{1,2,3}/`.
The combined source inspection is
`evaluations/runs/20261025-desktop-ui-english-components-v1-source-inspection.json`.
No earlier design or cross-host cohort was substituted or pooled into this
scoped result.
