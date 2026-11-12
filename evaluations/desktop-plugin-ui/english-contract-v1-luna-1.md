# Desktop plugin UI authored-language contract smoke

Date: 2026-10-25. Case type: **contract smoke**, one isolated forward run. This is a narrow validation of the authored-language rule; it is not a naturalistic repetition cohort or an actual UI acceptance test.

The [prompt](../pi-prompts/desktop-plugin-ui-english-contract.md) instructs the agent to discover and apply the supplied skill's authored-language rule without stating the target language. It supplies four legacy display strings as source fixtures, requests fourteen concrete component/content categories, and requires exact technical identifiers and an honest host-locale boundary.

The frozen runtime bundle contains 19 files with payload SHA256 `565602a9d166c18e15f07dce0a47c2a8587089085159572ca0094084886471ba`. Prompt SHA256 is `e85274ad991972fc26b1d26ec37955fd6e77634f0da7377a9a4535b9d7011b69` (2780 source bytes). The documented model exception selected `openai-codex/gpt-5.6-luna` instead of Spark, with high thinking, JSON strict mode, and a 600-second timeout.

## Result and retained evidence

The [single raw run](../runs/20261025-desktop-ui-english-contract-v1-luna-1/) passed in **40.604 seconds**. Strict harness: **pass**. Independent report checker: **pass**. Manual copy/language review: **pass**. Joint contract outcome: **pass, 1/1**. Failure classification: **none observed in this case**. No retry, favorable reroll, reviewer output edit, or bundle mutation occurred.

The exact generated outputs are:

- [audit/language-contract.md](../runs/20261025-desktop-ui-english-contract-v1-luna-1/workspace/audit/language-contract.md), SHA256 `64e66953b978b531b95edf6efcf32c0ba221fb042159bad648b67f16b3002d3b`.
- [audit/language-contract.json](../runs/20261025-desktop-ui-english-contract-v1-luna-1/workspace/audit/language-contract.json), SHA256 `53e8555a0b9ab485e012284ee13bcac524f0b55d6eb59e84ca9c11090a5e6aab`.

The raw folder retains the manifest, full events, strict harness checks, `read-surface.json`, and evaluator-created `independent-language-check.json`. Earlier design/cross-assistant failures remain separate and unchanged.

## Independent content inspection

Both artifacts identify **English** as the authored language. The Markdown table and JSON contain concrete component labels and display content for all fourteen requested categories:

| Category | Manual outcome |
| --- | --- |
| Title/navigation | English heading and navigation copy |
| Button | English save action |
| Input label and placeholder | English search label and placeholder |
| Pending/success status | English saving and saved text |
| Error and validation message | English failure/recovery and required-input instruction; diagnostic code remains secondary |
| Empty state | English no-match guidance |
| Contextual help | English ticket-search instruction |
| Accessibility label and live announcement | Concrete English accessible name and update announcement |
| Tooltip | English action help |
| Notification | English saved confirmation |
| Chart title/category/axis label | Concrete English title, category and count-axis wording |
| Sample ticket content | English ticket subject with stable ticket ID |
| Host-native terminal confirmation | English authored prompt wording, conditional on host support |
| Plain text fallback | English result with stable ticket ID |

All four raw legacy fixture strings are absent from both final artifacts. `TICKET-7`, `E409`, and `ui/initialize` retain their exact spelling in both. The ticket ID appears in sample content and fallback; the error code accompanies a human explanation; the protocol method appears only in clearly identified technical notes/identifier records. This preserves machine-facing values without leaving legacy display text untranslated.

The host-locale explanation limits the contract to plugin-authored copy. It explicitly leaves host chrome, permission dialogs, native presentation, terminal, OS and account locale under host control. Proposed native prompt wording applies only where the host allows authored text. Neither artifact claims that an account/OS locale changed or that host controls were restyled. `host_acceptance_verified` and `task_empirical_tests_performed` are literally false.

English language was judged by reading the generated component labels, display strings and explanatory prose. Fixture absence, field coverage and identifier preservation were also checked deterministically. The report checker found no source/evidence-format findings; there were **zero official URL occurrences** and zero historical rows in these artifacts, so that checker result is not evidence of source attribution or a language classifier result.

## Trace and isolation

The event summary observes only `gpt-5.6-luna` through `openai-codex`, with zero invalid JSON and zero tool errors. The six tool calls comprise three reads, two writes, and one local checker execution. The exact read surface is:

1. `../prompt.md` first;
2. `skills/desktop-plugin-ui/SKILL.md` immediately afterward;
3. `skills/desktop-plugin-ui/scripts/check_reports.py`.

The entry point alone supplied the necessary language rule. The run reads no fixture/gallery, sibling skill, repository document, project evidence or account material. It runs the bundled checker after both artifacts exist and inspects a successful result. Strict checks verify the exact paths, required fields and unchanged frozen payload. No network, provider tool, external application, installation, locale change or prototype rendering occurs in the trace.

## Commands

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-english-contract.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261025-desktop-ui-english-contract-v1-luna-1 --expect-output audit/language-contract.md --expect-output audit/language-contract.json --expect-output-json-field audit/language-contract.json::language=English --expect-output-json-field audit/language-contract.json::host_acceptance_verified=false --expect-output-json-field audit/language-contract.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-english-contract-v1-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261025-desktop-ui-english-contract-v1-luna-1/read-surface.json
uv run --script evaluations/runs/20261025-desktop-ui-english-contract-v1-luna-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-english-contract-v1-luna-1/workspace/audit/language-contract.md evaluations/runs/20261025-desktop-ui-english-contract-v1-luna-1/workspace/audit/language-contract.json --fail-on-findings
```

The first command documents the completed attempt; do not reuse its run ID for a new attempt. The deterministic checks do not modify the generated artifacts.

This result shows that the frozen bundle can produce the requested English copy contract from legacy source strings. It does not verify a rendered component, accessible-name exposure in an actual host, every dynamic runtime state, host-native localization, a user study, or current host acceptance. The skill's overall `validating` status and retained broader failures are unaffected.
