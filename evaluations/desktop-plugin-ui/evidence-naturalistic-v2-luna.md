# Evidence-classification repair: naturalistic v2 Luna review

Date: October 25, 2026, America/New_York. These are three fresh first attempts
on the revised 23-file subject. The naturalistic prompt and independent
criteria are unchanged from v1; no previous output is available to the tested
agents. Preserve the [v1 review](evidence-naturalistic-v1-luna.md) separately.

## Result

| Run | Strict | Final typed checker | Semantic content | Allowed scratch/read scope | Manual / joint |
| --- | --- | --- | --- | --- | --- |
| 1 | Pass | Pass | Fail: missing execution support for a used capability fact | Pass | Fail / Fail |
| 2 | Pass | Pass | Pass, with recommendation caveat below | Pass | Pass / Pass |
| 3 | Fail: one out-of-range read | Pass | Pass | Pass | Pass / Fail |
| Total | **2/3** | **3/3** | **2/3** | **3/3** | **2/3 / 1/3** |

The frozen joint naturalistic threshold of at least 2/3 is **not met**. The
revised workspace scratch guidance eliminates the observed v1 outside-temp
routes in this cohort, and all three use the typed workflow. A passing final
checker still cannot establish complete factual coverage or erase tool errors.
No failed case was rerun and no tested output was repaired by the reviewer.

All exact artifacts exist, required fields and Boolean false task flags pass,
and all copied payloads remain unchanged. Independent checks pass **30 exact
path assertions, 29 explicit hex-binding assertions, 19 recomputed contrast
ratios and 30 H1-H10 ID/label checks**. The two-file typed checker passes 79
official URL checks and 71 normalized records across the cohort. URL checking
deduplicates each URL within a report rather than counting every text occurrence.

## Frozen identities and commands

- Runtime/source/full: 23 files, SHA-256
  `ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
- Helper SHA-256:
  `63fddc71df0b659b9d630487b73bcfe05f18b395a08b49398f75d07dfc01a80b`.
- Unchanged prompt raw SHA-256:
  `ee44ad5752083b38ea153182d63eb31955fb790e8c86969c01ebd42c3134a390`.
- Unchanged criteria raw SHA-256:
  `c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2`.
- Existing deliberate model exception: `openai-codex/gpt-5.6-luna`, high
  reasoning, JSON strict mode, 600-second timeout.

The source/copy prompt text matches, with the same raw/manifest LF-normalized
identity distinction documented in v1. Per-run manifests and independent
identity receipts preserve exact output hashes and the 23-file frozen hash.

| Run suffix | Duration | Completed tool calls | Observed Luna records | Retained tool errors |
| --- | --- | --- | --- | --- |
| `1` | 157.788s | 30 | 19 | Zero |
| `2` | 178.097s | 28 | 18 | Zero |
| `3` | 183.347s | 40 | 30 | One read error |

All `pi` subprocesses exit 0. Run 3's strict wrapper returns failure because
event 16240 requests read offset 175 for an artifact with 118 lines. Its final
artifacts and all other gates pass after recovery, but the original error
remains. Required independent event summaries confirm Luna identity, valid
event JSON, prompt-first reads and the same error; no forbidden reads occur.

Representative commands from the repository root, with `N` replaced by 1, 2
or 3. Retained IDs must not be reused:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-naturalistic.md --run-id 20261025-desktop-ui-evidence-naturalistic-v2-luna-N --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output offerings/recommendation.md --expect-output offerings/recommendation.json --expect-output-json-field offerings/recommendation.json::host_acceptance_verified=false --expect-output-json-field offerings/recommendation.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v2-luna-N/events.jsonl --output evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v2-luna-N/independent-event-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\/])assets[\/]examples([\/]|$)' --forbid-read-regex '(?i)^skills[\/](?!desktop-plugin-ui([\/]|$))' --forbid-read-regex '(?i)^(?:[A-Za-z]:[\/]|/|\\)'
uv run --script projects/desktop-plugin-ui/scripts/review-evidence-naturalistic.py --prefix 20261025-desktop-ui-evidence-naturalistic-v2-luna
```

## Semantic review

All six final artifacts were inspected. They cover queue search, details,
staged edits and Save/Cancel, a chart/table/text equivalent, refresh/recovery,
selected CSV and explicit Explain selection. Ownership and reload/reconnect/
failure plans separate client selection/drafts/preferences from authoritative
server state. English copy, the exact supplied identifiers, export/Explain
scope, all ten Nielsen labels and host-owned styling are preserved. Source
inspection and documentation stay nonexecuted; skipped Copilot sign-in is a
user report plus untested assistant acceptance. There is no Copilot login,
real-host UI action or user-study claim.

Expected policy decline, sandbox denial and no-renderer guards are represented
as passing checks when expectations match. A named handshake or nested-schema
attempt may carry a failed outcome with its explicit expected and actual result;
none is used to turn missing stock paint into a failed rendering action.
Protocol results, ordinary extension-host behavior, terminal UI and signed-in
assistant paint remain distinct. Ordinary webview script/CSP requirements are
not replaced by MCP App CSP metadata fields.

**Run 1 has a definite coverage failure.** Its native-canvas offering's
`version_evidence_scope` says “the observed CLI canvases:true capability” does
not establish VS Code paint. The ledger's 22 records contain only the bare SDK
consumer's all-false renderer values, conditional/documented VS Code canvas
contracts and a skipped Chat acceptance record. They contain no execution
record for the terminal connection's true canvas capability. A correct fact in
the bundle still needs support with its actual basis when used. Conditional
VS Code prerequisites or the different all-false SDK consumer cannot supply
that executed observation. This repeats a coverage gap, not an incorrect
automatically derived label or a hidden record-count requirement.

**Run 2 corrects that distinction.** Its `copilot-cli-no-mcp-apps` record
explicitly records the real terminal's `elicitation=true`, `mcpApps=false`,
`canvases=true`, `extensions=false`, separately from the bare consumer. Its
resource/form/policy facts are scoped to the named backend, and it offers a
conditional stock MCP App route rather than excluding direct IDE MCP.

There is one recommendation caveat. Run 2 says “For a guaranteed dashboard,
use a developer-owned frontend” and lists “custom frontend only if a painted
dashboard is required.” In the full same-client paragraph, it also offers a
matching optional `ui://` View after stock-frontend negotiation/paint checks.
This is treated as a recommendation for a controllable implementation when
stock acceptance is unverified, not as an assertion that an owned frontend is
the only possible UI route. The word “guaranteed” should not replace acceptance
testing of the owned frontend. No hidden preferred architecture or exact
wording requirement is used to reject the complete recommendation.

**Run 3's content passes.** It records the terminal capability flag in its own
execution record, treats stock frontend acceptance as not-run, retains the
optional Codex MCP App route, and scopes webview results to ordinary extension
tests. Its owned-client suggestion is likewise accompanied by an explicit
conditional stock route. Its one out-of-range read still rejects joint
acceptance even though content and final checking are sound.

Broader stock-paint wording is interpreted in its full version/layer context.
Historical inline chart paint is not silently erased, while a backend-only
test does not certify the proposed support-queue renderer or the current
package. General caution about not promising an untested widget is different
from a product-wide exclusion or an owned-client-only requirement.

## Helper, values and consistency checks

All three actually call the typed helper and reuse its normalized records and
rendered Markdown table; independent comparison finds matching tables. They
use the new optional report metadata assembly rather than system-temp Python
builders. The final typed checker is run after both exact outputs are written,
and each agent inspects its successful result. The independent reviewer
repeats typed checking without altering any final artifact.

| Run | Typed records | URL checks | Exact paths | Hex bindings | Ratios | H labels |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 22 | 30 | 10 | 10 | 7 | 10 |
| 2 | 26 | 26 | 9 | 9 | 6 | 10 |
| 3 | 23 | 23 | 11 | 10 | 6 | 10 |

The project reviewer independently reads the frozen palette's leaves and
recomputes contrast with 1e-9 tolerance. The extractor was extended for run 3's
valid `path = #hex` strings and named ratio strings; its initial incomplete
counts were an evaluator-format limitation, not a missing test by the agent.
No tested artifact or frozen criterion changed. Font-family quoting is
presentation-equivalent; no font rendering or download is claimed.

All explicit ratios match. Dark red/dark ink replaces sole light-gray focus,
and ordinary error text uses a permitted darker value; red stays an accent
where red-on-pink would fail ordinary-text contrast. These are token arithmetic
and a design plan, not rendered accessibility acceptance. The source helper,
typed checker and heuristic IDs pass their scoped checks but cannot substitute
for factual coverage or a real renderer.

## Full command/write-path audit

This review inspects every write/edit path and shell command, not just read
events. Run 1 uses `work/raw_facts.json`, workspace ledger files and final
`offerings/` outputs. Run 2 uses `work/facts.json`, regenerates the ledger after
an in-session metadata correction, copies the final JSON into `offerings/`,
and removes only relative `work/`. Run 3 uses relative `work/` JSON validation,
ledger/metadata generation, final output updates and relative cleanup.

No shell command targets POSIX `/tmp`, system Temp, credentials, global
configuration or another provider. No outside scratch creation, read or cleanup
from v1 recurs. Source catalog listing and design helper calls are local;
diagnostic unknown-token findings are corrected without tool errors. All
non-output reads stay in the copied skill and its needed resources, except
the canonical `../prompt.md`. No acceptance fixture, gallery, sibling skill,
repository source or file above 50 KB is used as runtime reference material.

Raw manifests, events, strict gates, independent event/content reports and
identity receipts are retained under
`evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v2-luna-{1,2,3}/`.
The reviewer performs no outside-temp inspection or cleanup. This report makes
no canonical, backlog, account or original-output edits and clears no broader
release/live-host gate. OpenAI-only forward inference is separate from zero
Claude/Copilot model usage and the preserved no-Copilot-sign-in choice.
