# Independent composition forward review

Date: 2026-10-31. Skill: `desktop-plugin-ui`. Reviewer: independent delegated agent; no skill edits or forward-run restarts. Basis: the [frozen criteria](composition-criteria-20261031.md), complete generated artifacts, strict harness results, evaluator-owned JSON structure checks and inspected runtime traces.

The final **contract is 1/1 joint strict/artifact pass**, and the final **naturalistic cohort is 3/3 joint strict/artifact passes**, exceeding its frozen 2/3 threshold. This is acceptance of the narrow composition-guidance revision on the recorded model, not a whole-skill release or actual-host UI acceptance.

## Subject and results

All four runs copied the same 39-file runtime payload, SHA-256 `48a9e002e36aaa756babd78af3b7ae52d3d33c223002c7e9dd38a144bcddbf6b`. Run manifests select `openai-codex/gpt-6.1-sol`, medium reasoning, strict JSON mode, with ambient context/extensions/skills/templates/themes disabled and exactly the copied skill loaded. This is the already recorded model exception permitted by the frozen criteria; it does not change thresholds or establish Spark acceptance.

Run IDs have the prefix `20261031-desktop-ui-composition-` and live under `evaluations/runs/`:

| Final suffix | Required artifact(s) | Duration | Strict | Independent artifact | Joint |
| --- | --- | ---: | --- | --- | --- |
| `final-contract-sol-1` | `deliverables/choice.md` | 44.318 s | Pass | Pass | Pass |
| `final-naturalistic-sol-1` | `deliverables/review.md`, `deliverables/acceptance.json` | 248.156 s | Pass | Pass | Pass |
| `final-naturalistic-sol-2` | Same two exact paths | 230.806 s | Pass | Pass | Pass |
| `final-naturalistic-sol-3` | Same two exact paths | 208.248 s | Pass | Pass | Pass |

Each strict result reports exit 0, no timeout, exact required outputs, accepted events and unchanged skill payload. No final-cohort infrastructure or execution failure occurred. Earlier subjects, failures and model-provider attempts remain separate; none is pooled into these counts.

## Independent semantic review

The contract chooses one native Pi selector opened by a deterministic command, with explicit `compact|standard|detailed` arguments. It avoids a server, model-facing tool or custom UI for three choices. RPC request correlation, missing/timeout behavior, no-UI arguments and `mode === "tui"` versus `hasUI` are distinguished. Candidate state remains separate from the committed preference, cancellation does not mutate, and revision checks reject stale replies. Other extensions retain their status/keys, and focus restoration and narrow/theme checks are proposed honestly. This meets every contract criterion without an execution or paint claim.

All three naturalistic artifacts keep the selected export's identity, authoritative outcome and next action discoverable. They remove duplicate chat input, equal-priority actions and unnecessary branding footer replacement; all 12 records remain accessible through an on-demand finder. Summary, inspector, transient status and durable result have different jobs rather than replicating the queue. Each explicitly describes the cost of reduced permanent queue visibility or leaves finder size to later user testing.

Each separates Codex desktop from CLI, Pi TUI from RPC, and Claude Desktop Chat from native Code. Codex transport is not promoted to frontend paint or sidebar support; historical desktop evidence remains bounded. Pi does not treat RPC `hasUI` as custom TUI capability. Claude Chat uses an MCP App while Code uses native controls and placement checks. Larger modes depend on actual capabilities and their returned mode. Other-extension status, shared prompt content, notifications, keys and disposal receive concrete coexistence checks.

State plans cover stable identity/version, direct-input and dialog authority, stale and late replies, duplicate retry effects, cancellation acknowledgement, completion races and recovery after uncertain outcomes. Closing a view differs from cancelling work; reopening refreshes authority. Selection, query/draft and focus survive supported expansion and recovery intentionally. A local revision guard is not mistaken for a remote transaction. No major state/interaction omission was found.

Deterministic actions use ordinary handlers/tools rather than chat submission. Plans require dispatch instrumentation and separate inference from network/tool traffic. Naturalistic 2 additionally distinguishes conversational Codex entry from direct deterministic handler execution. Claims of executed work are limited to palette arithmetic and own-artifact structural validation, which match the inspected bash commands.

All outputs provide concrete H1-H10 notes, exact authored colorset1 roles, host-owned/native styling boundaries, redundant status cues and preserved accessibility overrides. They distinguish arithmetic contrast from actual rendered pairs. Fair visual plans keep task, record/state, viewport/container, theme and conversation draft comparable; label the baseline proposed; require actual pixel inspection; and independently exercise keyboard, error/retry, focus and state. Actual-host and representative-user conclusions remain explicitly untested.

Scenario evidence is independently actionable and consistent with each Markdown design:

- Naturalistic 1: A03-A10 cover cancel/state/retry/expansion; A11-A17 cover host limits/coexistence; A18-A21 cover keyboard/palette/inference/fair comparison; A22 covers users.
- Naturalistic 2: A03-A09 cover authority/cancel/late reply/expansion; A10-A18 cover host routing/coexistence/artifact effects; A19-A22 cover accessibility/comparison/users/lifecycle.
- Naturalistic 3: S04-S13 cover authority/idempotency/uncertain outcome/cancel/reopen; S14-S20 cover inference/modes/coexistence; S21-S26 cover pixels/Codex boundaries/palette/keyboard/real inspection/users.

No required-artifact absence, false execution claim, incorrect host contract, unsupported universal claim or major semantic omission was identified. No material advice gap warrants failing an artifact. These are procedure specifications, not delivered automation; the prompt requested plans and no implementation.

## Structure and read-surface checks

Ran `uv run --script projects/plugin-ui-exploration/scripts/check_forward_acceptance.py` independently from the evaluator workspace: exit 0, all three plans pass. Plans contain **22, 22 and 26** scenarios respectively, with **13, 11 and 12** nonempty string limitations. Every scenario has nonempty `id`, `surface`, `state`, `action`, `expected`, and `layer`; IDs are unique within each plan. This checker validates structure, not the semantic judgments above.

For each of the four final run IDs, ran `scripts/summarize-pi-json-events.py` with `--require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error --require-tool-call --require-read ../prompt.md`, plus gallery and sibling-skill read prohibitions. Every invocation exited 0: no invalid JSON/event records, tool errors or forbidden-read finding. Model observations are exclusively `openai-codex` / `gpt-6.1-sol`.

The contract reads the prompt, entry, and five relevant Pi/interaction/composition/usability references: seven completed reads. The naturalistic runs use 15, 15 and 13 reads, covering the prompt, entry, matrix/composition/vision/usability/state guidance, selected Codex/Pi/Claude host references, and colorset1. No acceptance gallery, sibling skill, repository document, project artifact or host/global configuration is read. The six-surface question explains the broader host-reference set; no large fixture/source read substitutes for compact runtime guidance. Full bash commands were inspected: only the bundled palette helper and JSON/existence checks of the generated deliverables ran, with no hidden discovery or external/model operation.

Machine results are under `projects/plugin-ui-exploration/artifacts/manifests/`: `forward-independent-review.json`, `forward-acceptance-structure.json`, `forward-contract-sol-1-trace.json`, and `forward-naturalistic-sol-{1,2,3}-trace.json`. They retain per-run results and read lists. Generated acceptance scenarios remain unexecuted; this review establishes neither visual quality nor actual-host paint, keyboard/OS effects, interoperability or user preference.
