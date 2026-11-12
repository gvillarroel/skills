# Nielsen and ColorSet rules for assistant plugin UI

Date: October 25, 2026, America/New_York.

## Subject and scope

This is a scoped design-contract update to `desktop-plugin-ui`, requested
after the cross-assistant investigation. Apply all ten Nielsen heuristics to
UI recommendations, designs and audits. Use ColorSet 1 for each new deliverable
unless ColorSet 2 is explicitly selected for that deliverable. The existing
42 interaction patterns remain unchanged.

The final source, runtime and full bundles each contain **19 files**, with
SHA-256 `d02ed682c82aaa66db71ca29019b3d866145c2a314bb0db3714dcde4d7c8f038`.
They include 13 progressive references, two exact palette assets and the two
existing report/source helpers. The new runtime path is
[`usability-and-color.md`](../../skills/desktop-plugin-ui/references/usability-and-color.md).

The palette snapshots are byte-identical to their canonical design sources:

| Asset | Unique hex tokens | SHA-256 |
| --- | ---: | --- |
| `assets/palettes/colorset1.yml` | 17 | `6472cb2a2e08738010051ce0f7c51107b115d215a70b8bb7f5db432411bf7cc1` |
| `assets/palettes/colorset2.yaml` | 37 | `b424b5aa2223a9587fa5d32e4258491f85207e73038c5f5be1d3f4ef99108a13` |

Runtime use reads the bundled copies. It requires no repository design files,
sibling skills or external palette service.

## Rules promoted

H1-H10 map in order to the official Nielsen principles, with concrete plugin
interaction checks, findings, remedies, evidence and justified nonapplicability.
A heuristic inspection is distinct from representative-user testing and host
acceptance. The reference cites the official NN/G principles and evaluation
method rather than presenting the project palette as a Nielsen requirement.

An exact role map covers actions, hover, text, surfaces, links, selection,
feedback and focus. Preserve redundant text, symbols or shapes, stable chart
categories, cancellation and recovery. Host-owned forms, consent controls,
chrome, native/terminal themes and accessibility overrides have explicit
styling boundaries. Never promise CSS, terminal truecolor, fonts, icons or
exact palette pixels without a supported renderer and actual verification.

Palette membership does not establish accessible contrast. Opaque sRGB
calculation identifies three unsafe default combinations:

| Proposed use | Pair | Contrast | Required threshold |
| --- | --- | ---: | ---: |
| Sole authored focus indicator | `#cfcfcf` on `#ffffff` | 1.5579550563651179 | 3:1 |
| Sole identifying input border | `#9c9c9c` on `#ffffff` | 2.7454458936977137 | 3:1 |
| Ordinary error text | `#e8002a` on `#ffccd5` | 3.326162240606473 | 4.5:1 |

Choose another exact token for a failed pair; preserve an explicit error cue.
These calculations exclude real host compositing, layout and interaction.

Primary sources were fetched and reviewed on this date:
[Nielsen heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/),
[heuristic evaluation](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/),
[text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html),
[non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html),
and [color redundancy](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

## Deterministic and repository checks

The project verifier passes **20/20** checks: identical palette copies,
17/37 token counts, ten unique heuristic IDs, 20 internal links, required
decision/evidence rules, nine valid token-role rows and 13 unrounded contrast
expectations. Two independent semantic reviews found no blocking issue.
H5 was refined before freezing to avoid requiring confirmation for every
ordinary change; it calls for appropriate review of high-cost or irreversible
actions.

The source helper now recognizes the exact `nngroup.com`, `www.nngroup.com`,
`w3.org` and `www.w3.org` hosts while retaining exact catalog matching and
spoof protection. All **53/53** source cases and **33/33** unchanged report
cases pass. All 72 cataloged primary URL occurrences in SKILL and references
pass the source audit. These helpers do not browse or verify usability.

```powershell
uv run --script projects/desktop-plugin-ui/scripts/verify-design-contract.py --output projects/desktop-plugin-ui/artifacts/data/design-contract-review-v2-20261025.json
uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py
uv run --script projects/desktop-plugin-ui/scripts/test-report-checker.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

Repository checks pass. The scoped authoring audit passes source/runtime/full,
with matching identities and no authoring findings. Large local artifacts and
raw runs remain ignored. No published example or Pages source changed.

## Isolated design study

The deliberate model exception remains `openai-codex/gpt-5.6-luna` because
Spark was rejected by the signed-in account in the earlier study. No Claude
or Copilot model allowance is used. Every case is closed-book advisory work:
no network, host operation, account/configuration change, installation or
prototype rendering. All payloads are read-only.

The frozen study has one contract case, three independent naturalistic
repetitions and one host-boundary case. Acceptance requires strict JSON,
exact outputs, false task-level acceptance/testing flags, observed Luna,
zero tool errors, a clean read surface, unchanged payload and independent
review of the requested design decisions. Do not pool this narrower study
with earlier broad capability cohorts.

| Case | Prompt SHA-256 | Exact output pair |
| --- | --- | --- |
| Contract | `635da51c6847200a9de696720d3ee50c8f7b66b40ce56db922bd4d6e733f154c` | `design/ui-review.md`, `design/ui-contract.json` |
| Naturalistic | `cceb724c433057106a5cab36e1505cf1c26dbe5c093b7072d6b66630aed83ad9` | `design/queue-audit.md`, `design/queue-audit.json` |
| Host boundary | `536f3ddb3fdb543e592592d11a41445adeda8054f4645aaaaa53df4367fb4509` | `review/design-host-boundary.md`, `review/design-host-boundary.json` |

The first design subject, `bcc6c0051fa2ceaf157a86a58444436d7fad694bec56b586f415aebc53121a86`,
passed strict execution in all five runs. Conservative full acceptance was
**3/5**: contract 0/1, naturalistic 2/3, boundary 1/1. Preserve its failures:
the contract's opening conflated local Claude deployment with ChatGPT, and a
JSON row classified an entire MCP App plus host frame as `host-mapped`;
naturalistic run 2 replaced requested short labels with full heuristic names.
The ten principles, palette values and computed contrast were correct.

The second subject adds explicit ChatGPT remote-transport wording, separate
authored iframe/host-chrome scope records and verbatim requested heuristic
labels. All prompts are unchanged. Its five fresh v2 runs pass strict execution
**5/5** and conservative full acceptance **4/5**. Do not combine v1 and v2 passes.

| Final v2 case | Strict | Independent full acceptance | Retained limitation |
| --- | --- | --- | --- |
| Contract | 1/1 | 0/1 | One purported exact source-token path is incomplete: `red.status` instead of `colors.red.status`. All 14 color values, H1-H10, default CS1, contrast repairs and host ownership are correct. |
| Naturalistic | 3/3 | 3/3 | Run 3 groups declined `false` and cancelled `null` as cancellation; implementation should distinguish them. Both avoid committing. |
| Host boundary | 1/1 | 1/1 | Ownership is explicit and correct, but one row describes both iframe and host frame rather than using the reference's preferred separate records. No literal row-structure compliance is claimed. |

The contract failure is an agent/artifact-contract provenance failure, retained
without output repair or rerun. The source/report helper checks URLs and
evidence fields; it does not validate YAML token paths. All 28 optional
naturalistic contrast calculations were independently recomputed: 8/12/8 pairs,
maximum absolute printed-value error 0.000325302 with tolerance 0.005. Every
extracted color belongs to CS2, with 21/19/19 distinct values by run. All v2
traces observe Luna, zero tool errors, clean read surfaces, exact outputs,
false task-level UI/testing flags and unchanged 19-file payloads. No actual
host rendering or user study was performed for these advisory cases.

The versioned prompts and exact per-case reproduction commands are retained
in the linked reports. Run IDs are
`20261025-desktop-ui-design-contract-v2-luna-1`,
`20261025-desktop-ui-design-naturalistic-v2-luna-{1,2,3}` and
`20261025-desktop-ui-design-boundary-v2-luna-1`. Each command uses the repo
isolated harness, `--mode json --strict`, the documented Luna exception,
every exact output and false JSON-field gates. No subject received retries.

Final v2 records:
[contract](design-contract-v2-luna-1.md),
[three naturalistic runs](design-naturalistic-v2-luna.md),
[boundary](design-boundary-v2-luna-1.md).

Retained v1 records:
[contract](design-contract-v1-luna-1.md),
[three naturalistic runs](design-naturalistic-v1-luna.md),
[boundary](design-boundary-v1-luna-1.md).

The ignored local installation matches all 19 final source files and passes
bundle validation. Scoped sync wrote only this skill; the verified temporary
sync stages were moved into ignored project artifacts after completion.

## Broader release boundary

Keep the skill **validating**. This design-rule update does not rerun or erase
the broader v4 failures or establish new UI paint, user testing or accessibility
conformance. Earlier factual/evidence-label errors and pending real host checks
remain recorded in the
[cross-assistant report](cross-assistant-validation-20261024.md).
