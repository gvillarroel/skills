# Cross-assistant naturalistic evaluation, frozen v3

Date: 2026-10-24 (America/New_York; UTC logs dated 2026-10-25). Skill:
`desktop-plugin-ui`. Recorded model exception:
`openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0. The task prompt and
independent grader are unchanged from [v1](cross-v1-naturalistic.md) and
[v2](cross-v2-naturalistic.md). Those results remain separate. No outputs,
skill payloads, grader rules, or failing samples were edited or replaced.

Frozen runtime payload SHA-256:
`1cd3cedbc5124bde59e242b22770eb0505893f65058cb7d438b90f55f79863b3`.
All three manifests record that same 15-file payload. Prompt SHA-256:
`4b2f770266448125b47ac76a40bd42f730f170ebff7205ddf4d4752df1df41b4`.

## Outcome

**3/3 strict harness and independent structural/source checks passed.**
Conservative manual acceptance is **2/3**, satisfying the naturalistic
two-of-three threshold. Run 2 uses overly exclusive wording about Codex
dashboard availability, despite retaining the correct uncertainty elsewhere.
Treat it as an **agent / semantic wording failure**, not evidence that the
product lacks UI. Run 1 passes with a narrower wording caution recorded below;
run 3 is clean. Do not report these as three unconditional manual passes.

| Suffix after `20261024-desktop-ui-cross-v3-` | Strict | Independent | Manual | Canonical IDs | Duration |
| --- | --- | --- | --- | --- | --- |
| `naturalistic-luna-1` | Pass | Pass | Pass with wording caution | 20 | 63.940 s |
| `naturalistic-luna-2` | Pass | Pass | Fail: Codex availability wording | 23 | 74.261 s |
| `naturalistic-luna-3` | Pass | Pass | Pass | 28 | 74.781 s |

Every run created the exact nonempty `proposal/support-queue.md` and
`proposal/host-decisions.json`, with all five host IDs, canonical patterns,
historical evidence labels, and both task-level acceptance/test booleans false.
Each agent ran the source checker after final writes and inspected `passed`.
The independent inspector reran the copied checker with `--fail-on-findings`
on both outputs. All source checks passed; all payloads remained unchanged.

## Direct manual findings

All six artifacts were read in full after completion.

1. **Run 2, Codex availability wording: conservative manual failure.**
   The lead prose says, “A dashboard is only available in a Codex frontend that
   we own, not established in the stock CLI/app-server/desktop/IDE surfaces.”
   JSON `hosts[2].ui_method` similarly says “dashboard only in an owned
   frontend.” The defensible recommendation is to use an owned client when
   stock frontend capability is unverified. “Only available” states a stronger
   exclusion than the evidence establishes. Later limits, historical rows,
   and detailed validation correctly retain stock paint as untested; those
   caveats are preserved but do not silently repair the exclusive lead/field.
   A consumer should use the later scoped evidence and avoid repeating the
   exclusive wording. No artifact was edited.
2. **Run 1, ambiguous Codex evidence phrase: pass with caution.**
   JSON `hosts[2].evidence` says “historical observed-failed stock MCP Apps
   bridge/UI presentation.” Taken alone, that could imply a stock presentation
   attempt failed. The adjacent limits explicitly identify `ui/initialize` as
   the wrong app-server bridge, and both the Markdown and historical record
   state that stock frontend paint was not tested. In this full context the
   failure remains bounded to the protocol/policy probes; nevertheless the
   phrase should not be reused without that scope. It is not proof of a
   renderer exclusion or a failed stock desktop paint test.
3. **Run 3: no blocking factual/evidence issue found.**
   The Codex section recommends tool fallback, reports the failed app-server
   request and `never` policy, and separately calls stock desktop/IDE paint
   untested. It does not claim a custom client is the only possible renderer.

Across all three, the queue design covers search, stable selection, priority
draft/commit, chart, CSV, and explicit explanation. The proposals keep business
state/version checks on the server, preserve prior data after refresh failure,
and retain useful text/structured fallback. Run 2 gives a particularly clear
post-submit cancellation contract: cooperative cancellation or an explicit
“too late” outcome, with version protection rather than falsely claiming that
an in-flight server mutation was undone.

All three distinguish Claude Desktop Chat MCP Apps from Claude Code native
Mods; native engine success from terminal pixels; Codex backend data/callbacks
from renderer acceptance; ChatGPT setup/fixtures from widget paint; and Copilot
CLI forms, VS Code MCP Apps, and separately installed extension webviews.
The proposals retain local-stdio versus HTTPS/tunnel deployment differences,
optional mode/file/permission gates, explicit drafted-versus-submitted
follow-up behavior, and a zero-inference-first validation sequence. Historical
positive and negative observations are not erased or promoted to current-task
acceptance. Exact bundled primary URLs are present for every product.

## Commands and trace review

Three fresh processes ran this command with suffixes 1, 2, and 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-naturalistic.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v3-naturalistic-luna-1 --expect-output proposal/support-queue.md --expect-output proposal/host-decisions.json --expect-output-json-field 'proposal/host-decisions.json::host_acceptance_verified=false' --expect-output-json-field 'proposal/host-decisions.json::task_empirical_tests_performed=false'
```

Each trace was separately summarized with the required model, varying suffix:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v3-naturalistic-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-cross-v3-naturalistic-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v3-naturalistic-luna- --output evaluations/runs/20261024-desktop-ui-cross-v3-naturalistic-inspection.json
```

All three required-model summaries pass and observe only
`openai-codex/gpt-5.6-luna`. There are valid events, zero tool errors,
prompt-first reads, exact outputs, and unchanged payload hashes. Each run has
14 read-tool calls: prompt, entry point, and the compact cross-host references
needed for this five-product task. No acceptance examples, sibling bundles,
repository docs, project artifacts, or external reads were used. Shell commands
only listed/check sources or asserted local JSON structure. No task-level
network command, install, configuration write, app/account operation, or
provider call was found.

| Repetition | Input | Output | Cache-read | Trace token total |
| --- | --- | --- | --- | --- |
| 1 | 38,479 | 8,017 | 119,168 | 165,664 |
| 2 | 35,389 | 9,639 | 154,112 | 199,140 |
| 3 | 36,809 | 10,281 | 97,152 | 144,242 |

These are OpenAI Pi evaluation aggregates, not Claude/Copilot allowance usage.

## Evidence retention and routing

Raw workspaces, exact artifacts, manifests, checks, hashes, and model trace
summaries remain under
`evaluations/runs/20261024-desktop-ui-cross-v3-naturalistic-luna-{1,2,3}/`.
The unchanged inspector output is
`evaluations/runs/20261024-desktop-ui-cross-v3-naturalistic-inspection.json`.
It grades structural/source evidence only; the manual failure above remains
separate and must not be hidden by its three-pass result.

The description did not change between v1/v2/v3. The separate metadata-only
routing control remains 10/10, with no forced skill, no body supplied/read,
one prompt read, one output write, valid JSON, and the required Luna model.
See [the v2 record](cross-v2-naturalistic.md#metadata-only-routing-control) and
`evaluations/runs/20261024-desktop-ui-cross-routing-luna-1/result.json`.
