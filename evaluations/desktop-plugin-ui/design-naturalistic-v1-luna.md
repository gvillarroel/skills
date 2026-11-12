# Desktop plugin UI design naturalistic validation, v1

Date: 2026-10-25. This is a scoped forward test of the added usability and palette guidance. It does not supersede the retained cross-assistant cohorts or change the skill's overall `validating` status.

Three fresh, independent sessions used the same frozen 19-file runtime bundle, payload SHA256 `bcc6c0051fa2ceaf157a86a58444436d7fad694bec56b586f415aebc53121a86`. The [unchanged naturalistic prompt](../pi-prompts/desktop-plugin-ui-design-naturalistic.md) had SHA256 `cceb724c433057106a5cab36e1505cf1c26dbe5c093b7072d6b66630aed83ad9` (4077 source bytes). The documented account exception selected `openai-codex/gpt-5.6-luna` instead of Spark. All runs used JSON strict mode, high thinking, a 600-second timeout, isolated skill copies, exact output paths, and three false task-level acceptance fields. There were no retries, favorable rerolls, output edits by the reviewer, or bundle changes during these runs.

## Per-run outcomes

| Run and retained raw evidence | Strict harness | Independent report checker | Manual artifact review | Joint outcome |
| --- | --- | --- | --- | --- |
| [v1-luna-1](../runs/20261025-desktop-ui-design-naturalistic-v1-luna-1/) | Pass; 107.925 seconds | Pass; 24 official URL occurrences, 2 historical rows | Pass | Pass |
| [v1-luna-2](../runs/20261025-desktop-ui-design-naturalistic-v1-luna-2/) | Pass; 128.463 seconds | Pass; 21 official URL occurrences, 3 historical rows | Fail: requested short labels were replaced | Fail |
| [v1-luna-3](../runs/20261025-desktop-ui-design-naturalistic-v1-luna-3/) | Pass; 107.655 seconds | Pass; 30 official URL occurrences, 3 historical rows | Pass | Pass |

Strict: **3/3**. Manual: **2/3**. Joint: **2/3**. This meets the repository's scoped naturalistic repetition threshold. The failed row remains retained; it is not pooled with earlier or future cohorts.

Each raw folder contains `run-manifest.json`, `evaluation-result.json`, `events.jsonl`, `event-check.json`, `artifact-check.json`, `json-field-check.json`, `skill-integrity-check.json`, and reviewer-created `read-surface.json`, `independent-artifact-check.json`, and `independent-contrast-check.json`. The exact generated files are `workspace/design/queue-audit.md` and `workspace/design/queue-audit.json`.

## Manual findings

All three outputs assess exactly ten heuristics numbered 1 through 10. Each includes the required brief evidence, recommendation, proposed acceptance check, outcome, and scoped evidence. The findings are grounded in the supplied proposal: invisible refresh/save state; protocol vocabulary; immediate changes and weak exits; inconsistent action labels; unsafe edits; disappearing context; missing keyboard paths; decorative content before tickets; destructive error handling; and missing help/export scope. Outcomes are design-brief `issue` findings, with current runtime evidence `untested`. None claims a completed user study or measured task improvement.

Run 2 uses the correct full Nielsen names, such as `H1 — Visibility of system status` and `H6 — Recognition rather than recall`, in both artifacts. The prompt explicitly requests the bundled short labels, such as `H1 Visible status` and `H6 Recognition cues`. All ten run-2 names differ from those requested labels. This is a bounded **artifact-format/instruction-following failure**, not an incorrect mapping of the Nielsen principles or a factual UI-capability failure. Runs 1 and 3 preserve all ten bundled short labels.

All outputs select explicit `colorset2` and provide concrete roles for surfaces, text, interaction, and status. Independent extraction found 21, 24, and 17 distinct hexadecimal colors respectively; every color appears in the copied ColorSet2 palette. The app-owned View receives exact authored tokens. Host chrome, consent, terminal paint, and mandatory accessibility overrides remain host-owned or mapped. Status uses words/icons/shapes in addition to color; links retain action cues; weak gray focus is rejected; ordinary error copy uses dark ink on the pale error background. The reports do not infer full-interface accessibility from a palette.

The independent reviewer recomputed **every JSON contrast claim**, covering 13, 8, and 11 pairs respectively (32 total), using sRGB linearization and `(Lmax + 0.05) / (Lmin + 0.05)`. All printed ratios agree within 0.000326, below the 0.005 rounding tolerance. The stated ordinary-text classifications agree with the unrounded calculations. In particular, red `#e8002a` on pale red `#ffccd5` is about 3.326:1 and is rejected for ordinary text; dark `#333e48` on that surface is about 7.721:1. Markdown repeats the same pairs and rounded values. These are opaque-color arithmetic checks, not rendered compositing or accessibility acceptance.

The surface recommendations keep Claude Desktop's optional negotiated fullscreen separate from Copilot VS Code's documented inline-only MCP Apps surface. Both retain an inline task path and useful text/structured tool results. All provide draft/save/cancel, authoritative server state, retained data after errors, recognizable filters, keyboard/focus work, and capability-dependent filtered export with fallback. Confirmation and recovery are proposed for consequential resolution. Cancellation checks remain implementation requirements; they do not prove that an already accepted server mutation can be revoked. Actual cancellation and late-response behavior still require target-host verification.

Historical rows distinguish actual Claude Desktop Chat, Copilot CLI terminal forms, browser fixtures, and the separate VS Code extension webview route. They explicitly exclude acceptance of this queue and untested Copilot Chat paint. Run 3's webview row uses the broader MCP guide link as context rather than a direct webview-probe provenance link; the claimed observation is attributed to the supplied snapshot. The row does not equate that extension route with Copilot Chat rendering. No current-task empirical success is inferred. All three JSON acceptance booleans are literally false.

Run 2 initially received diagnostic report-checker findings for historical evidence formatting, repaired its own JSON, and reran the diagnostic checker successfully. These were data findings with exit 0, not tool errors; the trace retains the complete repair. The independent reviewer did not alter its output.

## Trace and read-surface inspection

All three traces observe only `gpt-5.6-luna` through `openai-codex`, with zero invalid JSON records and zero tool errors. Every run reads the prompt first, then `SKILL.md`. Every copied skill passes its unchanged-payload gate. No trace reads acceptance examples, sibling skills, repository documentation, external account data, or project evidence. No model run uses the network, installs software, renders a prototype, or opens an external application.

All three read the eight task-relevant references `assistant-surface-matrix.md`, `bridge-patterns.md`, `chat-patterns.md`, `claude-chat-live.md`, `copilot-limits.md`, `distribution.md`, `evidence-and-probing.md`, and `usability-and-color.md`, plus the selected `assets/palettes/colorset2.yaml`. Run 1 also reads both checker scripts; run 3 reads `check_reports.py`; run 2 uses the checker's help and execution path. Unique read paths including prompt and entry point are 13, 11, and 12. These are compact references rather than fixture/gallery source. The largest reference read is `chat-patterns.md` at 10,419 bytes; no approximately 50 KB source is read.

## Reproduction commands

Run once for each `N` equal to 1, 2, and 3; the recorded IDs must not be reused for a new attempt:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-design-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261025-desktop-ui-design-naturalistic-v1-luna-N --expect-output design/queue-audit.md --expect-output design/queue-audit.json --expect-output-json-field design/queue-audit.json::host_acceptance_verified=false --expect-output-json-field design/queue-audit.json::task_empirical_tests_performed=false --expect-output-json-field design/queue-audit.json::rendered_ui_verified=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-design-naturalistic-v1-luna-N/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261025-desktop-ui-design-naturalistic-v1-luna-N/read-surface.json
uv run --script evaluations/runs/20261025-desktop-ui-design-naturalistic-v1-luna-N/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-design-naturalistic-v1-luna-N/workspace/design/queue-audit.md evaluations/runs/20261025-desktop-ui-design-naturalistic-v1-luna-N/workspace/design/queue-audit.json --fail-on-findings
```

## Artifact hashes

| Run | `queue-audit.md` SHA256 | `queue-audit.json` SHA256 |
| --- | --- | --- |
| 1 | `1de36fa52402b6466152caf42f3d7a16073a10f043d0ed19578ce6071941b23a` | `e7056e85e035b173b18163aa5349b453414c9328533462abd01b928c26bd4083` |
| 2 | `82e7bb8e1a87edc9e4ca0a97e1f4a5fc02d10909c9f84c9907a0207994a2eb98` | `0b81decd726ac1995a9c9f3f851cbcab665ad02a50a60b8d462e649566af26d3` |
| 3 | `025a222d867edbb031e50bf48b9f064cd7993860fc3e9cf2818e581812efdc2e` | `f366482af9cb76b1dc6fd0286ced9670361ce6cc29c38272c62130ea80d702ed` |

These outcomes validate the frozen bundle's ability to produce a bounded design audit. No ticket plugin was built, rendered, installed, exercised with users, or accepted in a host during this cohort. Earlier empirical evidence remains historical and separately scoped.
