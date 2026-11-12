# Typed evidence repair v2: contract and boundary review

Date: October 25, 2026, America/New_York. Skill: `desktop-plugin-ui`.
Subject: revised 23-file evidence workflow with task-scoped scratch guidance
and helper-owned final report metadata. These are two fresh first attempts
on a separately frozen subject. Earlier subjects and failed runs remain
intact; no result is pooled with them.

## Outcomes

| Case | Strict | Typed checker | Manual semantics | Execution scope | Joint |
| --- | --- | --- | --- | --- | --- |
| Synthetic contract | **1/1** | **1/1** | **1/1** | **1/1** | **1/1** |
| Status boundary | **1/1** | **1/1** | **0/1** | **1/1** | **0/1** |

The contract completes in **43.591 seconds** with 13 error-free tool calls
and ten Luna model records. The boundary completes in **108.289 seconds**
with 27 error-free tool calls and 18 Luna model records. Both have Pi exit 0,
all four strict gates true, zero invalid JSON and zero event-policy findings.
The independently required event summaries pass.

The typed checker passes on **10 contract records** and **14 boundary
records**. Independently normalized records and helper-rendered Markdown
tables match the final artifacts exactly. Contract has seven findings with
ten supporting ID references. Boundary has six findings with 14 references;
all 27 nested ID references resolve. These structural passes do not establish
that each reference supports the associated claim; the boundary's two
semantic failures are detailed below.

The contract has zero public URL checks because its sources are supplied
fixture locators. Boundary has four exact official URL occurrences across
its two files. All generated prose is English. No new renderer, numeric
contrast claim or user study is requested or performed.

## Frozen subject and output identities

Both copied runtimes contain **23 files**, SHA-256
`ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
Preflight, actual manifests and post-review copied snapshots all match.

| Input | SHA-256 |
| --- | --- |
| [Unchanged contract prompt](../pi-prompts/desktop-plugin-ui-evidence-contract.md) | `fa2e1a287c431754549c93d86a97c36bb379e3934c86f1f784789b6ffb012838` |
| [Unchanged boundary prompt](../pi-prompts/desktop-plugin-ui-evidence-boundary.md) | `441c75ee394a7e4f2a2e8ef95235c54deb62099f1577d5444768855508c6716e` |
| [Unchanged frozen review criteria](evidence-repair-review-criteria.md) | `c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2` |

The deliberate model exception remains `openai-codex/gpt-5.6-luna`, thinking
high, JSON strict, 600-second limit. Both task-level JSON acceptance flags
are literal Boolean `false`. Both exact required output files are present
and nonempty in each run.

| Run ID | Required output | Final SHA-256 |
| --- | --- | --- |
| `20261025-desktop-ui-evidence-contract-v2-luna-1` | `audit/evidence.md` | `9716e01388a91c459e6bcf8b52050ab60b89ede06b59aab2663fbd6a0eaa6814` |
| Same contract run | `audit/evidence.json` | `4a2ab143f53558da059cbb3a29ae53f89afee3ec4e87ab1705274b706e9d2798` |
| `20261025-desktop-ui-evidence-boundary-v2-luna-1` | `review/status.md` | `3f8f08201b71ea3a7ba13b237637d82befb357a856e2089573de53c2dfea1491` |
| Same boundary run | `review/status.json` | `f4dfeb9831fdf1d424fae249362d74b741a1ec498b58462fe4648d408014dd28` |

Manifest hashes refer to raw source prompts. The harness copies CRLF prompts:
contract copy SHA `06ce60504b7b6f9cbb2fd4850900edc0a014bb0e3898c9e64e1b0a866605ad68`,
boundary copy SHA `13a4f341742a34297d0b7cd5cca954ddd5179c726259b845d5f6b36dfa4eb27c`.
Both copies' normalized UTF-8 text exactly equals the corresponding source.
No prompt mutation is inferred from newline serialization.

## Contract: independent acceptance

All eight supplied lab notes are represented by ten correctly normalized
records. Source and contract declarations derive `documented/not-run`;
the tester's visibility report remains `untested/not-run` with unknown
capture version. Skipped paint is untested. The expected stale rejection
with unchanged revision 8 is a passing negative check; the unmet save
expectation with `E_UNAVAILABLE` is an observed failure. Canvas prerequisites
are conditional and separately unchecked. The camera exclusion is confined
to the fixture contract/build.

Seven voluntarily added factual findings link to the appropriate records.
The JSON explicitly identifies synthetic lab notes and keeps current-task
acceptance false, so the supplied receipt classifications are not presented
as new installed-product tests. The known Lab UI Host 1.4.2 context remains
attached to source/contracts/receipts, and the unrecorded human capture
version is not invented.

Actual workflow use is verified: the agent writes `work/facts.json` with its
optional `report` metadata, invokes `evidence_ledger.py` once to derive the
two final files, invokes the typed checker on both, observes `passed:true`
and reads both completed artifacts. No post-generation merge or handwritten
ledger classification is used. Independent classification and exact table
comparison pass. No contract semantic or write-scope failure was found.

## Boundary: useful corrections and retained failures

The memo correctly repairs the five central draft statements:

- Missing signed-in readiness/paint stays untested rather than a fabricated
  failure; the user's current continuation without sign-in is preserved.
- Activation is a logged attempt followed by orderly termination with no
  failure stack, not established authenticated readiness.
- Expand source is documented and not executed; no fullscreen acceptance is
  invented.
- User-reported visibility, actual failed controller binding and unperformed
  control checks remain distinct outcomes. The failed bind does not become a
  product rendering exclusion.
- The hypothetical stale-edit sentence has no receipt in this memo; it does
  not acquire an executed guard result.

Ordinary webview behavior remains separate from signed-in Copilot Chat. The
24-check English/CS1 result is scoped to real MCP plus a synthetic-browser
fixture. Future checks are explicitly unperformed and conditional on authorized
access. The prose does not claim a user study or host ColorSet pixels.

Two factual-scope problems nonetheless fail the frozen manual criteria:

1. **Native observations and user choice are combined as a user report.**
   `copilot-workspace-choice` combines the later workspace's cleared Restricted
   Mode/remaining Sign In observations with the user's no-sign-in choice. It
   assigns the combined record `basis:user-report`, `layer:user-report` and
   reporter `October 25 follow-up user/workspace review`. These are materially
   different origins: workspace state was a native observation, while the
   account choice was a user statement. The source bundle does not establish
   that the user reported the native observations. The typed helper accepts
   the declared basis but cannot make that attribution accurate. This fails
   the prompt's layer separation and the criteria's requirement to preserve
   basis/observer and split materially different bases.
2. **A source claim references an unrelated execution record.** The second
   JSON `sources` entry describes the GitHub Copilot extension tutorial's
   `CLI extension route` and links it through `evidence_ids` only to
   `copilot-native-webview-pass`. The Markdown also states that extension-route
   distinction. The referenced record describes ordinary VS Code webview
   execution, not the documented CLI route. No normalized record supports
   this added documentation claim. Its URL is valid and the ID resolves,
   but neither fact establishes the required scoped evidence relationship.

These are not hidden row-count or ID-format requirements. The failure is the
actual declared origin and support relationship of used claims. All five
central corrections and the correct exact-source URLs remain positive scoped
findings. Some broader host labels use `Codex/Copilot follow-up`; their
precision could improve, but no additional hard failure is assigned merely
for that wording or for the free-choice `copilot-*` record IDs.

## Scope, trace and helper audit

Both traces begin with `../prompt.md`, then the loaded entry point. Contract
reads focused evidence/report references and the two helper scripts.
Boundary reads the relevant host/evidence/report and language-color references
plus its helper scripts, task-owned raw ledger and exact outputs. No acceptance
gallery, sibling skill, external project material or source file above 50 KB
is read. The source references and scripts are relevant to these diagnostics.

Every shell command and explicit write path was reviewed. Contract uses two
helper `--help` calls, then task-relative `work/facts.json` → `audit/` generation
and typed checking. Boundary uses helper help, task-relative classifier output
under `work/`, local copy to `review/status.json` and typed checking. Its
successful in-attempt raw-input and Markdown edits are retained in the trace;
the evaluator makes no changes to them. Both final tables exactly match the
classifier output after the last generation. Both final typed passes are
inspected, followed by reads of the completed files.

**Scope passes for both:** no system-Temp path, generic temporary-file API,
absolute output, outside-workspace read/write, cleanup, provider, account,
sign-in, app/global operation or real-host UI action appears in either trace.
The evaluator did not inspect or clean any outside temporary directory.
No Claude/Copilot inference was performed.

Raw evidence is retained under each `evaluations/runs/<run-id>/`, including
manifests, original events/stderr, exact outputs, strict gate receipts,
`independent-event-summary.json` and `independent-artifact-review.json`.
The independent artifact receipts include output/prompt/criteria hashes,
nonzero record counts, recursive ID checks, table equality and copied hashes.

No rerun, reviewer artifact repair, canonical edit or backlog edit occurred.
The [v1 contract/boundary results](evidence-contract-boundary-v1-luna.md) and
other case families remain separate. These two cases do not establish the
remaining cohort thresholds or actual assistant-host rendering/controls.

## Commands

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-contract.md --run-id 20261025-desktop-ui-evidence-contract-v2-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output audit/evidence.md --expect-output audit/evidence.json --expect-output-json-field audit/evidence.json::host_acceptance_verified=false --expect-output-json-field audit/evidence.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-boundary.md --run-id 20261025-desktop-ui-evidence-boundary-v2-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output review/status.md --expect-output review/status.json --expect-output-json-field review/status.json::host_acceptance_verified=false --expect-output-json-field review/status.json::task_empirical_tests_performed=false --timeout-seconds 600
```

The required summary was run separately for each exact ID:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/independent-event-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
```

Independent typed checks used the unchanged copied helper:

```powershell
uv run --script evaluations/runs/20261025-desktop-ui-evidence-contract-v2-luna-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-evidence-contract-v2-luna-1/workspace/audit/evidence.md evaluations/runs/20261025-desktop-ui-evidence-contract-v2-luna-1/workspace/audit/evidence.json --require-evidence-records --fail-on-findings
uv run --script evaluations/runs/20261025-desktop-ui-evidence-boundary-v2-luna-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-evidence-boundary-v2-luna-1/workspace/review/status.md evaluations/runs/20261025-desktop-ui-evidence-boundary-v2-luna-1/workspace/review/status.json --require-evidence-records --fail-on-findings
```

Completed IDs remain immutable; these commands document the retained attempts
and do not authorize overwriting them.
