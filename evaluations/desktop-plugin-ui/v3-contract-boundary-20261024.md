# Desktop plugin UI: v3 contract and boundary evidence

Checked 2026-10-24. These two cases evaluate the final frozen **v3** nine-file
runtime only, SHA-256
`93deff855cc7172a09e125235323e8fda95121b532d017e1cb14284764508149`.
V3 adds the deterministic bundled source checker and requires checking every
generated report format. Initial and v2 citation failures remain separately
recorded in their own reports; neither their failures nor their successes are
pooled into this subject. No rerolls or evaluator repairs were performed.

Both fresh isolated runs used **openai-codex/gpt-5.6-luna**, high thinking,
runtime payload, strict JSON mode and a 600-second timeout. The deliberate
model exception follows the separately retained Spark provider rejection and
is recorded in `SKILLS.md`. Environment: Pi 1.4.0, uv 0.10.12, Windows 11.

## Results

| Case and run ID | Strict harness | Independent artifacts | Joint result |
| --- | --- | --- | --- |
| Contract: `20261024-desktop-ui-v3-contract-luna-1` | Pass, 13 error-free calls, 78.687 seconds | Pass: 20 canonical JSON patterns, correct Chat/Code/packaging/host-owned distinctions, exact source URLs | Pass |
| Boundary: `20261024-desktop-ui-v3-boundary-luna-1` | Pass, 13 error-free calls, 46.039 seconds | Pass: six accurate assessments, ten canonical pattern IDs, honest provisional host and evidence limits | Pass |

Strict, independent and joint acceptance are **2/2**. V3 contract and boundary
gates are each **1/1**. Naturalistic/generalization cohorts and routing remain
separate evidence. This success does not establish signed-in host painting,
installation, permissions, OS delivery, or untested platform behavior.

## Contract semantic review

Exact outputs `results/reference.md` and `results/decisions.json` exist,
are nonempty, and agree on the intended ordinary Chat versus separate Code-tab
runtimes. JSON parses, contains required fields and **20** unique canonical
pattern IDs, records the snapshot date, and keeps
`host_acceptance_verified: false`. The reference gives concrete inputs, rules,
alternatives and validation actions for well over the required ten patterns.

Substantive advice correctly identifies MCP Apps registration, UI MIME,
sandboxed HTML and bridge as the Chat mechanism, MCPB/settings as distribution
and configuration, and native Mods as the Code mechanism. It preserves usable
text/data and scopes fullscreen, files, asynchronous state, CSP and optional
capabilities. Native previews retain their surface and scripting boundaries.

The requested host-owned surfaces are covered explicitly: elicitation is a
restricted host form or external URL flow, with negotiated modes and no secrets
in form data; ordinary Desktop Chat execution remains conditional/untested.
Native render sites can augment documented messages/tool/progress/question
sites without implying arbitrary host permission, toolbar, DOM or OS access.
Most such replacements remain documented/untested. The advice distinguishes
SDK, synthetic browser, native engine and actual installed-host acceptance.

The report includes a harmless empty row in the surface-comparison Markdown
table. It does not hide or alter information and is not an acceptance failure.
No material factual, compatibility or evidence-scoping defect was found.

## Boundary semantic review

Exact outputs `review/boundaries.md` and `review/status.json` exist and parse
as expected. JSON contains six assessments and **ten** canonical pattern IDs;
both product confirmation and host acceptance are false. The review finishes
with a clearly provisional Claude Desktop assumption rather than inventing a
Cloud Desktop API or requiring an unavailable reply.

The recommendations accurately handle each proposed assumption:

- Native Mod and Client trees cannot accept arbitrary React/iframe DOM; a
  separate MCP Apps HTML View is the conditional Chat alternative.
- The tested 2.1.302 `file:` Link downgrades to Text while the remaining tree
  survives; accepted/stubbed actions do not prove an OS effect.
- SDK method or PiP enum existence is insufficient; capability, returned mode,
  policy and actual delivery need independent checks and denial fallbacks.
- A browser fixture remains lower-layer evidence; installed host acceptance
  stays untested with concrete host discovery/paint/interaction/delivery checks.
- Hidden viewer initialization is a dimension-sensitive sizing pitfall, with
  reveal/resize and actual-pixel verification, not a universal HTML prohibition.

Each assessment provides a practical conditional fallback and the relevant
evidence needed. The Markdown and JSON are materially consistent. No external
application action or unsupported production claim was made.

## Source-checker use and independent URL review

The contract agent first ran the exact bundled source catalog, then checked
**both** `results/reference.md` and `results/decisions.json`. The actual tool
result was `passed: true`, **21** official URLs checked, and no
findings. Boundary checked **both** `review/boundaries.md` and
`review/status.json`; its actual result was `passed: true`, **9** official URLs
checked, and no findings. Neither used `--allow-url`, skipped JSON,
or treated exit status alone as proof. No repair pass was needed in either run.

The evaluator independently extracted complete URLs from both output formats
and compared them case-sensitively against the copied frozen Markdown bundle,
retaining path/query/fragment and removing only terminal sentence/list
punctuation. This broader check includes example/local URLs rather than only
recognized official source families:

| Output | Unique HTTP(S) strings | Exact-source mismatches |
| --- | ---: | ---: |
| Contract Markdown | 22 | 0 |
| Contract JSON | 0 | 0 |
| Boundary Markdown | 10 | 0 |
| Boundary JSON | 1 | 0 |

The boundary JSON URL is the literal localhost example; official citations are
in Markdown. Both formats were checked even where no source link occurred.
Per-run evaluator `source-url-check.json` files retain the full comparison
results outside the copied bundle.

## Trace and payload review

Both observed-model summaries pass valid JSON and zero tool-error checks.
Each agent first reads `../prompt.md`, then `SKILL.md` and all six compact
references. These are broad cross-surface cases; the source checker reads only
its own entry point/reference catalog and specified generated reports. Neither
trace depends on repository docs, sibling skills, acceptance galleries,
project artifacts, network browsing or external applications. The boundary's
extra working-directory/shallow file inventory remains inside its isolated
workspace after reading the prompt and skill. It provides no hidden context.

Both nine-file payload integrity reports have identical before/after digests
and no added, removed or modified copied resources. Semantic and URL grading
were evaluator-owned; no results were fed back into an evaluated run.

## Commands

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261024-desktop-ui-v3-contract-luna-1 --expect-output results/reference.md --expect-output results/decisions.json --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261024-desktop-ui-v3-boundary-luna-1 --expect-output review/boundaries.md --expect-output review/status.json --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-v3-contract-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-v3-contract-luna-1/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-v3-boundary-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-v3-boundary-luna-1/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Observed agent-side commands from the isolated workspace:

```sh
uv run --script skills/desktop-plugin-ui/scripts/check_sources.py --list-sources
uv run --script skills/desktop-plugin-ui/scripts/check_sources.py results/reference.md results/decisions.json
uv run --script skills/desktop-plugin-ui/scripts/check_sources.py review/boundaries.md review/status.json
```

The last command belongs to the separate boundary workspace. Full argument
vectors, outputs and tool events remain in their respective run evidence.

## Retained artifacts

All raw events, manifests, output pairs, checker responses and independent
URL/trace/integrity reports remain under the two named ignored
`evaluations/runs/` directories.

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| Contract `results/reference.md` | 25,984 | `7676822c9394e1ca75c2c6f30a5d5d4e23c8657818a637e0c89803a668226297` |
| Contract `results/decisions.json` | 13,599 | `15d063bb555fb38963f4e8221793f11a6ec4b329ea36987ea3d2bc6a3a6ea1a2` |
| Boundary `review/boundaries.md` | 9,246 | `3d4c28b7fa587fbf3cb11028cd4097e1ac9d5a4d531c649b070d3e9a15359112` |
| Boundary `review/status.json` | 4,012 | `93e3df9ca94077054aa10b2978d57a9df1001b5571dde5f273bd5a444b6535b2` |
