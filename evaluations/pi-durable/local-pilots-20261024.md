# Local agents and Codex provider validation, 2026-10-24

## Frozen skill subject

The final canonical Pi Durable bundle has 39 runtime files, SHA-256
`d3cde177a0bbbfb4a4ddc7ed8157ba242debf473cfaa84bb4498031dff87b633`,
and 48 full files, SHA-256
`5c4aa8f004c253b52e62cf72d56cbbdc52d039cc4aacc4660da3f790336e323a`.
The runtime payload copied by the final forward harness matches these bytes.
The bridge targets installed Pi CLI 0.84.2 and pinned Pi AI/Durable 1.3.0.

The skill now supports `openai-codex` through the installed Pi CLI's read-only
auth operation. It includes expiry checks, bounded capture, credential-safe
errors, low thinking, real request-attempt counters, and matching explicitly
requested reflection support. Compact references explain account renewal,
local repository/CI watcher adapters and durable progress notifications.
The Codex adapter does not serialize generic `maxTokens`; no server-side
token/spending cap is claimed.

## Deterministic and forward evidence

A fresh generated standalone service passed prepare/build, all 76 acceptance
tests and offline smoke. Evidence is retained under
`evaluations/runs/pdc-20261024-canonical/`; all 35 initial generated-file hashes
match its refreshed manifest. Tests use faux/injected behavior where stated.

The final isolated command was:

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-codex-bridge-contract.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id pi-durable-codex-bridge-20261024-final-2 --expect-output generated/service/package.json --expect-output generated/service/config.json --expect-output generated/service/src/codex-provider.ts --expect-output generated/service/.cache/smoke-result.json --expect-output checks/operations.json
```

It passed in 91.129 seconds: model observed correctly, all five exact artifacts,
valid events, zero tool errors, clean read surface and unchanged skill payload.
Independent inspection confirmed two named agents, Codex provider/model/path,
GitHub off, passing faux smoke and operational limits. The test did not use
account credentials or call a real model from the generated service.

The earlier `pi-durable-codex-bridge-20261024-contract` run also passed strict
gates for its distinct 38-file runtime hash
`9aa39f493e6fc220781ad388db749b51492b20e0637e40a2d4d68e614addc9a1`.
It predates the local watcher recipe. The intermediate `...-final` attempt
failed source preflight because the new long reference lacked contents links;
no forward model ran. Adding the contents section fixed that authoring defect.
Keep the attempts and hashes separate; do not pool their results.

The deliberate Sol forward-model exception remains the existing backlog
exception after Spark rejection before tools. This is one scoped contract,
not a replacement for the earlier failed naturalistic authoring cohort in
[the evolution record](evolution-20261024.md). Keep the skill `validating`.

## Actual local service evidence

The independent application in [the local pilot project](../../projects/pi-agent-services/README.md)
has actual host adapters for source and delivery observations. Two real
`openai-codex/gpt-5.6-sol` agents completed initial jobs, recorded public
evidence/decisions, reconnected to a real follow-up chat, deduplicated its
repeated request, and survived a host restart with unchanged task identities
and zero model calls for mere status/reconnect. A subsequent delivery change
triggered another real job. The project passed 98 tests, with focused reruns
after final provider/configuration changes.

Desktop outbox attempts were accepted on native Windows. Telegram remains
disabled pending the owner's channel and private recipient/secret setup.
WhatsApp was researched, not connected. No mobile delivery, native macOS
launch, public webhook, broad PR-review quality or unattended account renewal
is established. No automatic login task was installed. The processes run in
the current Windows session; durable state survives a later manual restart.

The [project validation record](../../projects/pi-agent-services/validation.md)
separates live evidence, deterministic tests, resource bounds and remaining
limits. Raw state, credentials, transcripts, logs and bulky runs stay ignored.

## Repository checks

Pattern IDs, skill structure, skill independence and payload checks pass.
An initial repository-wide check/sync observed a concurrent untracked Reflex XY
reference before its entry-point route was added; the later whole-repository
validator passed. That unrelated work was preserved. Local synchronization
completed; the Pi Durable installation matches all final canonical files.
An all-skill check observed two concurrently edited non-Pi example files;
this does not change the exact Pi bundle comparison. Publication receipts are
retained under the pilot's ignored artifact directory and can be checked against
the repository's GitHub Actions history for the published commit.
