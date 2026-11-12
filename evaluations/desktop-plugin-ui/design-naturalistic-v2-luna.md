# Desktop plugin UI design naturalistic validation, v2

Date: 2026-10-25. This cohort tests the final usability/palette guidance on a proposed support-ticket plugin. It is separate from [v1](design-naturalistic-v1-luna.md) and the retained cross-assistant cohorts. The skill's overall status remains `validating`; scoped design success does not clear unrelated failures or establish actual host acceptance.

All three fresh sessions used the same frozen 19-file runtime bundle, payload SHA256 `d02ed682c82aaa66db71ca29019b3d866145c2a314bb0db3714dcde4d7c8f038`. The [unchanged prompt](../pi-prompts/desktop-plugin-ui-design-naturalistic.md) had SHA256 `cceb724c433057106a5cab36e1505cf1c26dbe5c093b7072d6b66630aed83ad9` (4077 source bytes). Compared with v1, the bundle clarified exact requested heuristic labels, separated authored iframe paint from host chrome, and clarified ChatGPT's supported remote transport requirement. The prompt and acceptance criteria were unchanged.

The documented account exception selected `openai-codex/gpt-5.6-luna` instead of Spark. All sessions used JSON strict mode, high thinking, a 600-second timeout, isolated read-only skill copies, exact output paths, and three false task-level acceptance fields. There were no retries, favorable rerolls, reviewer output edits, or bundle mutations during the cohort.

## Outcomes

| Retained raw run | Duration | Strict harness | Independent final report checker | Manual review | Joint |
| --- | --- | --- | --- | --- | --- |
| [v2-luna-1](../runs/20261025-desktop-ui-design-naturalistic-v2-luna-1/) | 88.301 s | Pass | Pass; 9 official URL occurrences, 3 historical rows | Pass | Pass |
| [v2-luna-2](../runs/20261025-desktop-ui-design-naturalistic-v2-luna-2/) | 106.113 s | Pass | Pass; 30 official URL occurrences, 0 top-level historical rows | Pass | Pass |
| [v2-luna-3](../runs/20261025-desktop-ui-design-naturalistic-v2-luna-3/) | 100.409 s | Pass | Pass; 22 official URL occurrences, 3 historical rows | Pass with the terminal wording caveat below | Pass |

Strict: **3/3**. Manual: **3/3**. Joint: **3/3**. This satisfies the scoped naturalistic repetition threshold. No failure was hidden or replaced; v1's short-label substitution failure remains recorded separately.

Each raw folder retains its manifest, strict harness checks, full event trace, generated artifacts, and independent `read-surface.json`, `independent-artifact-check.json`, and `independent-contrast-check.json`. Exact output files are `workspace/design/queue-audit.md` and `workspace/design/queue-audit.json`.

## Independent artifact review

Every output contains ten heuristic records, with all requested fields and correct numbering and short principle labels. Each finding names evidence from the proposed design, gives a specific implementation change, and proposes an unperformed acceptance check. The ten mappings cover status, familiar language, exits, conventions, mistake prevention, recognition, efficient routes, minimal content, useful errors, and contextual help. No report invents observed UI behavior or measured user impact.

The JSON contract provides separate `number` and `name` fields and does not prescribe their exact JSON type or require an H-prefix inside `name`. Review therefore evaluates the pair together: run 1 uses numeric `1` and `Visible status`; run 2 uses numeric `1` and `H1 Visible status`; run 3 uses `H1` and `Visible status`. All preserve the requested number and exact short label. This does not excuse v1 run 2, which replaced the short labels with different full principle names.

All three select explicit `colorset2`, bind surfaces/text/interactions/status to exact bundled tokens, and separate authored app paint from host chrome and mandatory accessibility overrides. Independent extraction found 21, 19, and 19 distinct hexadecimal colors, with **zero unlisted values**. Status has redundant words/icons/shapes; selected/focus states are explicit; links retain cues. Weak light-gray focus is rejected and error copy uses dark ink rather than bright red on pale red. Terminal paint is not asserted to have exact palette pixels. No palette or sample calculation is presented as full accessibility acceptance.

Every reported contrast pair was independently recomputed using sRGB linearization and `(Lmax + 0.05) / (Lmin + 0.05)`:

| Run | Recomputed JSON pairs | Accurate within 0.005 | Maximum absolute printed-ratio error |
| --- | --- | --- | --- |
| 1 | 8 | 8 | 0.000311545 |
| 2 | 12 | 12 | 0.000325302 |
| 3 | 8 | 8 | 0.000311545 |

All **28/28** calculations agree. Markdown pairs and printed values match the JSON calculations. The stated ordinary-text decisions agree with unrounded thresholds: error red on pale red is about 3.326:1, and success green `#36b300` on pale green is about 2.523:1; run 1 correctly rejects both for ordinary text and supplies dark text plus redundant cues. These checks cover opaque authored colors, not compositing, font rendering, focus behavior, or a rendered host.

All three recommend a workable app-owned MCP Apps route for ordinary Claude Desktop Chat and Copilot VS Code, with useful text/structured results. Claude fullscreen is optional and negotiated; Copilot's documented inline-only surface remains usable. Host chrome and permission/consent UI retain host ownership. The recommendations preserve filters, ticket identity, drafts and last successful data; include validation and authoritative server state; name pending/error/retry/cancel behavior; and make filtered export capability-dependent with text/CSV fallback. Terminal commands are proposed workflow semantics, not invented installed commands.

Historical evidence remains scoped to other synthetic apps, builds, native webviews, terminal forms, or browser fixtures. No output promotes extension-webview or protocol-fixture success into Copilot Chat acceptance. Run 2 places its historical records under `sources.historical_bundle_observations`; the generic checker reports zero top-level historical rows, so the reviewer inspected those nested rows manually. Their successful historical Claude/CLI observations have canonical `observed-working` evidence and scope. The additional current-queue `untested` row is explicitly current work, despite that array's broad name. All three task-level booleans are literally false.

**Retained wording caveat:** run 3's terminal paragraph groups confirm `false` and `null` as cancellation. Both safely avoid an accepted mutation, but a declined confirmation and Escape cancellation should remain distinguishable when the host exposes them. The proposed flow needs that refinement during implementation. This is a bounded terminology limitation, not a claim that the host treats those return values identically or evidence of host acceptance. No output was edited and no run was repeated to remove the caveat.

## Trace and read surface

The strict harness and independent event summaries all pass: only `gpt-5.6-luna` through `openai-codex` is observed, with zero invalid JSON and zero tool errors. Every trace reads the prompt first and `SKILL.md` immediately afterward, creates the exact files, runs `check_reports.py` on both completed artifacts, and leaves the frozen payload unchanged. No session calls a provider tool, uses the network, installs software, opens an external application, or renders a prototype.

Unique read paths including prompt and entry point number **12, 11, and 13**. All sessions read the selected ColorSet2 asset and the eight relevant references: `assistant-surface-matrix.md`, `bridge-patterns.md`, `chat-patterns.md`, `claude-chat-live.md`, `copilot-limits.md`, `distribution.md`, `evidence-and-probing.md`, and `usability-and-color.md`. Run 1 also reads `check_reports.py`; run 3 reads both checker scripts; run 2 executes the checker and source catalog without reading their source. No session reads acceptance examples, galleries, sibling skills, repository documentation, external project evidence, or account material. The largest reference is `chat-patterns.md` at 10,419 bytes; no approximately 50 KB source is read.

## Commands

For each recorded `N` equal to 1, 2, and 3, the launch was:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-design-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261025-desktop-ui-design-naturalistic-v2-luna-N --expect-output design/queue-audit.md --expect-output design/queue-audit.json --expect-output-json-field design/queue-audit.json::host_acceptance_verified=false --expect-output-json-field design/queue-audit.json::task_empirical_tests_performed=false --expect-output-json-field design/queue-audit.json::rendered_ui_verified=false --timeout-seconds 600
```

Independent deterministic checks used the actual numbered run directory:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-design-naturalistic-v2-luna-N/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261025-desktop-ui-design-naturalistic-v2-luna-N/read-surface.json
uv run --script evaluations/runs/20261025-desktop-ui-design-naturalistic-v2-luna-N/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-design-naturalistic-v2-luna-N/workspace/design/queue-audit.md evaluations/runs/20261025-desktop-ui-design-naturalistic-v2-luna-N/workspace/design/queue-audit.json --fail-on-findings
```

Do not reuse these IDs for new attempts. The retained manifests bind the actual command, prompt, payload, exact outputs, model, and environment.

## Artifact hashes

| Run | `queue-audit.md` SHA256 | `queue-audit.json` SHA256 |
| --- | --- | --- |
| 1 | `a30e85f88bbe7ed8b3aaa7d1a44c316a613b08933f6ea8d38a47e0ca325e4bb2` | `082bd5a6459f2f221096e8c0fc626862b6a229e731832769a0ebb6ba12fd606b` |
| 2 | `9bac2debd3cf69a8690672de1b58d7cfb163c92fd89168537124cb995ea5b6e1` | `251aad265f2f3596ae55da6fad515bc1f4bd1fe583a9fafdf39c3eec6dcee984` |
| 3 | `952825e8cc5f069fb5a4a626872943c34982931ed98b087f8611ce873812d3c3` | `f57bf9c82cea78d9e16c8d60b78269d8eb3380b8de0640df767690f67e870b48` |

This cohort validates bounded design-audit output, not an implemented ticket queue. No new UI paint, user study, account action, export delivery, or actual host acceptance occurred in these runs.
