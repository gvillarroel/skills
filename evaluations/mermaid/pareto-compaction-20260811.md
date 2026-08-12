# Mermaid Capacity Pareto Evolution and Compaction — 2026-08-11/12

## Outcome

The Mermaid 11.16.0 skill now has a rendered maximum-capacity acceptance case for every public family that exposes finite indexed colors, configured color slots, semantic roles, or semantic classes. The promoted candidate also reduces the tracked skill bundle from 49 files to 18 by embedding the 31 acceptance sources in the fixture manifest without changing their bytes.

The final Harbor generation-6 gate promoted candidate `a-runtime-v6` with canonical digest `sha256:79835bdaacd4f425d500955c7833f0d76141f13e79e76307caa9f36b52985bd0`. Provenance was verified, the skill changed relative to baseline, and the promotion had no blockers or task regressions.

## Bundle compaction

- Baseline revision: `17f98e1e`.
- Acceptance fixture files: 49 tracked files before compaction, 18 after compaction; 31 files removed, a 63.3 percent reduction.
- The 31 removed `.mmd` files were embedded exactly in `assets/examples/mermaid-max-elements/manifest.json`; byte-for-byte parity was verified before deletion.
- `SKILL.md`: 60 physical lines / 5,082 bytes before compaction, 53 lines / 4,237 bytes after compaction; 845 bytes smaller.
- Final runtime profile: 15 files / 410,493 bytes, excluding `assets/examples/` and transient bytecode.

## Maximum-capacity contract

The corrected capacity model is:

- Mindmap: root plus 11 level-one branches, or 12 visible fills; the limit is not 14.
- Timeline, Radar, and Pie: 12 indexed items.
- Treemap: 12 named colored hierarchy nodes; a named wrapper root leaves 11 direct child-group slots.
- Kanban: 10 reachable colored columns, mapped to the lightened `cScale2` through `cScale11` rules.
- Journey: seven distinct reachable section classes plus an eighth boundary section that cycles to class zero.
- GitGraph: eight branches including main; Venn: eight sets; Sankey: eight configured node colors.
- XY: six extended plot colors and five standard plot colors; the sixth standard series proves cycling.
- Quadrant: four fixed domains; Cynefin and Event Modeling: five semantic roles each.
- Gantt: six visual task states rather than an invented task-count maximum.
- Every class-capable family except indexed Treemap: all nine semantic classes bound to distinct rendered geometry.

The final deterministic run used the pinned `@mermaid-js/mermaid-cli@11.16.0` and passed 31/31 families, 25 finite-capacity cases, 200 finite slots, 62/62 styled diagrams, 62/62 SVG renders, 11/11 cyclic render contracts, and zero findings. The semantic SVG gate requires each class role to bind to visible geometry with its expected fill and stroke; declaring unused classes is insufficient.

## Evaluation-guided repairs

Native Harbor 0.18.0 used `gpt-5.6-luna`, medium reasoning, no retries, rendered SVG/PNG verification, and nine all-or-nothing rewards: primary reward, routing, fidelity, metadata, render, palette, visible palette, counterfactual palette influence, and visual fidelity.

Earlier generations were deliberately not promoted when a sealed holdout exposed a defect:

- Generation 3 exposed ambiguous Sankey weights, an XY standard-palette oracle error, and Gantt combined-state ordering.
- Generation 4 exposed family-specific semantic-class grammar and over-narrow aspect contracts.
- Generation 5 reached 15/15 development but failed its holdout gate. ER rendered at aspect ratio 10.48, Swimlane palette coverage was only 0.9226 percent, and one State attempt hid required IDs behind aliases. The formal gate reported a task regression and did not promote the candidate.
- The generation-6 mutation adds compact nine-role defaults only when the user has not supplied family layout: ER uses `minEntityWidth: 180` and `rankSpacing: 20`; Swimlane uses Flowchart `nodeSpacing: 10` and `rankSpacing: 20`. It also states that State aliases replace visible IDs. Explicit user layout remains authoritative.

The repaired generation-5 cohort rerun passed 6/6 attempts with all rewards at 1.0. The full generation-6 development cohort then passed 18/18 versus 16/18 baseline, with zero agent, provider, or infrastructure failures in the formal analysis.

The fresh generation-6 holdout digest was `8c233d8fb1ff78b3de418570caf908e499760d9366b7c9911916e19466876bd9`. It was disjoint from all previous maximum-capacity profiles and covered Requirement Diagram's nine semantic classes, Quadrant's four domains, and Event Modeling's five roles. The candidate passed 6/6 versus 4/6 baseline, gained +0.333333 mean reward, and had zero task regressions. The population search verified both candidate and baseline provenance and returned `promoted: true` with no blockers.

## Infrastructure notes

- GEPA mutation was not available because the environment had no `OPENAI_API_KEY`, and Docker-based Harbor doctor checks could not run. A dry-run succeeded, then the evolution followed the documented manual population-search fallback with an immutable baseline and sealed holdouts.
- Windows Proactor TCP wakeup pairs intermittently stalled Harbor. Run-local Harbor commands used a UDP loopback wakeup-pair adapter; the task environment and verifier remained unchanged.
- Harbor completed and scored all generation-6 trials, but its optional post-run Codex trajectory conversion emitted a Windows `cp1252` Unicode decoding warning for some event logs. Trial artifacts, rewards, and the formal promotion analysis were intact.
- One deterministic render attempt used an invalid npm cache and failed before invoking `mmdc`. Its output was discarded. A fresh run with the real npm cache produced the clean 62/62 report recorded above.

## Isolated forward validation

Strict runtime-profile run `mermaid-maximum-capacity-20260812-spark-1` used `openai-codex/gpt-5.3-codex-spark` at medium thinking and passed the exact-output, valid-event, observed-model, zero-tool-error, clean-read-surface, and unchanged-payload gates. The isolated agent inferred 12 authored Mindmap elements, seven Journey palette slots plus the eighth cycling section, and 10 Kanban columns. Both styling checks reported `missingStyleCount: 0`.

The runtime payload contained 15 files / 410,493 bytes with SHA-256 `e3a8b69e8fbb86fef17bf101de02c7cb2df0fc2c3e10fbb7677c6cbeb065414f`. The trace read the prompt, `SKILL.md`, `references/palette-capacity.md`, and its own generated artifacts; it did not read acceptance examples, sibling skills, repository documentation, or network resources. An independent post-run render with pinned `@mermaid-js/mermaid-cli@11.16.0` produced all three SVGs and preserved every expected label, including `Mind branch 11`, `Journey slot 08`, and `Kanban slot 10`.

## Final repository gates

- Maximum-capacity fixture tests: 12/12 passed.
- Harbor dataset contract tests: 20/20 passed.
- Visual palette regression tests: 2/2 passed.
- Python compilation passed for the changed styler, fixture validator/tests, dataset builder/tests, and visual-palette tests.
- The Pages build completed with 401 generated files; pattern-ID validation passed 1,159 canonical IDs.
- Repository skill validation, skill-independence tests, payload validation, skill quick validation, and `git diff --check` passed.
- The repository-local installation matched all 18 canonical Mermaid skill files after synchronization.

## Durable and local evidence

- Versioned fixture and validator: `skills/mermaid/assets/examples/mermaid-max-elements/`.
- Dataset builder and tests: `evaluations/mermaid/build_harbor_dataset.py` and `evaluations/mermaid/test_max_capacity_dataset.py`.
- Final deterministic report: ignored local run `evaluations/runs/mermaid-pareto-evolution-20260811/final-fixture-render-v6b-report.json`.
- Development jobs: ignored local runs under `evaluations/runs/mermaid-pareto-evolution-20260811/direct-v6-jobs/`.
- Holdout jobs and population decision: ignored local runs under `evaluations/runs/mermaid-pareto-evolution-20260811/direct-v6b-jobs/` and `population-v6-analysis/`.
- Strict isolated run: ignored local run `evaluations/runs/mermaid-maximum-capacity-20260812-spark-1/`.

## Reproduction

```powershell
uv run --script skills/mermaid/assets/examples/mermaid-max-elements/scripts/test_max_elements.py
uv run --script evaluations/mermaid/test_max_capacity_dataset.py
uv run --script evaluations/mermaid/test_visual_palette.py
uv run --script skills/mermaid/assets/examples/mermaid-max-elements/scripts/validate_max_elements.py --work-dir <fresh-dir> --npm-cache <npm-cache> --render-attempts 3 --report <report.json>
uv run --script evaluations/mermaid/build_harbor_dataset.py <fresh-run-dir> --run-id <run-id> --profile max-capacity-v6-pareto --attempts 2
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/mermaid-maximum-capacity.md --model openai-codex/gpt-5.3-codex-spark --thinking medium --mode json --strict --run-id <run-id> --timeout-seconds 900 --expect-output deliverables/standard/mindmap.mmd --expect-output deliverables/standard/journey.mmd --expect-output deliverables/extended/kanban.mmd --expect-output deliverables/capacities.json --expect-output deliverables/style-standard-report.json --expect-output deliverables/style-standard-check.json --expect-output deliverables/style-extended-report.json --expect-output deliverables/style-extended-check.json
```
