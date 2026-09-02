# Diagram Design Adoption Study — 2026-08-13

## Source and scope

- Source: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design), commit `f3622cf66a3c557cb2ead57b687a3c1ff63f5a2b` dated 2026-08-12.
- License: MIT.
- Reviewed surfaces: `SKILL.md`, semantic patterns, output adaptation, animation, styling, accessibility, import guidance, type references, self-check and repository validators, and the local 39-entry gallery navigation containing the 27 core visual types plus variants and import/motion examples.
- Visual evidence: browser snapshots and disposable screenshots of Architecture, Loop, paired policy traces, the explicit static motion state, and a Mermaid import were inspected locally. The only gallery console error was a missing `favicon.ico`.

## Transferable findings

1. **Select behavior before layout.** Capacity, enforcement, trust, policy divergence, and residual risk need semantic primitives and budgets independent of the layout family.
2. **Treat density as a contract.** An overview needs a bounded concept/relationship count, a stable reduction order, and an overview/detail escape instead of smaller text.
3. **Make reduction auditable.** Destination, detail, and audience are independent decisions. Any semantic reduction needs a kept/merged/omitted/moved-to-detail ledger.
4. **Require useful accessible names without overclaiming.** The root figure needs a short subject title and a content-oriented description; geometry narration is not a substitute for meaning. This metadata gate does not make every diagram relationship structurally navigable to assistive technology.
5. **Keep static meaning complete.** Motion may explain order but cannot create states, counts, labels, or outcomes absent from the settled frame.
6. **Validate edge traceability after rendering.** Automatic layout is not proof that important routes, labels, and endpoints are readable.
7. **Prefer semantic design roles over raw colors.** A focal role and a bounded accent budget teach more than copying a large palette.

## Adoption decisions

| Owner | Decision | Applied change |
| --- | --- | --- |
| `mermaid` | Adopt | Added behavior-first editorial contracts, overview budgets, independent destination/detail/audience dials, fidelity-ledger rules, and rendered edge-traceability review. A separate compact reference covers accessible title/description metadata. The styler reports `accTitle`/`accDescr` coverage; both the source checker and SVG renderer expose an opt-in `--require-accessibility` gate, and the renderer resolves the final `<title>`/`<desc>` ARIA references. |
| `scene-composition-director` | Adopt | Added a progressive content-budget/fidelity reference, explicit `contentBudget` and `contentAccounting` handoff fields, and an opt-in `--require-content-accounting` validator gate. The gate derives node/edge/focal counts from enumerated draw items; bounds typed annotations and total visible content; maps every visible kept or merged item to that basis; proves exhaustive dispositions; cross-validates CLI, global, and local anchors; rejects moved content that remains in visible-bearing fields; and requires exact scene targets or registered external targets. |
| `compose-synchronized-svg` | Do not duplicate | Existing compiler, relationship routing, port/lane separation, label plaques, root/module accessibility, script-free fallback, reduced motion, and browser audit are already stricter than the transferable source rules. |
| `d3` | Do not duplicate in this pass | Existing composition, replication, contract, and evaluation guidance already owns general D3/SVG visual review. The worktree also contains a separate active D3 evolution, so an overlapping rewrite would be unsafe and low-value. |
| `plantuml-colorset-renderer` | Do not adopt | It is primarily a semantics-preserving renderer. Manual connector routing and editorial element deletion would conflict with PlantUML layout and source-preservation guarantees. |
| Repository colorsets | Keep local contract | Website-derived arbitrary brand onboarding was not transplanted because this repository deliberately standardizes visual skills on colorset1 and explicit colorset2 expansion. The reusable lesson—semantic roles and restrained focal emphasis—was adopted without replacing those palettes. |
| Upstream templates and icon catalog | Do not copy | The existing Mermaid, D3, PlantUML, procedural SVG, and synchronized SVG skills already cover the renderer/type surface. Copying 95 HTML examples or the large icon reference would add duplicate payload rather than transferable instruction. |

## Implemented validation coverage

- `evaluations/mermaid/test_editorial_accessibility.py`: 8/8 tests cover source metadata reporting plus rendered SVG root type, unique IDs, and resolved ARIA references.
- `evaluations/mermaid/test_editorial_queue_verifier.py`: 9/9 tests prove that the case verifier rejects wrong visible labels, explicit or implicit invented nodes, duplicate, chained, or alternate-form relations, facts attached to the wrong relation, and missing or misclassified fidelity-ledger rows while accepting repeated identical Mermaid declarations and both standard Markdown table styles.
- `evaluations/scene-composition-director/test_content_accounting.py`: 26/26 tests cover exhaustive partitions, bounded annotation laundering, conservative entity-noun rejection, derived count bases, prefix/postfix and unit-first numeric claims plus relation synonyms, content-free non-diagram scenes, Unicode- and symbol-safe exact moved-content checks across text-policy fields, bidirectional anchors, exact arbitrary scene IDs, forward-only moves, repeated-ledger reconciliation, and exact registered external deliveries.
- Local Mermaid integration: the final nine-node/eight-relation finite-capacity queue passed colorset write/check with `missingAccessibilityCount: 0`; the renderer accepted a real Mermaid 11.16.0 SVG with unique resolved metadata; the semantic verifier reported `"ok": true`; and browser inspection confirmed readable fan-in, capacity, throughput, Approved, and Deferred routes with no moved secondary detail.
- Strict isolated Mermaid run `mermaid-editorial-accessibility-20260813-spark-5` passed exact outputs, required JSON fields, literal prompt commands, the explicit read allowlist, Spark model, valid events, zero tool errors, clean runtime read surface, and unchanged payload. The independent post-run semantic verifier passed the exact labels, nine nodes, eight required relations, fact-to-edge bindings, 12-row ledger, and gates against implicit nodes, duplicates, chains, alternate links, and invented topology.
- Strict isolated scene run `scene-composition-content-accounting-20260813-spark-9` passed the exact plan path, literal validator command, Spark model, valid events, zero tool errors, clean runtime read surface, unchanged current payload, derived visible-content limits, internally consistent operator-aware count claims, exhaustive ledgers, and exact forward Audit preservation.
- The prior superficially passing Mermaid and scene artifacts were retained only as ignored run evidence and now fail the new semantic/contract validators for the intended reasons. This guards against validating style or file existence while missing source fidelity.
- An independent adversarial review drove four hardening rounds, then returned clean after all ten final mutations covering implicit or duplicate Mermaid relations, misplaced edge facts, Unicode/symbol moved-content matching, omitted text-policy fields, and alternate numeric phrasing were rejected or accepted as intended.
- The post-review maximum-capacity suite remains green: 31 families, 25 finite cases, 200 finite slots, 62 styled diagrams, 62 Mermaid 11.16.0 renders, and zero findings.

## Validation commands

```powershell
uv run --script evaluations/mermaid/test_editorial_accessibility.py
uv run --script evaluations/mermaid/test_editorial_queue_verifier.py
uv run --script evaluations/scene-composition-director/test_content_accounting.py
uv run --script evaluations/mermaid/verify_editorial_queue.py --source evaluations/runs/mermaid-editorial-accessibility-20260813-spark-5/workspace/deliverables/review-queue/queue.mmd --ledger evaluations/runs/mermaid-editorial-accessibility-20260813-spark-5/workspace/deliverables/review-queue/fidelity-ledger.md
uv run --script skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan evaluations/runs/scene-composition-content-accounting-20260813-spark-9/workspace/projects/review-queue-composition/composition-plan.json --expect-scenes 2 --require-anchor "Gateway" --require-anchor "Audit stream" --require-anchor "capacity 2" --require-anchor "1 item per hour" --require-content-accounting
python -m py_compile skills/mermaid/scripts/style_mermaid_directory.py skills/mermaid/scripts/animate_mermaid_svg.py skills/scene-composition-director/scripts/validate_scene_composition_plan.py evaluations/mermaid/verify_editorial_queue.py
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/mermaid-editorial-accessibility-20260813-spark-5/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/scene-composition-content-accounting-20260813-spark-9/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

Final repository, independence, payload, and diff outcomes are recorded in `SKILLS.md` after completion.
