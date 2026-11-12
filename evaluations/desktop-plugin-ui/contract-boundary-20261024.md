# Desktop plugin UI: initial contract and boundary evidence

Checked 2026-10-24. These results belong to the initial frozen seven-file
`desktop-plugin-ui` runtime, SHA-256
`8ae7ae5066ab3eee6913ecbb57f137204f15aba527d7eafc4f0e2b82e65c4808`.
They must remain separate from a later revised payload or cohort. No rerolls
were performed and neither generated output pair was repaired by the evaluator.

The evaluated model was **openai-codex/gpt-5.6-luna**, with high thinking,
strict JSON mode and a 600-second timeout. `SKILLS.md` records the deliberate
exception after the separately retained Spark provider rejection. Pi 1.4.0,
uv 0.10.12 and Windows 11 were observed. Both runs used fresh helper-created
workspaces and the runtime profile; only the target copied skill was loaded.

## Results

| Case and run ID | Strict harness | Independent artifacts | Joint outcome |
| --- | --- | --- | --- |
| Contract: `20261024-desktop-ui-contract-luna-1` | Pass, 10 error-free tool calls, 48.549 seconds | Fail: one App API source URL mutated to an incorrect domain; substantive advice otherwise passes | Fail; classification `agent` |
| Boundary: `20261024-desktop-ui-boundary-luna-1` | Pass, 12 error-free tool calls, 42.561 seconds | Pass: all proposed assumptions assessed with appropriate conditional alternatives and evidence limits | Pass |

The strict result is **2/2**. Independent and joint acceptance is **1/2**.
The initial contract gate is therefore **0/1**, and boundary is **1/1**.
These two cases alone do not establish naturalistic/generalization thresholds,
automatic skill routing, signed-in host acceptance, or a complete release.

## Contract semantic review

The run created exactly `results/reference.md` and `results/decisions.json`.
JSON fields parse, `host_acceptance_verified` is false, and all **16** unique
pattern IDs are canonical entries in the copied bundle. The recommendations
correctly distinguish ordinary Chat's MCP Apps HTML View from native Code Mods,
and separate MCPB/settings/configuration from runtime UI. The ten Chat patterns
have concrete input needs, rules, alternatives and validation actions; bridge
patterns extend the reference rather than replacing those recipes.

The artifact correctly scopes SDK, synthetic browser and native-engine
observations. It retains conditional fullscreen, download and permission
claims, identifies actual signed-in paint and delivery as untested, and records
the 2026-10-24 snapshot. It treats inline action counts as design guidance and
does not claim browser success proves Desktop support. The prose and JSON are
consistent on the intended surface and principal limits.

The source list contains a specific source-fidelity error:

- Output URL: `https://apps.extensions.modelcontextprotocol.com/api/classes/app.App.html`
- Exact bundled URL: `https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html`

The evaluator compared the generated reference with the copied bundle and
performed a separate read-only web check. The `.com` URL was inaccessible to
the web tool; the exact `.io` URL loaded the official App API page. This is an
incorrect authoritative citation, not evidence the upstream API is unavailable.
The run is retained as an **artifact failure**, classified `agent`, because the
correct URL was present in the read resources. All other substantial advice can
still be useful; it does not erase this failed acceptance gate. A future skill
revision can explicitly require exact source-URL preservation and validate a
new frozen cohort without merging its passes into this one.

## Boundary semantic review

The run created exactly `review/boundaries.md` and `review/status.json`.
The JSON contains six assessments and **12** canonical pattern IDs, with no
unknown IDs. Both `product_confirmed` and `host_acceptance_verified` are false.
The prose proceeds with a clearly provisional Claude Desktop assumption and
conditional Chat/Code/browser alternatives, completing the review without
inventing a product or demanding an unavailable answer.

The review correctly explains:

- React/HTML belongs in an MCP Apps View; a native Mod or Client is a native
  tree and cannot accept arbitrary iframe/DOM content.
- Tested 2.1.302 native `file:` Links downgrade to non-clickable Text while
  preserving the rest of the tree. It does not overstate this as a universal
  fatal render failure. It offers an explicit user-pressed opener with argv or
  a copyable path, keeping real OS effects unverified.
- PiP enum membership and `downloadFile` method existence do not establish host
  support. The pinned SDK's dispatch despite absent advertised download support
  is identified as a failed assumption, with fixture denial distinguished from
  the real host.
- A browser fixture is a distinct evidence layer; actual installed host paint,
  consent, policies and delivery require named target-host checks.
- Hidden-container chart initialization is a dimension-sensitive viewer pitfall,
  with mount-on-show/resize alternatives and actual paint checks. It does not
  falsely label `display:none` forbidden throughout HTML.

Each assumption has a workable fallback and an evidence collection plan.
No unsupported production or OS-delivery claim was found. The review uses
read-only bundled paths as its closed-book provenance and introduces no
invented external citation.

## Trace and integrity review

Both trace summaries pass observed-model, JSON validity and zero tool-error
checks. First completed reads were `../prompt.md`, then the bundle entry point.
Both runs read `SKILL.md` and all five compact references. This broad read
surface is justified by these specific cross-surface contract/boundary prompts:
the contract requested at least ten rules plus Chat/Code/packaging distinctions,
and the boundary combined native, Chat, browser, capability and lifecycle issues.
The boundary additionally reread its two generated artifacts. There were no
repository, sibling skill, acceptance gallery, project artifact or external
reads. The copied seven-file payload remained byte-identical in each run.
The agents did not browse or change an external application.

The evaluator's later source-URL check was separate from the isolated agent
trace and did not feed information back into the runs.

## Commands

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261024-desktop-ui-contract-luna-1 --expect-output results/reference.md --expect-output results/decisions.json --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261024-desktop-ui-boundary-luna-1 --expect-output review/boundaries.md --expect-output review/status.json --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-contract-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-contract-luna-1/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-boundary-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-boundary-luna-1/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Independent checks parsed JSON, compared all output IDs with canonical
`## claude-ui-*` headings in the copied references, reviewed both Markdown/JSON
pairs directly, compared source URLs, and inspected the complete trace summary
and copied-payload integrity report.

## Retained artifact identities

Raw runs, full command manifests, events, stdout/stderr and evaluator reports
are retained under the two named ignored `evaluations/runs/` directories.

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| Contract `results/reference.md` | 15,211 | `8dc2c3cc729f9aabceaf9ae7e4d157891ea393182f56bba5993904ba24ffdc90` |
| Contract `results/decisions.json` | 9,112 | `ee8c00be31a3bfb925ea04c3da57557d8ca0ae6bc4d1c2b03fbb4556708cf982` |
| Boundary `review/boundaries.md` | 7,082 | `4d4cc27d2705936dfa6392c0cd9276b42c2f21f685309219409a7f8c8b4b6a81` |
| Boundary `review/status.json` | 4,974 | `fe87dd646d795c6f4c016cccdbc552cdcfb69241d76f198d82ca5d5406dbe291` |
