# Plugin authoring and interaction quality revision

Date: October 25, 2026, America/New_York. The user requested a skill for creating
plugins across Claude Desktop, ChatGPT Desktop, Codex, Pi extensions and Claude
Code, with useful interactions, less complexity and Nielsen review.

The existing `desktop-plugin-ui` bundle remains the owner. Its new authoring
route creates runnable source and appropriate packaging rather than stopping
at a capability comparison. Overall backlog status remains `validating`:
this scoped revision does not close earlier semantic failures or live-host gaps.

## Reusable changes

- [Entrypoint](../../skills/desktop-plugin-ui/SKILL.md) and discovery metadata
  explicitly route plugin creation for the five requested environments.
- [Authoring](../../skills/desktop-plugin-ui/references/plugin-authoring.md)
  distinguishes Claude Chat from Code, local ChatGPT Desktop from remote
  connections, host-specific packaging, direct deterministic commands and
  optional model reasoning. Multi-host plans share contracts and reviews.
- [Pi](../../skills/desktop-plugin-ui/references/pi-extensions.md) supplies a
  runnable TypeScript native command, argument fallback, safe cancellation,
  local loading and current TUI/RPC/JSON/print distinctions. `hasUI` alone
  does not establish custom terminal UI support.
- [Interaction quality](../../skills/desktop-plugin-ui/references/interaction-quality.md)
  defines task completion, action/state ownership, relevant recovery checks,
  deterministic actions and a bounded inspect/fix/recheck/simplify loop.
  Complexity counts support task completion and error prevention; fewer clicks
  alone do not establish usability. H1-H10 apply to actual interactions and
  do not require ten additional controls.
- The source checker recognizes exact Pi primary ownership and retains
  exact-URL gating, rejecting unknown paths and spoofed hosts/owners.
  Existing English, ColorSet 1 default, explicit ColorSet 2, host-owned
  styling and typed evidence-report boundaries remain.

Primary OpenAI packaging/Desktop/MCP and release-pinned Pi sources were
rechecked. Exact URLs live in the new references. Nielsen's original source
was fetched; no user study or current host-wide paint certification follows.
No published gallery or pattern ID changed; Pages publication is not part of
this revision.

## Frozen subjects and model

| Subject | Files | Source/runtime/full SHA-256 | Scope |
| --- | --- | --- | --- |
| V1 authoring | 26 | `2eed59901630cd5c552e248c1e719ae53a2624365f0a1252f40a867dfb3cdefb` | Contract, naturalistic 3, boundary, generalization 3 |
| V2 compact planning | 26 | `ed3f7529ae344b2bf9c29dbb73c2e3a787c99ed1ce39bca769dc747588fb66d7` | Fresh contract and generalization 3 |

Requested/observed forward model: `openai-codex/gpt-6.1-sol`, medium, Pi 1.4.0,
Windows, strict JSON runtime payload. Spark was retried first and rejected
before any tool or output: `20261025-plugin-build-contract-spark-2`, with the
account/provider unsupported-model error and no token usage. Its earlier
pre-citation-integration payload hash is
`8312bec407cd5159e0f3dba2c4a617b75de781a163c7e3932f44a97280cf4c66`.
This is a retained infrastructure failure, not a Spark pass. The existing Sol
exception is recorded per run; no global model setting changed.

The [frozen criteria](build-interactions-review-criteria.md),
[independent artifact review](build-interactions-artifact-review.md) and
[metadata routing control](plugin-build-routing-20261025.md) contain separate
acceptance evidence. Naturalistic/generalization require at least 2/3 joint
passes; deterministic contract and boundary require 1/1. Do not pool subjects,
model cohorts or time budgets.

V1 passes 6/8 joint and 8/8 document/behavior review. Contract is 1/1,
naturalistic 3/3, boundary 1/1; generalization is 1/3 and misses its threshold.
Two generalization attempts produced complete artifacts but exceeded the
360-second budget during final writing/checking: 373.091 and 442.903 seconds
total harness duration. Retain them as agent/task-workload time-budget failures,
not as successful runtime exits or proven process-hang defects.

The follow-up changes only the entrypoint and authoring reference: use one
shared state/domain/heuristic contract, small adapters, JSON for precise fields
and prose for decisions, and deeper catalogs only for unresolved questions.
A blueprint uses scoped source notes rather than an automatic second claim
ledger. Prompts, model, 360-second budget and acceptance thresholds are unchanged.
V2 outcomes are recorded separately in the independent artifact review.

V2 compact planning meets its generalization threshold at **2/3 joint**:
repetitions 1 and 3 pass strict and independent review in 347.579 and 359.904
seconds. Repetition 2 retains a 387.485-second timeout. The fresh contract
artifact passes 34/34 behavioral checks and manual review, but two agent tool
errors fail its strict event gate, so contract is **0/1 joint** and the scoped
V2 cohort is **2/4 joint**. No whole-skill release pass is claimed. The two
contract errors were an absent optional `tsc` probe returning exit 1 and an
initial inline fixture syntax error; the model corrected the fixture, which
does not erase the observed errors. No extension defect was independently found.
All four V2 artifacts pass independent semantic review. In the three blueprint
samples, required outputs total 183,325 bytes for V1 versus 161,762 for V2;
observed unique read-tool bundle files are 16/15/15 versus 13/13/13. These are
descriptive sample measurements, not a causal or performance guarantee.

## Reproduction commands

All commands run from the repository root. Exact output paths differ by case;
every run manifest records its full command, prompt hash and output inventory.

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-build-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261025-plugin-build-v2-contract-sol-1 --timeout-seconds 360 --expect-output plugin/queue.ts --expect-output review/interaction-review.md --expect-output review/checks.json
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-build-generalization.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261025-plugin-build-v2-generalization-sol-1 --timeout-seconds 360 --expect-output blueprint/implementation.md --expect-output blueprint/contracts.json
```

The run IDs are immutable; repetitions use suffixes 2/3 and fresh workspaces.
V1 IDs omit `v2-`. Naturalistic outputs are `extension/releases.ts`,
`review/design.md`, `review/validation.json`; boundary outputs are
`fallback/recommendation.md`, `fallback/interaction.json`. Prompt sources are
`evaluations/pi-prompts/desktop-plugin-ui-build-<case>.md`.

For each completed trace:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error --require-tool-call --output evaluations/runs/<run-id>/read-surface.json
```

Inspect reads and shell actions as well as flags. All tested agents remain
inside their copied runtime and task workspace; no examples, sibling skill,
installed package source, network, account operation or deployment is allowed.
The evaluator separately uses installed tools to inspect completed artifacts.

## Deterministic and actual runtime evidence

| Check | Result and scope |
| --- | --- |
| Source checker | 67/67, including 14 new Pi subprocess cases and ownership checks |
| Design helper | 16/16 exact palette/token/contrast and immutable-copy checks |
| Typed ledger | 32/32 basis/outcome and output-integrity checks |
| Typed report integration | 41/41, fresh retained run ID |
| Legacy report checks | 33/33; legacy labels do not certify semantic truth |
| Harness regression | 17/17 |
| Artifact verifier selftests | 8/8 accepted-valid/rejected-defect fixtures |
| V1 generated executable artifacts | Contract 34/34 and each naturalistic 33/33 independent VM checks |
| Pi reference example | Actual offline RPC 9/9; modes 6/6, including 3 mocked branches and actual JSON-print checks |
| Generated naturalistic extension | Actual installed offline RPC 18/18; zero agent/turn events, exact filters/cancel, clean exit and empty stderr |
| Metadata-only routing | 10/10; no skill body or forced skill selection |

The independent artifact verifier is
[verify-build-interactions.ts](../../projects/desktop-plugin-ui/scripts/verify-build-interactions.ts);
its [selftests](../../projects/desktop-plugin-ui/scripts/test-build-interactions-verifier.ts)
reject wrong filtering/values, implicit cancel acceptance, headless notification
no-op and unexpected model turns. One naturalistic check initially required
an unnecessary keyword; the original false failure was preserved and corrected
against the prompt without rerunning the model or changing its artifacts.

Actual generated-code runtime command:

```powershell
node projects/desktop-plugin-ui/scripts/verify-generated-pi-rpc.ts evaluations/runs/20261025-plugin-build-naturalistic-sol-1/workspace/extension/releases.ts C:/Users/villa/AppData/Roaming/npm/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js
```

The [reusable RPC verifier](../../projects/desktop-plugin-ui/scripts/verify-generated-pi-rpc.ts)
uses isolated artifact-local Pi state and disables ambient resources/MCP/tools.
Generated extension SHA-256:
`a3c6ba1ab55b3ef9169b8ef77a16ef6de093e6991b36d63da4f0da63c9aab30d`.
Raw events/results remain under
`projects/desktop-plugin-ui/artifacts/generated-pi-rpc-20261025/`.

## Repository checks and limits

Required repository pattern, structure, independence and payload checks passed
on V1. The final pattern check passes with 1,348 IDs; independence and payload
checks pass. The final global structural check is blocked by a concurrently
edited unrelated file, `skills/pi-durable/references/agent-lifecycle.md`,
which lacks the required contents section for a reference over 100 lines.
The owning skill passes its scoped structural validator and all three
source/runtime/full audit profiles have exactly 26 files and the V2 hash.
No unrelated canonical source was repaired. Commands:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/validate-skills.py --skill skills/desktop-plugin-ui
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/audit-skill-authoring.py --skills evaluations/runs/20261025-plugin-build-v2-scoped-audit/source --check-bundles --output evaluations/runs/20261025-plugin-build-v2-scoped-audit/report.json
```

The scoped source tree is a preserved copy of the owning canonical bundle;
its audit digest matches the forward manifests and canonical source. A broad
unrelated whole-repository copy audit
was stopped and replaced by the scoped audit; it is not reported as a pass.
Initial preflight caught missing contents sections in two new references;
they were fixed before the frozen forward subject. A retained-test directory
collision and mistaken validator CLI path were corrected with a fresh test ID
and the documented path. These setup errors are not skill-use passes.

The required `uv run --script scripts/sync-local-skills.py` ran and V1's
26 files matched the local installation. Its global check encountered a
concurrently edited unrelated Pi Durable template. A V2 global synchronization
attempt stopped at the unrelated reference preflight. The same helper's scoped
`validate_bundles`, `pending_files` and `source_files` functions then copied
only the two V2 changes and verified **26/26 owning files with zero drift**.
The installed bundle also passes scoped validation. No unrelated canonical
fix was attempted or unrelated installation-wide parity claimed.

Actual Pi RPC is not TUI paint, focus, resize, screen-reader testing or project
installation. The revision does not establish signed-in UI acceptance across
all requested hosts or representative-user usability. Host/account gates and
earlier evaluation failures remain explicit; retain overall `validating`.
