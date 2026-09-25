# Hierarchy Lens composition decisions — 2026-09-25

The new `--view decision` mode chooses both the next eligible record and the vacant cell it occupies. Explicit categorical or numeric priorities determine entry order. Weighted parent proximity, attribute affinity, occupied-neighbor contact, and radial compactness determine placement. Every placement is connected and preserves a hole-free body. The shared deterministic engine runs in Node during building and directly in the offline HTML when the user changes the policy.

The 1200-record example remains a 128 × 128 native image with four pixels per record. It now exposes actual placement replay, exact prefix scrubbing, individual steps, editable rules, score contributions, alternative vacancies, and a JSON decision-log download. Color lenses preserve the active geometry and replay progress. PNG/SVG export the visible prefix; SVG retains complete decision context.

## Release evidence

The final runtime contains 20 files, excluding examples, with SHA-256 `a18165d1150289a98fc9f146f412935f5b9034315d9fa96b3170d9e5d7b605f2`. The final model cohort and its command-contract retry all use this same payload unchanged. The local installation matches 26 canonical files, including six example resources.

| Gate | Result |
| --- | --- |
| Deterministic tests | 21 existing explorer tests and 11 decision tests pass. |
| Independent spatial oracle | The small exact fixture reconstructs every admissible vacancy and verifies that the chosen score is maximal. Larger tests independently reconstruct eligibility, priority, score terms, and connected hole-free prefixes. |
| Data-driven policy controls | Reversing category priority changes both order and geometry; changing affinity also changes actual positions. Repeated identical inputs reproduce the same layout. |
| Main 1200-record example | 54 pixel checks and 20 decision checks pass, including real playback, policy edits, future-record lookup, partial SVG export, JSON trace download, and restore. |
| Scale and numeric policy | The 5000-record example and 430-record descending-token example each pass the same 74 checks. The interactive engine's cap is 5000, distinct from the geometric organic mode's 20000-record cap. |
| Prior views | Preserved organic, radial pixel, and analytical examples pass 54, 44, and 43 checks respectively. |
| Final command contract | One fresh passing strict run after retaining two prompt-fence harness failures. The retry uses the unchanged final payload. |
| Final naturalistic cohort | 3/3 strict passes for 430 people, descending individual token priority, generation eligibility, role affinity, and four pixels per record. |
| Final generalization cohort | 3/3 strict passes for the eight-project portfolio, descending token priority, parent-ready eligibility, explicit spatial weights, and exactly one pixel per record. |
| Final boundary | 1/1 strict pass on an invalid tree and overlapping team totals. |
| Unforced routing | 11/11 correct, including decision composition and rejection of unrelated job ranking and game sprites. |
| Independent artifact validation | Source preservation, arithmetic, requested-policy checks, and evaluator-side browser reruns pass for passing visual trials. |
| Repository and Pages | Metadata, pattern IDs, structure, independence, payload, 14 harness tests, three Pages boundary tests, and 14-entry catalog checks pass. Pages builds 646 files. All four view routes and legacy hash transitions work. |

The recorded model exception remains `openai-codex/gpt-5.6-luna`, following the earlier Spark provider rejection before its first tool call. This release does not claim a new Spark pass. Strict mode checks the observed Luna model, JSON events, zero tool errors, exact output paths, confined read surface, and immutable copied payload. All final successful runs satisfy these checks.

Machine-readable results, every attempt, run identities, payload hashes, read surfaces, independent oracles, and failure classifications are in [decisions-20260925.json](decisions-20260925.json). Raw evidence remains under `evaluations/runs/hierarchy-decisions-*20260925-luna-*`. The final cohort uses `v2` in its run IDs; the successful command retry uses `v2-retry`.

## Retained initial failures and simplification

The initial cohort passes naturalistic 2/3, generalization 1/3, and boundary 1/1. Its command case fails only the exact-command gate. These attempts remain separate from the final release evidence.

- **Agent:** Initial naturalistic trial 3 retained the demo's role policy despite the requested descending-token policy. Initial generalization trials 1 and 2 omitted `--cell-pixels 1`, producing four pixels per record instead of one. Generalization trial 2 also attempted identical input/data-output paths, recovered, and remained a strict failure because of the tool error.
- **Skill workflow simplification:** Added direct CLI overrides for priority, direction/category order, affinity, eligibility, four spatial weights, and growth allowance. These update the embedded policy and optional source export together. The compact reference now gives distinct numeric-demo and one-pixel custom-input commands, explicitly maps side length to area, avoids redundant source rewriting, and requires matching the build report to the user's request. The engine's placement algorithm was unchanged.
- **Harness:** The exact-command scanner accepts only empty, `bash`, `sh`, and `shell` fences. The initial `text` fence and first attempted `powershell` correction both yielded `no-fenced-command-in-prompt`, although the agents executed the exact command and passed artifact/JSON gates. After inspecting the parser, changed the prompt to `shell` and ran a fresh successful retry. Neither rejected attempt is silently promoted.
- **Visual polish:** Before freezing the final runtime, increased CSS selector specificity for rule weights so labels and numeric values occupy separate columns, and improved table spacing. Inspected the final rules panel in-browser.

Final-cohort model traces read only the prompt, skill entrypoint, focused input/decision/validation references when needed, and generated artifacts; one also reads the compact organic reference. They do not read acceptance fixtures, sibling skills, project context, or external services. An initial generalization trial additionally inspected the builder source. The simplified final recipe removes that need: no final trial reads script or template source. Runtime engine assets execute through the bundled builder rather than being copied as instructions into model context.

## Reproduction

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = 'C:/Users/villa/dev/skills/projects/hierarchy-lens/artifacts/browser-cache'
uv run --script skills/hierarchy-lens/scripts/test_explorer.py
uv run --script skills/hierarchy-lens/scripts/test_decisions.py
uv run --script projects/hierarchy-lens/scripts/build_pixel_example.py
uv run --script skills/hierarchy-lens/scripts/audit_decisions.py skills/hierarchy-lens/assets/examples/hierarchy-lens/index.html --report projects/hierarchy-lens/artifacts/reviews/decisions-final-audit.json --screenshot projects/hierarchy-lens/artifacts/screenshots/decision-final.png
uv run --script skills/hierarchy-lens/scripts/build_explorer.py --demo --demo-size 430 --view decision --priority tokens --priority-direction descending --affinity role --eligibility generation --cell-pixels 2 --output projects/hierarchy-lens/artifacts/html/decisions-numeric.html --data-output projects/hierarchy-lens/artifacts/data/decisions-numeric.json --report projects/hierarchy-lens/artifacts/reviews/decisions-numeric-build.json
uv run --script projects/hierarchy-lens/scripts/run_decision_trials.py contract --revision FRESH-ID
uv run --script projects/hierarchy-lens/scripts/run_decision_trials.py naturalistic --revision FRESH-ID
uv run --script projects/hierarchy-lens/scripts/run_decision_trials.py generalization --revision FRESH-ID
uv run --script projects/hierarchy-lens/scripts/run_decision_trials.py boundary --revision FRESH-ID
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/RUN-ID/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script evaluations/contracts/check-hierarchy-lens.py SOURCE.json EXPLORER.html --portfolio
uv run --script projects/hierarchy-lens/scripts/collect_decision_evidence.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/test-pages-output.py
uv run --script projects/hierarchy-lens/scripts/check_organic_publication.py --report projects/hierarchy-lens/artifacts/reviews/decision-pages-navigation.json
uv run --script scripts/sync-local-skills.py --source skills/hierarchy-lens --destination .agents/skills/hierarchy-lens --check
```

The cohort helper uses `--mode json --strict`, the recorded Luna model exception, three fresh naturalistic/generalization workspaces, and exact `--expect-output` entries for every requested artifact. It asserts record/decision counts, view, pixel area, audit outcome, numeric direction, eligibility, and the generalization weights/window. The contract additionally checks the exact command. Boundary outputs are `review.json` and `review.md`; visual cases require HTML, input JSON, build JSON, audit JSON, and PNG overview at their prompt's exact paths. The independent evidence collector grades retained runs and does not launch model trials.

## Visual review and limits

Inspected the final role map, half-complete growth, rules panel with aligned values, mobile view, a 430-record numeric-priority output, and the four-of-eight-cell portfolio frame. Category order visibly affects the growth bands. Numeric order creates different value patterns; neither appearance is evidence of an intrinsic importance ranking.

This is a greedy composition engine with explicit priorities and local spatial preferences. It does not find a global optimum, infer importance on its own, reproduce organizational history, or guarantee that a whole reporting subtree is contiguous. Cell contact is packing, not a reporting edge. Exact parents remain available through lookup. The default generation rule preserves outward level progression; parent-ready eligibility deliberately allows generations to interleave. Color scope and quantiles do not alter placement priority.

The reusable recipe is [decision-growth.md](../../skills/hierarchy-lens/references/decision-growth.md), pattern `hierarchy-decision-growth`, in the cataloged `hierarchy-lens` example set. The [interactive composer](https://gvillarroel.github.io/skills/examples/hierarchy-lens/#hierarchy-decision-growth) becomes the main example. Previous organic, radial pixel, and analytical hashes redirect to their preserved pages. Publication is verified against the source commit's Pages workflow, exact main-example bytes, and live navigation of all four views.
