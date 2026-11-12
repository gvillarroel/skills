# Capability-offerings naturalistic study, version 1

Reviewed October 25, 2026. Exactly three independent sessions were run against the frozen 21-file `desktop-plugin-ui` runtime bundle. **Strict harness: 3/3; report checker: 3/3; conservative manual acceptance: 0/3; joint strict/manual acceptance: 0/3.** All attempts and final outputs remain intact. No retries, output repairs, canonical edits, renderer builds or new host/UI tests were performed by this review.

The recommendations contain useful positive offerings, English queue copy, realistic state ownership, and correct explicit palette values. Manual failures concern incomplete historical-claim records in runs 1/3 and a concrete mechanism mix-up in run 2. Checker success did not establish full factual or evidence coverage. This cohort does not satisfy the pre-frozen naturalistic threshold of at least 2/3 joint acceptance and does not establish broad skill completion.

## Frozen inputs and command

- Source/runtime/full subject: `26b12b4879ba0e4663b7d225bba066424f1baa1dee7d1461ba1c84a4de1060a5`, 21 files. Every run manifest records this subject; integrity checks pass unchanged.
- [Naturalistic prompt](../pi-prompts/desktop-plugin-ui-offerings-naturalistic.md): original file SHA-256 `a7ff09f0ef63e3ba30c7502eb32f2228195d634e88fd593c9b5344526579938b`.
- [Pre-frozen review criteria](offerings-review-criteria.md): SHA-256 `4e6d0d0a0f85c04cc7a73c4a89a8ae8d81f8a4caf8c87b6f9658832173b4d590`. Criteria were read before launch and were not revised after seeing outputs.
- The harness hashes normalized prompt text as `62e1a5e84349933dc124de095d5ab5401032a43c6ba79e16fd2145282bb7f447`. Each copied prompt has byte SHA-256 `5d37bd25f99483d32e414fb288caa1f1d7b2814a886d04e92b602987732011b3`; independent text comparison with the frozen source passes. These hashes differ because the harness reads universal newlines and writes a Windows text copy, not because the request changed.
- Model exception: `openai-codex/gpt-5.6-luna`, documented for this study; Pi 1.4.0, JSON mode, high thinking, 600-second timeout. Ambient context, extensions, discovery, templates, themes and session persistence were disabled by the isolated harness.

The command below was executed once for each suffix `1`, `2`, `3`, with the corresponding exact run ID:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-offerings-naturalistic.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-offerings-naturalistic-v1-luna-1 --expect-output offerings/recommendation.md --expect-output offerings/recommendation.json --expect-output-json-field 'offerings/recommendation.json::host_acceptance_verified=false' --expect-output-json-field 'offerings/recommendation.json::task_empirical_tests_performed=false'
```

Required-model summaries were independently generated with `summarize-pi-json-events.py --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md` and forbidden fixture/sibling-skill read patterns. All three summaries pass: only `gpt-5.6-luna` through `openai-codex`, valid event JSON, zero tool errors, prompt-first reads, exact outputs and unchanged skill copies.

## Per-run findings

| Run suffix | Duration | Strict / checker | Manual / joint | Accepted checks and retained limitation |
| --- | --- | --- | --- | --- |
| 1 | 131.510 s | PASS / PASS | FAIL / FAIL | Six useful offering records; 13/13 exact token bindings; 7/7 ratios; all H1-H10 labels. Historical-claim coverage is incomplete. A critical text/accent pairing is also ambiguous, without an explicit wrong numeric claim. |
| 2 | 115.368 s | PASS / PASS | FAIL / FAIL | Five useful offering records; 10/10 exact token bindings; 6/6 ratios; all H1-H10 labels. Ordinary webview guidance incorrectly uses MCP Apps CSP metadata names. |
| 3 | 122.965 s | PASS / PASS | FAIL / FAIL | Four client offering records with optional MCP App/canvas routes; 11/11 exact token bindings; 5/5 ratios; all H1-H10 labels. Historical-claim coverage is incomplete. |

Run IDs are `20261025-desktop-ui-offerings-naturalistic-v1-luna-{1,2,3}`. Each local folder contains `run-manifest.json`, `evaluation-result.json`, `events.jsonl`, `trace-summary.json`, the immutable generated pair in `workspace/offerings/`, and `independent-review.json`. The independent inspection script is retained under ignored runs as `evaluations/runs/offerings-naturalistic-review.py`.

**Runs 1 and 3: historical-coverage failures.** The prompt expressly requires every empirical historical claim used to have a row containing host, surface, version, layer, result and a canonical observation label inside `evidence`. Run 1 JSON line 60 states observed `mcpApps:false`, and line 71 reports the Restricted Mode / Models unavailable / Sign In workspace gate. Its six `historical_observations` rows (from line 290) do not record these claims in a matching result. Run 3 similarly uses the terminal capability at line 117 and the observed workspace gate at line 159; its seven history rows (from line 337) omit these results. Existing terminal-form or ordinary-webview rows do not supply those missing results. The underlying facts agree with the frozen bundle, but the requested evidence record is incomplete. This is an artifact/evidence-coverage failure, not a claim that the host facts are false. The checker checks listed rows; it cannot detect omitted observations.

**Run 2: mechanism-contract failure.** `recommendation.json` line 69 places “declare only required connectDomains, resourceDomains, and frameDomains” in the ordinary VS Code extension webview offering. Those are MCP Apps resource CSP metadata names. An ordinary extension webview needs its own HTML Content Security Policy and source directives/nonce. The surrounding narrow-CSP and privileged-extension bridge advice is useful, but this instruction transfers a different surface's configuration contract and is a substantive factual failure under the frozen mechanism criterion.

Run 2 also puts newer package/core inventory in the unversioned desktop-capture history row (line 232), while explicitly saying the capture's build was not recorded. Keep the capture version unknown and inventory in a separate record to avoid misleading attribution. Runs 2/3 refer to `never` automatic decline with `observed-failed` presentation wording; policy decline itself is a normal outcome. These wording concerns are retained separately from the decisive CSP error.

**Run 1: color ambiguity, not an additional automatic failure.** The JSON role “critical text/accent” at line 239 uses `#e8002a`, and a separate critical background is `#ffccd5`, without an explicit ordinary-text replacement for that pairing. Independent arithmetic gives red/pink **3.326162240606473:1**, below 4.5:1 ordinary text, although red on white passes. No artifact explicitly reports a false red/pink ratio or renders the pair. This is an ambiguous styling instruction to clarify, not evidence of painted failure. Run 3 explicitly selects `#333e48` for ordinary critical text and red for the labelled icon/accent; run 2 warns against sole red error text on pink.

No hidden method-specific response table was imposed. All three outputs tell the caller to interpret `false` and `null` by method/action and avoid treating either as a saved priority. None equates valid Boolean false with a missing value or discards a business field through a default. More concrete callback mapping would improve implementation guidance, but its absence is not an added prompt requirement.

## Scoped passes and trace review

- Exact outputs and all requested top-level JSON fields: 3/3. Both current-task booleans are literally false in all three; `language` is `en` and all reviewed authored visible/accessibility/help/fallback copy is English. `T-104`, `high`, `pending` and `E_INVALID_PRIORITY` remain intact.
- Positive offering coverage: 3/3 include tool/text delivery, bounded terminal forms, conditional MCP Apps, ordinary extension webviews and canvas prerequisites/fallbacks. Search, selection, staged Save/Cancel, status chart/table, refresh/recovery, selected CSV and Explain all have concrete routes and copy. Webview is recommended for dense owned dashboards without requiring that architecture as a hidden grading preference.
- State plan: 3/3 separate server-authoritative business values from client selection/draft/preferences; refetch/version checks, stale-save rejection, last-successful snapshots and conditional storage are explicit. Mock process state is not presented as durable storage.
- Version/evidence scope: npm 0.145.0 and desktop-bundled 0.164.0-alpha.11.1 are distinguished; the desktop package is recorded separately. No output assigns the old npm MCP limitations universally to the current desktop. No output claims direct IDE MCP is unavailable because plugin bundles are unavailable. Desktop/IDE paint and signed-in Copilot Chat acceptance remain surface-specific. Run 1 uses the corrected serving-process form evidence and version-specific nested-schema refusals; no run repeats the withdrawn missing-serving-connection explanation.
- English/default ColorSet/heuristic checks: 3/3 use default colorset1, separate authored iframe/webview paint from host chrome/forms/terminal/accessibility overrides, and include all ten exact H IDs/labels with queue-specific checks. These are design inspections and recommendations, not user studies or rendered accessibility certification.
- Exact JSON token/value bindings: **34/34** resolve against the corresponding frozen palette; all declared hexadecimal/font values match. Actual bundled helper use is present in all three traces. Reported unrounded contrast ratios independently recompute **18/18**, absolute tolerance 1e-9. Markdown rounded ratios also agree within that tolerance. The helper's `passed:true` is treated as input validity, not global contrast compliance or host-paint acceptance.
- Bundled `check_reports.py` ran on BOTH outputs after each final write/edit and returned inspected `passed:true`. Independent final-byte checks also pass: run 1 checks 31 official URLs / 6 history rows, run 2 checks 24 / 7, run 3 checks 29 / 7: **84 URL checks and 20 listed rows total**, no findings. This does not close the omitted-row failures above or validate the CSP instruction.
- Diagnostic recovery is preserved: run 2 first received `passed:false` for unknown `interface.surface.page.value`, listed tokens, corrected exact paths and obtained `passed:true`; run 3 diagnosed that path and then `interface.surface.default.value` before successful exact resolution. All were default diagnostic exit 0, with zero tool errors. Run 1 made a post-check JSON edit and checked both final files again.
- Read surface: all three read the prompt, SKILL, and only relevant bundled assistant matrix, capability offerings, Codex/Copilot limits, distribution, chat patterns, evidence/probing, usability/color and report-checker resources. Run 2 also read source-checker code. Helpers read their own bundled palette/catalog. No acceptance fixtures, repository docs, sibling skills, project evidence, network, new provider, installation or host/account/global action appears. Read-tool calls: 11/12/11; bash calls: 6/5/6. Full commands and helper diagnostics are in each independent record.

Observed usage totals: input 144,963; output 50,901; cache read 761,344; reported total 957,208 tokens. These are trace counters, not price estimates. Three isolated OpenAI-backed sessions were used; no Claude or Copilot model allowance was used by this cohort.

## Immutable artifact hashes

| Run | `offerings/recommendation.md` SHA-256 | `offerings/recommendation.json` SHA-256 |
| --- | --- | --- |
| 1 | `7ac90b4923c76a2d2039856c1a76426fb8770d7f10d49fc99893fd51503cea01` | `41407c86972f700481263097ae80128c68886fd024b59ece19d2c597e10d9e0f` |
| 2 | `ec61c4ec1a404b737881a95c06e2b1defcecec3b94a0fa30e720ebc1a7fc89e5` | `5402913e533800801cb43f6b5901689cd41cf5fdcf65d79ecb782268066673c4` |
| 3 | `9970a69f55c17771682f1da3ef8d4a5c7cdfa5efbe460cc500319c19ce2b5f84` | `3967e4b718c1f4a53cdcd4e504e512de22a0f2087af7e2a18344510ec1573c97` |

## Practical next guidance

For a future canonical update, build the historical-observation ledger before prose and give each reused empirical fact a matching result: include capability flags, access gates and lifecycle observations, not only headline positive/negative tests. Omit nonessential empirical detail when its version/layer cannot be recorded accurately. A checker can verify rows that exist; the author must separately reconcile claims with the ledger.

Add a small mechanism-specific CSP comparison: MCP Apps resource metadata versus ordinary extension webview HTML CSP/nonce/source directives. Keep desktop capture version unknown when it was not recorded, separate from current inventory. Give ordinary critical text and icon/accent separate color roles and backgrounds. These are recommendations from the retained failures; this frozen subject and these outputs were not changed or rerun.
