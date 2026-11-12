# Cross-assistant v3 contract and boundary validation

Date: 2026-10-24 America/New_York / 2026-10-25 UTC. Model:
`openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0; existing recorded Luna
exception. Each case ran once with unchanged prompts and original grader.
No Claude or Copilot inference was used for these advisory evaluations.

The frozen runtime profile contains 15 files, payload SHA-256:

`1cd3cedbc5124bde59e242b22770eb0505893f65058cb7d438b90f55f79863b3`

V3 clarified diagnostic source checking during report repair and reserved the
failing CI flag for a clean final gate. Skill sources and grader were not
changed while these tests ran. Earlier v1/v2 failures remain separate.

| Case/run | Strict harness | Original independent grader | Direct artifact review |
| --- | --- | --- | --- |
| `20261024-desktop-ui-cross-v3-contract-luna-1` | Pass | Pass; 37 canonical patterns | Pass: substantive claims, exact sources, fields, and evidence labels |
| `20261024-desktop-ui-cross-v3-boundary-luna-1` | Pass | Pass; 13 canonical patterns | Substantive facts/citations pass; explicit evidence-field label placement gap remains |

Both runs completed with Pi exit zero, exact outputs, requested JSON false
booleans, unchanged copied payload, expected observed Luna model, zero invalid
JSON, and zero tool errors. Neither is a new host acceptance test.

## Contract review

The contract covers all five host IDs and distinguishes Desktop Chat versus
Code tab, Codex backend versus actual frontend, and Copilot terminal versus
VS Code MCP Apps/webviews/canvases. Its 37 canonical patterns have the required
input, rule, fallback, validation, and evidence. It preserves actual Claude
Desktop Chat paint/direct actions/fullscreen while keeping native-engine,
protocol, terminal, extension-owned webview, and incomplete ChatGPT setup at
their actual layers. Each historical JSON `evidence` field contains canonical
observed-* labels and scope.

Sources are exact members of the copied bundle/catalog. Both agent and
independent source checks pass for both final artifacts. No broad false UI
exclusion, unsupported permission inference, invented protocol method, or
material factual/citation defect was found. Cancellation, denied capability,
policy, and transport are kept separate from product support. The contract
does not claim that successful HTML bytes, SDK methods, or a webview prove
stock assistant paint.

## Boundary review and remaining format finding

The boundary preserves the unresolved Cloud names while completing a useful
conditional review. It rejects a universal native DOM container, direct
app-server `ui/initialize`, invented ACP `ui/show`, cancellation as permission,
native `file:` portability, and universal fullscreen/device support. Each
rejection is bounded to the correct surface and accompanied by an alternative
and next check. Historical Claude paint, native-engine checks, Codex protocol,
Copilot terminal controls, and incomplete ChatGPT setup remain distinct.
No substantive factual error or fabricated primary citation was found.

However, every historical observation places `observed-working` and/or
`observed-failed` in its JSON **`result`** string, while the requested
**`evidence`** string contains date, source, and narrative only. The current
skill explicitly requires the canonical label in a requested `evidence` field.
This is therefore a bounded artifact-format failure despite the substantively
correct result. Do not describe it as an unqualified manual-format pass.

The original independent helper checks for canonical labels anywhere in the
historical-observations array, which explains its pass: it does not enforce
per-field placement. No evaluator modification or output repair was made after
observing this gap. The raw agent output remains intact for audit.

## Trace/read-surface review

Both traces read 14 paths: `../prompt.md`, the copied skill entry point, and
the relevant copied references. No acceptance fixture, project evidence,
sibling skill, repository docs, previous run, or outside-workspace source was
read. Broad reference coverage is appropriate for the five-host task.

Contract shell activity: one clean exact-command source check of both final
outputs using `--fail-on-findings`. Boundary: list the bundled source catalog,
then a diagnostic source check covering both final outputs. Both the agent
and independent checks returned `passed: true`. There was no network,
application, account/configuration operation, or provider call within either
advisory task. Model execution was only the evaluator's ChatGPT-backed Luna.

## Exact artifacts and hashes

Paths are relative to each run's `workspace/`.

| Case | Artifact | SHA-256 |
| --- | --- | --- |
| Contract | `results/cross-reference.md` | `54d24f740ff31919a07458edbca44b67b6a83609a4582956994566c8b3e6f984` |
| Contract | `results/cross-decisions.json` | `9c7f825146399c644e24a60b7e9202ada5f9b4e73e5cfb8db7bebc386fcc1051` |
| Boundary | `review/cross-boundaries.md` | `08fed4e7f73b296dc69a45ddd06e60572b3668406da962199fd23576429bfadc` |
| Boundary | `review/cross-status.json` | `59a9392de2e1fcea3cf20ac2cacfa704ec9d2ad264b0c2a63b82b750d311672a` |

## Commands and retained evidence

Exact harness commands, prompt hashes, expected output/boolean arguments,
and payload digests are in each run manifest. These use the commands from
[v1](cross-v1-contract-boundary.md), changing only the run ID cohort to
`cross-v3-`; prompt files, strict mode, Luna model, and output contract are
unchanged.

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v3-contract-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v3-contract-luna-1/read-surface.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v3-boundary-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v3-boundary-luna-1/read-surface.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v3-contract- --output evaluations/runs/20261024-desktop-ui-cross-v3-contract-independent.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v3-boundary- --output evaluations/runs/20261024-desktop-ui-cross-v3-boundary-independent.json
```

JSONL, stderr, manifests, gate reports, read summaries, copied payloads, and
unmodified agent artifacts remain in the original ignored run directories.
No same-payload favorable reroll or manual artifact repair is accepted here.
