# Agent micro decisions — 2026-11-12

User review rejected the broad application's permanent navigation and repeated
summaries for an agent decision, and the unstyled terminal's weak visual
hierarchy. The corrected default is one pending human question, only
decision-relevant context/evidence, and a typed answer returned to the agent.
The earlier complex workbench remains a capacity stress fixture. See the
[run guide](../../docs/plugin-ui-micro-decisions.md) and
[source hashes and receipts](micro-decisions-20261112.json).

## Corrected interaction

The synthetic question asks whether Ontology alignment belongs under Knowledge
modeling or Data integration. Each option presents a local tree with the
disputed term and a relevant sibling. The parent heading labels the root once.
The definition and short reasons distinguish the classifications; optional
scope evidence can change the choice. No directory, global tabs, fleet counters,
settings or unrelated branch navigation remains. One selected placement or an
explicit deferral completes the interaction.

The Pi version uses native theme roles: accent for the active option, warning
for the unresolved concept, success for a selected receipt and muted/dim for
supporting context. Bold text, circles, checks, whitespace, separators and tree
connectors also carry meaning. Deferral stays neutral. A bounded E disclosure
shows relevant evidence and returns to the same question. Both alternatives
and decision keys fit 60x16 terminal cells with host rows reserved.

## Final checks

| Layer | Result | Scope |
| --- | --- | --- |
| Edge/browser/domain/MCP/App SDK | 25/25 | 780/542/390/320px, physical chart-label readability, one question/two options/no global navigation, selected/deferral outcomes, stale and duplicate answers, strict sandbox, actual server receipt, controlled-host context update then one continuation acknowledgement, reopen and absent-capability fallback. |
| Installed Pi 1.4.0 | 8/8 | Real ConPTY TUI, 80x32/60x16, distinct selected/unresolved/success colors, keyboard choice, relevant evidence, returned placement, Escape deferral and normal exit without a model turn. |
| Desktop-bundled Codex 0.167.0-alpha.3.2 | 10/10 | Isolated portable marketplace installation, cache-byte equality, actual app-server discovery and direct choice-opening tool without a model turn. |
| Current app integrated browser | Observed | Actual 542x767 undecided/selected/recorded comparison; one heading, two alternatives and zero global navigation. The corrected example is kept open. |
| Skill-only contract forwards | 7/7 strict | One case per comparison/host bundle, exact outputs, requested model, clean read surface, valid events, zero tool errors and unchanged copied payloads. |

The real SDK test records through the actual MCP server. It distinguishes a
future context update from a continuation request and sends exactly one message
only when the controlled host advertises text messages. This proves the bridge
contract with that fixture, not a stock host live model continuation. The
standalone IAB example says that it records locally. The native Pi demonstration
puts the answer into model-visible history with `triggerTurn:false`.

The result contains question identity/revision, selected option or deferral and
request/receipt identity. It does not edit a taxonomy. A stale question or a
different second answer is rejected; reopening restores the recorded receipt.
Missing host capabilities give a direct chat fallback instead of pretending
that the agent resumed.

## Standalone skill validation

The seven bundles now start with their own `references/micro-decisions.md`.
The reference explains the relevance gate, comparable local taxonomic graphs,
typed return lifecycle, semantic native styling and host-specific mechanisms.
Entry prompts align with that default. Pi also ships the tested self-contained
`assets/templates/pi-command/micro-choice.ts`; its bytes match the native source
used for the actual terminal trial.

Each `<skill>` uses:

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/micro-ui-<skill>-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output micro-plan.json --expect-output review.md --run-id 20261112-micro-ui-<skill>-sol-1 --timeout-seconds 360
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261112-micro-ui-<skill>-sol-1/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

The model exception reuses the earlier account-specific Spark rejection.
Independent checks verified all six requested JSON fields and reviews below
400 words. Manual review checked the relevance justification for visible
elements, one-decision scope, selected/deferred answers, host mechanism, native
color semantics, and receipt/continuation boundaries. These are one-repetition
contract cases, not a generalization rate. All seven skills remain `validating`
where actual host/deployment gates remain open. No preceding cohort is pooled.

One failed native trial is retained. The selected label wrapped Data and
integration onto separate terminal rows; an evaluator substring assertion
missed it. A whitespace-aware assertion fixed the evaluator; the native output
was visually correct. Final 8/8 verification uses that corrected check.

## Publication and limits

No new personal Claude server was configured. Claude Code login/Desktop Code
onboarding and Gemini registration gates remain. The current app IAB is in
Codex mode and is separate from stock ChatGPT inline App acceptance. No cloud
settings or account permissions changed. All screenshots and raw host data stay
under ignored project artifacts; only the compact inventory is versioned.

The main publication uses an isolated checkout to preserve unrelated local
semantic-skill edits. The latter leave four authoring-route findings in the user
worktree; the clean publication passed pattern IDs (1,348), full structural validation,
independence, payload and a frozen 8-skill/16-bundle source/runtime/full audit.
Scoped local installation verification matches all 164 source files; other
installed skills were preserved. The first ignored-artifact source exposed zero
Git-visible files and is not counted as a sync; a corrected source outside the
helper checkout copied 36 changed files and passed exact comparison.
