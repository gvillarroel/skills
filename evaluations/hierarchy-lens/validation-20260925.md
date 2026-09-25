# Hierarchy Lens validation — 2026-09-25

The released runtime builds a self-contained interactive radial SVG map inside HTML. Node positions are independent of categorical or numeric color lenses. Branch focus, search, explicit missing values, observed additive sums, fixed global domains, keyboard access, mobile labels, and SVG/PNG snapshots are bundled. The acceptance organization contains 1200 fictional people across seven reporting levels.

## Final result

All final release gates pass. The runtime contains nine files, excluding acceptance examples, with payload SHA-256 `d4681d68f97a086ba6744ece645a3e211b4922c12310bb8cea5df0651a3e5f9e`.

| Gate | Result |
| --- | --- |
| Deterministic semantics and invalid-input suite | 13 tests pass, including subcases for malformed trees, numeric boundaries, exact demo sizes, null/zero distinctions, and escaped HTML-closing text. |
| 1200-record offline Chromium audit | 43 checks pass; actual lens changes, branch navigation, fixed geometry/domains, search, keyboard, category highlighting, ring controls, real SVG/PNG downloads, mobile sizing, no external requests, and no browser errors. |
| 5000-record scale audit | All checks pass; the complete multi-state audit takes 5.77 seconds on this host. This is whole-audit time, not a single-frame rendering claim. |
| Singleton boundary | Browser audit passes for one node, absent categorical/numeric data, a nonadditive metric, and a literal script-looking label that remains inert text. |
| Strict command contract | Final cohort 1/1 passes with five exact outputs. |
| Strict naturalistic organization case | Final cohort 3/3 passes with exact 430-record inputs and five exact outputs each. |
| Strict portfolio generalization | Final cohort 3/3 passes. The independent oracle verifies eight preserved IDs, root sum 950 over seven observed records, Materials 500/3, Ecology 425/3, and unchanged missing/zero observations. |
| Invalid-source boundary | 1/1 passes; the agent declines to fabricate a tree from cyclic/multiple-parent reporting lines or add overlapping team totals. |
| Unforced metadata routing | 6/6 correct across organization, portfolio, taxonomy, line-chart, general-graph, and logo requests. No skill was forced into this run. |
| Independent artifact gates | Source-preservation oracle and evaluator-side Chromium reruns pass for all seven final visual runs. |
| Repository and publication build | Quick validation, pattern IDs, repository structure, independence, payload, Pi harness (14 tests), Pages output boundary (3 tests), Pages build, 14-entry catalog format, and built-page browser audit pass. |

The default Spark attempt was rejected by the provider before its first tool call because the ChatGPT account does not support `gpt-5.3-codex-spark`. The explicit model exception is `openai-codex/gpt-5.6-luna`, also recorded in SKILLS.md. All eight final forced-skill runs use strict JSON mode, observe the requested Luna model, preserve the copied payload, produce all exact outputs, have valid event JSON and zero tool errors, and keep reads confined to the prompt, entry point, needed compact references, and generated artifacts. No final runtime run reads acceptance examples, sibling skills, or repository context.

## Retained failures and correction

The original command contract passed. The original naturalistic cohort passed only 1/3 strict runs: two agents hand-authored a synthetic team-size formula and failed a count assertion before recovering and producing valid maps. These are retained as agent execution failures; recovery does not erase a strict tool error. The skill entry point now explicitly routes fictional organizations with a requested headcount through `--demo --demo-size N`, reserving custom structure construction for an actual custom-structure requirement. The final contract and complete fresh naturalistic/generalization cohorts evaluate that revised payload.

An initial local browser check found no matching Chromium installation. Installing the declared Playwright browser into ignored project artifacts resolved that infrastructure failure. The initial Pages build also exposed a missing explicit copy step for the new catalog entry; adding that step fixed the build. Neither initial failure is presented as a pass.

Machine-readable trial identities, failures, hashes, read paths, independent artifact results, and cohort counts are preserved in [validation-20260925.json](validation-20260925.json). Raw evidence remains under `evaluations/runs/hierarchy-lens-*20260925*`; local screenshots, built maps, browser cache, independent audits, and publication evidence remain under `projects/hierarchy-lens/artifacts/`.

## Reproduction

```powershell
uv run --script skills/hierarchy-lens/scripts/test_explorer.py
uv run --script skills/hierarchy-lens/scripts/build_explorer.py --demo --output projects/hierarchy-lens/artifacts/html/organization-atlas.html --data-output projects/hierarchy-lens/artifacts/data/organization.json --report projects/hierarchy-lens/artifacts/reviews/build.json
uv run --script skills/hierarchy-lens/scripts/audit_explorer.py projects/hierarchy-lens/artifacts/html/organization-atlas.html --report projects/hierarchy-lens/artifacts/reviews/browser-audit.json --screenshot projects/hierarchy-lens/artifacts/screenshots/overview.png
uv run --script scripts/run-pi-skill-eval.py hierarchy-lens --prompt-file evaluations/pi-prompts/hierarchy-lens-naturalistic.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id hierarchy-lens-naturalistic-FRESH-ID --expect-output deliverables/organization.html --expect-output deliverables/organization.json --expect-output deliverables/build.json --expect-output deliverables/audit.json --expect-output deliverables/overview.png --expect-output-json-field deliverables/build.json::nodes=430 --expect-output-json-field deliverables/audit.json::ok=true
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/RUN-ID/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script evaluations/contracts/check-hierarchy-lens.py SOURCE.json EXPLORER.html --portfolio
uv run --script projects/hierarchy-lens/scripts/collect_evidence.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/sync-local-skills.py --source skills/hierarchy-lens --destination .agents/skills/hierarchy-lens --check
```

The browser commands require a compatible installed Chromium or `PLAYWRIGHT_BROWSERS_PATH` pointing to one. This host uses `projects/hierarchy-lens/artifacts/browser-cache`. Use a fresh run ID for each repetition. Contract, boundary, generalization, and routing prompts are adjacent to the naturalistic prompt in `evaluations/pi-prompts/`. The collector rechecks retained runs and records their evidence; it does not create new model trials.

## Pattern and practical limits

The reusable recipe is [radial-lenses.md](../../skills/hierarchy-lens/references/radial-lenses.md), canonical pattern ID `hierarchy-radial-lenses`, example-set ID `hierarchy-lens`. The source example, catalog entry, and generated Pages metadata share those identities. The [public example](https://gvillarroel.github.io/skills/examples/hierarchy-lens/#hierarchy-radial-lenses) is discoverable from the main examples catalog. Live deployment evidence belongs to the GitHub Pages workflow for the publication commit.

Visual inspection covered the overview, focused branch, numeric scope, mobile state, and the research-portfolio generalization. Dense outer marks are intentionally explored through search or branch focus. The default overview limits visible depth and reports deeper records; users can select more rings. Each categorical lens supports eight explicit categories, the tree requires one primary parent, and numeric subtree sums require exclusive individual observations. The 20000-record input cap is a validation bound, not a performance promise. Static exports retain the current legend and context; the HTML retains interaction.
