# Write a capability report from evidence

Use this procedure when a recommendation reuses dated observations. It does
not require executing new host tests. Keep current-task acceptance flags false
when the task only reviews bundled evidence.

## Contents

- [Derive labels from the evidence basis](#derive-labels-from-the-evidence-basis)
- [Build the evidence ledger first](#build-the-evidence-ledger-first)
- [Keep mechanisms and versions attached to facts](#keep-mechanisms-and-versions-attached-to-facts)
- [Finish without avoidable execution errors](#finish-without-avoidable-execution-errors)

## Derive labels from the evidence basis

Use one atomic claim per typed record. The basis describes how the claim is
supported; the label describes the conclusion permitted by that basis.

| `basis` | Additional required fields | Derived `evidence` | Execution state |
| --- | --- | --- | --- |
| `execution` | `action`, `expected`, `actual`, `outcome` (`pass` or `fail`) | `observed-working` for pass; `observed-failed` for fail | `executed` |
| `source-inspection` | `source` locator | `documented` | `not-run` |
| `primary-documentation` | `source` locator | `documented` | `not-run` |
| `user-report` | `reporter`, `reported_result` | `untested` by the agent | `not-run` |
| `not-run` | `reason` | `untested` | `not-run` |
| `conditional` | nonempty `prerequisites` array | `conditional` | `not-run` |
| `explicit-exclusion` | authoritative `source` and explicit `exclusion` | `unsupported` | `not-run` |

Every record also needs nonempty `id`, `claim`, `host`, `surface`, `version`,
`layer` and `basis` strings. Write `unknown` for an unrecorded version; do not
borrow another capture's version. A source locator identifies documentation or
an inspected file, not an execution receipt. Preserve the reported result of a
human observation without upgrading automated acceptance. An inferred limit
is conditional or untested, not an explicit exclusion.

An executed check must name what was attempted and compare its expectation
with the actual result. An expected stale-edit rejection, denied top-document
access or automatic policy decline is a **passing negative check**. An unmet
expectation is a failed check. If no paint/readiness action ran, its absence is
`not-run`; never manufacture a failure from “not established.” Inspecting an
Expand handler supports “source declares a fullscreen request,” not “the
fullscreen request was observed.” Split declaration and execution into records.

Prepare raw facts as `{"records": [...]}` outside the skill, then run:

```powershell
uv run --script <bundle>/scripts/evidence_ledger.py --input work/facts.json --output work/ledger.json --markdown work/ledger.md
```

Inspect `passed:true` before using outputs. The helper derives `evidence`,
`classification` and `execution_state`; conflicting supplied labels, mixed
basis fields and incomplete records are findings. Diagnostic mode exits zero
even on findings; reserve `--fail-on-findings` for clean CI. Invalid data creates
no outputs. Copy the normalized `evidence_records` into the final report and
reuse the rendered table rather than hand-classifying it again. Keep the raw
input distinct from output paths; outputs inside the bundle are refused.

Put final non-ledger fields in an optional top-level `report` object in the
input: task-level false flags, factual findings, sources, state plans or
heuristic rows. The CLI emits those fields with normalized `evidence_records`
and a protected `evidence_validation` object in the final JSON file. Its stdout
keeps the original `passed`/`findings` diagnostics. Domain `report.findings` is
allowed; the reserved keys `records`, `report`, `passed`, `schema_version`,
`evidence_records` and `evidence_validation` are refused there. Keep factual
`evidence_ids` references accurate and run the typed checker after generation.
Write valid JSON with the file tool; do not paste JSON Boolean/null literals
into Python source or build a long shell heredoc merely to merge metadata.

The helper checks declared structure. It cannot determine whether prose is
true, sources were really read, an asserted outcome is accurate, or a claim
was omitted. Independently compare those facts against the input evidence.

## Build the evidence ledger first

1. Select only claims needed for the decision. Build their typed ledger before
   prose. Include executed checks, source declarations, user reports and not-run
   checks with their own bases. New reports need no `historical_observations`
   array; if an older contract requires one, reserve it for executed records.
   Do not force every claim into an observed label to satisfy that legacy array.
2. Keep records atomic. Split different bases, clients, versions, layers and
   outcomes, including source code versus a real callback versus visible paint.
3. Write the recommendation using record IDs. Link factual findings with
   `evidence_ids: ["record-id"]`; a proposed next step is not an observed fact.
   Put the next unperformed check
   under `conditional` or `untested`; do not turn a recommendation into an
   observation. Use `documented` for a source contract without an execution.
4. Read BOTH final outputs and reconcile every empirical statement against the
   ledger. Check prose, offering conditions, limits, state and styling sections,
   not only paragraphs called "history". A nearby filename is not a ledger row.

Frequently missed observations include an SDK's false capability flags,
Restricted Mode/sign-in readiness, a returned chart's metadata without paint,
the serving process's negotiated extension, schema normalization, CSP refusal,
and reload/disposal state. If these facts are used, record their rows. If they
are unnecessary, omit them rather than expanding the report with unused tests.

For example, a raw input record for the historical SDK negotiation is:

```json
{
  "id": "copilot-sdk-bare-consumer",
  "claim": "The bare SDK consumer advertised no MCP App or canvas renderer.",
  "host": "GitHub Copilot CLI",
  "surface": "SDK consumer without a renderer",
  "version": "CLI 1.0.103; SDK 1.0.26",
  "layer": "capability negotiation",
  "basis": "execution",
  "action": "Initialize the SDK consumer without a renderer.",
  "expected": "mcpApps=false and canvases=false",
  "actual": "mcpApps=false and canvases=false",
  "outcome": "pass"
}
```

A normal refusal under an approval policy is not automatically a broken UI.
Describe the expected and actual action. A protocol flag may negotiate
successfully while renderer acceptance remains untested.

## Keep mechanisms and versions attached to facts

| Fact | Correct scope | Do not transfer it to |
| --- | --- | --- |
| MCP Apps `connectDomains`, `resourceDomains`, `frameDomains` | That MCP App host's resource metadata/CSP contract | Ordinary VS Code webview configuration |
| VS Code `WebviewOptions`, `localResourceRoots`, `asWebviewUri`, HTML CSP | Ordinary extension webview | MCP Apps resource metadata |
| CLI `canvases:true` | The named CLI/SDK connection's negotiation | VS Code's local Copilot Agent Host canvas pixels |
| Disposed/new webview loses its state | The tested extension-host lifecycle | Durable server data or a serializer not tested |
| A historical desktop chart capture with an unrecorded image build | That capture and known route | The currently installed package/core inventory |
| Bare SDK consumer has no renderer | That consumer configuration | All Copilot hosts or installed app features |

Use [capability-offerings.md](capability-offerings.md) to select a route and the
matching host reference for its contract. For actual MCP Apps, read the host's
CSP rules; for ordinary webviews, use the VS Code webview API. Never borrow one
mechanism's field names to make another mechanism appear configured.

## Finish without avoidable execution errors

Use the task's explicit writable directory or relative `work/` inside the
current task workspace for all raw inputs, scripts and generated files.
Create it with `Path(...).mkdir(parents=True, exist_ok=True)` or the native
equivalent. A workspace-only task does not authorize system temp, `/tmp`,
`%TEMP%`, bare `mktemp` or default `tempfile` paths. If a temporary-file API is
needed, pass its directory explicitly within the permitted workspace. Do not
assume that a shell's `/tmp` resolves to the same location in Windows Python.

For JSON repairs, load the object, change the intended fields and serialize
with `json.dump`/`json.dumps`; do not rely on a long ambiguous text replacement.
Preserve the exact requested output paths. The bundled helper's explicit URL
replacement handles copied citations; it cannot add missing semantic evidence.

Run `check_reports.py report.md report.json --require-evidence-records` on both
completed artifacts and inspect `passed:true` and a nonzero typed-record count.
Final JSON needs all three normalized fields, not only raw input records.
`evidence_ids` references must resolve. Legacy-only checking is explicitly
reported as `legacy-labels-only` and does not validate declared execution.
Then independently verify that every used empirical fact has a correctly
scoped row, that sources support the stated mechanism, and that exact token
paths/contrast values came from `design_values.py`. A clean checker alone
does not establish complete history, factual truth, accessibility or host paint.

Use the ledger input's optional `report` object for final report fields instead
of building a second JSON serialization script. Repair inputs and rebuild the
ledger rather than editing derived labels. Copy-only inventories without
evidence claims can omit the typed flag; they prove no runtime acceptance.

For a copied URL error, use the helper's all-occurrence replacement:
`uv run --script <bundle>/scripts/check_reports.py <report.md> <report.json> --replace-url "<wrong-url>" "<exact-catalog-url>"`.
Choose the exact target from `check_sources.py --list-sources`. The helper
refuses bundle writes and validates JSON before writing. Use default diagnostics
during repair; reserve `--fail-on-findings` for clean CI. Use `--allow-url` for a
new primary source only after independently verifying that exact URL. No
checker browses or authorizes an external action.
