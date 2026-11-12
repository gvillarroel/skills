# Typed evidence repair: contract and boundary review

Date: October 25, 2026, America/New_York. Skill: `desktop-plugin-ui`.
Subject: 23-file evidence-workflow repair. These are two distinct first
attempts, not reruns of prior subjects. The deliberate
`openai-codex/gpt-5.6-luna` exception continues; no Claude or Copilot inference
was used. No evaluator changes were made to either tested output.

## Results

| Case | Strict | Typed checker | Independent manual | Joint |
| --- | --- | --- | --- | --- |
| Synthetic contract | **1/1** | **1/1** | **1/1** | **1/1** |
| Status boundary | **1/1** | **1/1** | **1/1** | **1/1** |

The contract completes in **51.022 seconds**, with 15 tool calls, 11 Luna
model records and zero tool/event errors. The boundary completes in
**127.318 seconds**, with 25 tool calls, 17 Luna model records and zero
tool/event errors. All strict gates pass: exact nonempty outputs, valid
events/model/read surface, false JSON acceptance flags and unchanged skill.
The required independent event summaries also pass.

The independent checker checks **10 typed contract records** and **15 typed
boundary records**. It finds zero issues. Contract has no public URLs because
its sources are supplied lab locators; boundary checks four official URL
occurrences across its two outputs. Zero URL checks in the contract are not
presented as public-source verification.

Independent classification and rendering checks confirm that all final
records equal their normalized form and that both Markdown ledger tables
exactly match the helper's rendered table. Boundary has eight factual findings
with 16 supporting `evidence_ids`, all resolving to records. Passing the helper
is structural evidence; the manual findings below establish this scoped
acceptance.

## Frozen identities

The copied runtime for both cases contains **23 files**, SHA-256
`a06c9f918308160272427d8a97f40d19ebfa82db65a7f2ff0a5571406f3a1799`.
The source was frozen and hashed before launch. Each manifest independently
matches that identity, and post-review comparisons preserve it.

| Input | SHA-256 |
| --- | --- |
| Contract prompt | `fa2e1a287c431754549c93d86a97c36bb379e3934c86f1f784789b6ffb012838` |
| Boundary prompt | `441c75ee394a7e4f2a2e8ef95235c54deb62099f1577d5444768855508c6716e` |
| Pre-frozen criteria | `c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2` |

Inputs are
[the contract prompt](../pi-prompts/desktop-plugin-ui-evidence-contract.md),
[the boundary prompt](../pi-prompts/desktop-plugin-ui-evidence-boundary.md) and
[the independent review criteria](evidence-repair-review-criteria.md).
The criteria were evaluator material and were not supplied to the agents.

| Run | Exact outputs and final SHA-256 |
| --- | --- |
| `20261025-desktop-ui-evidence-contract-v1-luna-1` | `audit/evidence.md`: `d9962b546e94e9faa46e4e0e82a2da80548747c0860997c21d1d60f9ccf28f71`; `audit/evidence.json`: `95cb11a63fbee14dc552f65a987c2fa1154001c18286ab1c5a44cdc03d96e807` |
| `20261025-desktop-ui-evidence-boundary-v1-luna-1` | `review/status.md`: `10cfb7235ade380c63346f3d00840d96c4ab3c55469887a02d21fecf9c41ea7c`; `review/status.json`: `c975781cb44536d283601e05be82414e12450a249cb161eb408aca2b0f8701a1` |

The manifest prompt hashes refer to the original source bytes. The harness
copies Windows CRLF prompts; normalized copied text exactly equals each source.
`independent-final-identities.json` in each run records both byte hashes and
newline counts. Neither difference is a changed instruction or reroll.
An initial evaluator-only identity extraction used Windows' implicit cp1252
text encoding and failed on a smart quote. Explicit UTF-8 corrected that
read; neither tested artifact nor the prompt was modified. The correction
is recorded in the independent identity receipts, separately from the
error-free Pi traces.

Both final JSON files contain their requested fields and literal Boolean
`host_acceptance_verified:false` and `task_empirical_tests_performed:false`.
The contract's synthetic execution receipts classify supplied lab notes;
they do not assert new installed-product tests by the agent.

## Contract manual review

Ten atomic records represent all eight supplied notes. Additional records
separate an unrecorded handler execution from its declaration and unchecked
canvas prerequisites from the conditional proposal; there is no hidden row
minimum.

| Supplied fact | Independent finding |
| --- | --- |
| Inspected `widget.ts:40` fullscreen call | `source-inspection` derives `documented`, `not-run`; a separate record preserves the unrecorded execution. |
| Inline resource view in Contract section 2 | `primary-documentation` derives `documented`, `not-run`. |
| Tester reports visible chart, no automated capture | `user-report` preserves reported visibility, derives `untested`, `not-run`, and leaves capture version explicitly unknown. |
| Paint skipped without a signed-in session | `not-run` derives `untested`; no failed paint result is manufactured. |
| Expected stale rejection and revision 8 retained | Genuine supplied action/expectation/receipt match; `outcome:pass` derives `observed-working`. |
| Save expected revision 9, got unavailable and revision 8 | Supplied expectation is unmet; `outcome:fail` derives `observed-failed`. |
| Proposed canvas prerequisites unchecked | `conditional` preserves both prerequisites; a separate `not-run` record preserves that neither was checked. |
| Contract section 4 excludes camera access | `explicit-exclusion` derives `unsupported` within Lab UI Host 1.4.2's fixture build. |

The known lab version remains attached to its contracts and receipts. The
human-report row conservatively identifies the unrecorded capture version as
unknown without inventing an automated capture. All prose is English.

The trace actually invokes `evidence_ledger.py`, then reads its generated
outputs. The agent adds requested final metadata and fixture-source locators
without changing derived record classifications or the generated table. Its
final typed-mode report check passes and it reads both final artifacts.
The evaluator's independent normalization and table equality checks pass.
No unsupported real-product capability or new UI/contrast claim appears.

## Boundary manual review

The five draft errors are corrected with appropriately scoped records:

1. **Missing acceptance is untested.** Copilot readiness/paint is not labeled
   as an observed failure. The later cleared Restricted Mode, remaining model
   sign-in gate and user's choice to continue without sign-in are preserved.
2. **Activation is an attempt.** The memo retains orderly host termination and
   no observed failure stack, while refusing to infer signed-in readiness or
   paint. It does not classify the proposal mismatch as fatal or harmless.
3. **Source is not execution.** The Expand handler is documented source with
   `execution_state:not-run`. There is no manufactured request or accepted
   fullscreen transition.
4. **Visibility is not control acceptance.** User-reported visibility, a
   separate documented desktop capture and an actually failed controller bind
   have different records/bases. The controller outcome is a specific failed
   check, not a rendering exclusion. Live controls remain untested.
5. **The stale-edit statement has no receipt here.** It is represented as
   `not-run`; no real guard result is invented or borrowed from another test.

The memo also distinguishes ordinary native extension-host checks from signed-in
Copilot Chat and identifies the 24-check CS1/English result as real MCP plus
offline synthetic-browser fixture evidence. Unknown versions remain explicit;
known ordinary-webview inventory is qualified as on-disk/runtime evidence.
The documented inline-only VS Code MCP Apps contract does not become a Codex
mode restriction. Exact primary URLs match the bundled catalog.

Every factual finding has resolving `evidence_ids`; the actual records support
their claims. The memo gives future checks conditionally and explicitly leaves
them unperformed. It respects the current no-sign-in choice. Language and CS1
remain authored-fixture boundaries; no host paint, contrast acceptance or user
study is invented. No design, heuristic checklist or numeric calculation was
required or added.

One temporal phrasing caution does not change this case's acceptance: the
controls-not-run record repeats the earlier pre-expansion reason, while the
memo separately records the later transient listing/bind failure. Naming the
earlier versus later attempt would be clearer. The current outcome remains
correctly untested, with the failed binding and reported expansion preserved.

The trace uses the classifier twice, repairing raw input facts before final
assembly rather than editing derived classifications. It reuses the helper's
table exactly. The agent removes its own scratch `work/` folder after final
checking; the raw write/repair payloads and helper output remain in the events.
The evaluator does not recreate or alter those scratch files or final outputs.

## Isolation and retained evidence

Both traces read the prompt first, then the entry point, then focused bundled
resources. Contract reads the evidence/report-authoring references and the
two deterministic script sources. Boundary reads the relevant Codex/Copilot
and report/evidence references plus the language/color reference and CS1 asset
for its requested styling boundary. No gallery, acceptance fixture, sibling
skill, repository/project document or file above 50 KB is read in normal use.

Only task-owned raw facts, ledger intermediates and requested outputs are
written. The observed commands run the bundled classifier/checkers, source
catalog/help and local output inspection/assembly. No network, account,
sign-in, extra provider, host/app/global operation or UI test is present.
The complete shell-command audit finds no generic `tempfile` use, absolute
output path or external system-Temp write: classifier outputs are the explicit
task-local `audit/` or `work/` paths; the remaining commands are read-only
inspection/checking and the boundary's own scratch cleanup.
All unsuccessful earlier subjects remain untouched and unpooled.

Raw evidence remains under each corresponding `evaluations/runs/<run-id>/`:
manifest, events, stderr, original final outputs, harness gate reports,
`independent-event-summary.json`, `independent-artifact-review.json` and
`independent-final-identities.json`. This durable review adds no canonical or
backlog edits. These two passes do not establish the other repair-cohort case
thresholds, clear older failures or certify actual assistant controls.

## Commands

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-contract.md --run-id 20261025-desktop-ui-evidence-contract-v1-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output audit/evidence.md --expect-output audit/evidence.json --expect-output-json-field audit/evidence.json::host_acceptance_verified=false --expect-output-json-field audit/evidence.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-boundary.md --run-id 20261025-desktop-ui-evidence-boundary-v1-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output review/status.md --expect-output review/status.json --expect-output-json-field review/status.json::host_acceptance_verified=false --expect-output-json-field review/status.json::task_empirical_tests_performed=false --timeout-seconds 600
```

Run the required event summary for each run ID, substituting its exact ID:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/independent-event-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
```

Independent checker invocations use the unchanged copied helper:

```powershell
uv run --script evaluations/runs/20261025-desktop-ui-evidence-contract-v1-luna-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-evidence-contract-v1-luna-1/workspace/audit/evidence.md evaluations/runs/20261025-desktop-ui-evidence-contract-v1-luna-1/workspace/audit/evidence.json --require-evidence-records --fail-on-findings
uv run --script evaluations/runs/20261025-desktop-ui-evidence-boundary-v1-luna-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-evidence-boundary-v1-luna-1/workspace/review/status.md evaluations/runs/20261025-desktop-ui-evidence-boundary-v1-luna-1/workspace/review/status.json --require-evidence-records --fail-on-findings
```

Completed IDs are immutable. A later experiment needs a new ID and separate
identity; do not reuse these commands as an instruction to overwrite evidence.
