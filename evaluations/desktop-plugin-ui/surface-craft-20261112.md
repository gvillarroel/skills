# Surface-specific craft implementation - 2026-11-12

Implemented the Impeccable-informed craft rules at the actual presentation
authority of eight independent bundles: the comparison router, six assistant
host skills and embedded Reflex XY. The [implementation map](../../docs/plugin-ui-surface-craft.md)
and [machine-readable evidence](surface-craft-20261112.json) record the scope.

## Implementation

Each bundle owns a compact `references/craft-by-surface.md` (2.1–3.3 KB), linked
directly from `SKILL.md`. The seven micro-decision references also route to the
matching profile. XY's existing interaction recipe now distinguishes a requested
chart/export from an agent decision and preserves its semantic data palette.
No sibling skill, new style package or global context-file system is required.

- Owned HTML/MCP Apps: relative reading roles, scoped CSS, meaningful grouping,
  distinct subject/selection/action/status, real keyboard focus and bridge-bound
  completion. The Claude Chat CSS example preserves the inherited font family.
- Native Claude Code: verified constructors, native layout/theme authority,
  authentic command/mount events and separate frontend paint checks.
- Pi: semantic theme roles, ANSI-aware terminal geometry, short-terminal
  reachability, evidence/choice completion, and distinct TUI/RPC/print routes.
- Codex: CLI/form, actual App renderer, owned app-server client and integrated
  browser are selected and validated independently.
- Gemini Enterprise: accepted A2UI catalog properties and typed A2A actions;
  unsupported graphics become equivalent catalog text/list/table controls.
- XY: public API or connected schema controls the chart; scoped HTML controls
  the wrapper. Color used for a data series is not replaced merely to reserve
  an action accent. Values, scales, gaps and category identities are preserved.

The profiles require the same decision and evidence across representational
fallbacks. A requested plot/export can remain a plot/export without introducing
an unnecessary human-choice flow.

## Isolated forwards

Final candidates passed **8/8** strict contract runs, one per bundle, with exact
`surface-contract.json`; XY also produced exact `request.json`. Independent
review confirmed five requested JSON keys and 675–857 words, the actual styling
owner, allowed mechanisms, host boundaries, same-information fallbacks and honest
planned/unexecuted checks. Read-surface summaries passed the requested model,
valid event JSON and zero tool errors; copied skill payloads remained unchanged.

For each `<skill>`:

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/surface-craft-<skill>-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output surface-contract.json --run-id 20261112-surface-craft-<skill>-sol-1 --timeout-seconds 360
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261112-surface-craft-<skill>-sol-1/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

Use `sol-2` for the final `desktop-chat-plugin-ui` candidate. Add
`--expect-output request.json` for `reflex-xy`. The explicit Sol/medium exception
follows the earlier recorded Spark account rejection. The earlier Claude Chat
run also passed strict mode but predates the inherited-font refinement; it is
retained and not counted as a second final-candidate repetition. These contracts
do not constitute a generalization rate or signed-in host-paint certification.

## Deterministic and live renderer checks

The eight selected bundles pass structural validation. The existing A2UI checker
passes 12 tests and both starter streams pass its bounded closed-tree profile;
those checks do not validate the full catalog or registered host. The existing
connected XY checker passes 4 tests. The independently generated XY request
passes that checker and preserves the exact supplied observations.

The actual connected `xy_render_chart` tool rendered the generated request:
colorset1, two lines, CSS dimensions 800x420, and native PNG 1600x840 plus SVG.
Visual inspection confirms observations 110/140/190 ms, a separate dashed
150 ms objective, explicit hour/ms axes and an unobstructed lower-right legend.
The primary red remains a data encoding. This is real renderer/export evidence;
it does not establish new stock-host UI paint or a live Python callback.

Relevant commands:

```powershell
uv run --script skills/gemini-enterprise-ui/scripts/test_check_a2ui.py
python skills/gemini-enterprise-ui/scripts/check_a2ui.py skills/gemini-enterprise-ui/assets/templates/status-panel.json
python skills/gemini-enterprise-ui/scripts/check_a2ui.py skills/gemini-enterprise-ui/assets/templates/chart-and-table.json
uv run --script skills/reflex-xy/scripts/test_connected_spec.py
python skills/reflex-xy/scripts/check_connected_spec.py --spec evaluations/runs/20261112-surface-craft-reflex-xy-sol-1/workspace/request.json --report projects/plugin-ui-surface-craft/artifacts/xy-spec-review.json
```

All eight skills remain `validating` where actual host/account/deployment gates
are still open. No personal plugin configuration, account access or cloud setting
changed. Raw runs, temporary render URLs, PNG/SVG exports and source snapshots
remain outside Git under the prescribed artifact directories.

## Repository and installation gates

The clean current-main checkout passes pattern IDs (1,348), full skill
validation, independence, payload and the explicit diff whitespace check.
Frozen source/runtime/full authoring checks pass for 8 skills and 16 copied
bundles. Scoped installation updated 24 source-owned files and matches all
172 canonical source files, preserving other installed skills. The user
worktree retains four unrelated semantic-skill authoring-route findings; its
pattern, independence and payload checks pass. Those unrelated edits are not
part of this publication.
