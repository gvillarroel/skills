# Typed evidence contract: GPT-6.1 Sol first attempt

Date: October 25, 2026, America/New_York. Skill: `desktop-plugin-ui`.
Run: `20261025-desktop-ui-evidence-contract-v2-sol-1`.
This is one new cross-model first attempt on the unchanged v2 subject.
The per-run `openai-codex/gpt-6.1-sol` exception was explicitly recorded in
`SKILLS.md` before launch. No global model or account setting was changed.

## Acceptance

| Gate | Result | Evidence |
| --- | --- | --- |
| Actual model/account path | **Accepted for this run** | Ten observed `gpt-6.1-sol` records from `openai-codex`, normal tool execution and Pi exit 0. |
| Strict harness | **1/1** | Exact artifacts, events/model/read surface, false task flags and unchanged payload all pass. |
| Typed report checker | **1/1** | Ten normalized records; no findings. |
| Independent manual semantics | **1/1** | All eight synthetic input notes are represented with accurate evidence bases and outcomes. |
| Execution scope | **1/1** | Explicit writes remain in task-relative `work/` and `audit/`; no outside-temp, account or host action. |
| Joint acceptance | **1/1** | Strict, typed, semantic and scope checks agree for this case. |

The run completes in **88.613 seconds**, with 11 tool calls: seven reads,
one write, two bash calls and one successful Markdown edit. There are zero
tool errors, zero invalid JSON records and zero event-policy findings. The
required independent summary explicitly requires `gpt-6.1-sol` and passes.
Acceptance is established by execution and observed model records, not merely
by the requested model name in the manifest. It establishes this model path
at this time, not general account entitlement or future quota availability.

## Frozen identities

| Item | Identity |
| --- | --- |
| Copied runtime | 23 files, SHA-256 `ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f` |
| [Unchanged contract prompt](../pi-prompts/desktop-plugin-ui-evidence-contract.md) | SHA-256 `fa2e1a287c431754549c93d86a97c36bb379e3934c86f1f784789b6ffb012838` |
| [Pre-frozen Sol review criteria](evidence-repair-sol-review-criteria.md) | SHA-256 `0a94fd291070d026215d42b19ef816fad4b6b0e2e8aab55de87e35ce63f4a3db` |
| `audit/evidence.md` | SHA-256 `d7ea7a98749f448d7f0a88720b473e3d174c7591454e8d9214591d6211d152f9` |
| `audit/evidence.json` | SHA-256 `993a4a702025c3047f01c488d9b683851619191be2719c35bd318ca1fb42ad20` |

Both requested files exist at their exact paths and are nonempty. JSON has
normalized `evidence_records`, supplied-fixture `sources` and literal Boolean
`host_acceptance_verified:false` and `task_empirical_tests_performed:false`.
The copied prompt has Windows CRLF SHA-256
`06ce60504b7b6f9cbb2fd4850900edc0a014bb0e3898c9e64e1b0a866605ad68`;
its normalized UTF-8 text equals the source. Preflight, actual manifest and
post-review snapshots all preserve the frozen copied subject.

The semantic standards and thresholds remain those of the repair cohort;
the separate criteria change the required evaluator model. No prior Luna
result is pooled with this Sol result or retrospectively reclassified.

## Independent content review

The ten helper-normalized records cover every input note:

- The inspected fullscreen handler is a source declaration, not observed
  execution. A separate unrecorded-execution record correctly explains that
  no receipt does not prove execution never occurred.
- Contract section 2 is documentation of an inline view, not painted UI.
- The tester's visibility remains a human report with automated acceptance
  untested. A separate record preserves the absence of automated capture.
- The desktop paint check is unperformed because no signed-in session exists;
  the account gate does not become an observed failure or product exclusion.
- The supplied `E_STALE` receipt matches the expected rejection and preserved
  revision 8, so its negative check passes.
- The save receipt does not reach expected revision 9 and returns
  `E_UNAVAILABLE` with revision 8 unchanged, so that supplied check fails.
- The proposed canvas remains conditional, with both prerequisites explicitly
  unchecked. No enabled renderer or supported session is invented.
- Camera access stays unsupported only under the supplied fixture build's
  explicit section 4 exclusion.

The report retains supplied host version 1.4.2 while explicitly preserving
unknown capture versions. It does not replace missing capture information
with a host inventory. The scope and provenance explain that neither the
source files, contract nor lab probes were newly inspected/executed by the
agent. Supplied receipt classifications remain separate from false task-level
acceptance flags. All prose is English and no new real-product claim, UI,
numeric contrast value or user study appears.

The eight fixture-source entries provide ten `evidence_ids`, covering all
normalized records; every reference resolves. Public URLs were not required:
the report correctly uses the supplied source locators rather than inventing
external documentation URLs. Zero URL checks therefore do not certify public
source retrieval.

## Workflow, read surface and write scope

The first completed read is `../prompt.md`, followed by the loaded entry
point. Focused additional reads are `references/report-authoring.md`,
`scripts/check_reports.py`, `scripts/evidence_ledger.py` and the two final
outputs. There is no acceptance-gallery, sibling-skill, project-document or
outside-workspace read, and no file above 50 KB is read.

The agent writes raw facts with final metadata to `work/facts.json`, invokes
the classifier once, and then adds an explanatory Markdown introduction.
The ledger table remains exactly the helper-derived table. Independent
reclassification confirms all normalized fields match; independent Markdown
comparison confirms exact table equality. The final typed checker runs after
the last edit and returns inspected `passed:true` with ten nonzero records.
No file is modified after that final check.

The complete shell audit contains only these task-local helper commands:

```bash
export UV_OFFLINE=1 UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1
uv run --script skills/desktop-plugin-ui/scripts/evidence_ledger.py --input work/facts.json --output audit/evidence.json --markdown audit/evidence.md
```

```bash
export UV_OFFLINE=1 UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py audit/evidence.md audit/evidence.json --require-evidence-records
```

These variables are per-process controls, not global configuration changes.
No generic temporary-file API, absolute output, system-Temp inspection or
cleanup, account/sign-in operation, extra provider, Copilot/Claude call,
browser or real-host UI test occurs. No explicit write leaves the authorized
task workspace or enters the read-only copied skill.

## Commands and retained evidence

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-contract.md --run-id 20261025-desktop-ui-evidence-contract-v2-sol-1 --model openai-codex/gpt-6.1-sol --mode json --strict --expect-output audit/evidence.md --expect-output audit/evidence.json --expect-output-json-field audit/evidence.json::host_acceptance_verified=false --expect-output-json-field audit/evidence.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-contract-v2-sol-1/events.jsonl --output evaluations/runs/20261025-desktop-ui-evidence-contract-v2-sol-1/independent-event-summary.json --require-model gpt-6.1-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
uv run --script evaluations/runs/20261025-desktop-ui-evidence-contract-v2-sol-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-evidence-contract-v2-sol-1/workspace/audit/evidence.md evaluations/runs/20261025-desktop-ui-evidence-contract-v2-sol-1/workspace/audit/evidence.json --require-evidence-records --fail-on-findings
```

The original run is retained under
`evaluations/runs/20261025-desktop-ui-evidence-contract-v2-sol-1/`: manifest,
events, stderr, exact outputs, all strict gate reports,
`independent-event-summary.json` and `independent-artifact-review.json`.
The independent artifact receipt includes all hashes, observed model/provider,
table equality, basis counts, recursive IDs and complete shell commands.

There was one first attempt, with no account rejection, retry, reviewer
artifact repair, canonical edit or backlog edit. Prior
[Luna v2 contract/boundary results](evidence-contract-boundary-v2-luna.md)
remain separate. This passing contract does not establish the full Sol cohort,
model superiority or actual assistant-host UI acceptance.
