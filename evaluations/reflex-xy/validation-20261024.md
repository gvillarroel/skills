# Reflex XY validation

Date: 2026-10-24. Skill: [reflex-xy](../../skills/reflex-xy/SKILL.md).
Status: `validating`. The bundle is created and locally installed; the final
naturalistic cohort does not meet the strict release threshold.

## Subject and scope

The final V4 bundle has ten runtime files and payload inventory SHA-256
`84cf8e2ece0e66bf5ac7cfa30a885da8b3ec0daa4e09a8cb07f5ef702ba66e3a`.
V4 changes only the entrypoint's checker-label guidance from V3; both scripts
are byte-identical. Exact script hashes and the final audit appear in the
independent review.
Source, runtime and full payloads are identical; no acceptance gallery or
repository-specific resource is needed at runtime.

The executable baseline is published `xy==0.0.8`, release tag commit
`6483032a7947e1f44ced1a560ac08f1025637529`. Research also checked main commit
`d95f84b6d61a6524d9af3f7879ba444dab095ae9`. The bundle records the stale
0.0.1 installation prose rather than repeating its Windows wheel claims.
Core probes used native Windows Python 3.14.7; isolated uv scripts resolved
Python 3.13.12. The package requires Python 3.11 or newer.

## Deterministic and reference checks

- Real native backend, HTML, SVG and PNG probe passed; its JSON file records
  version, platform, memory, actual file sizes and SHA-256 values.
- The editable runtime starter produced HTML/SVG/PNG/memory outputs and passed
  offline Edge rendering with zero attempted HTTP(S) requests or JavaScript
  errors. Its native PNG and browser screenshot were visually inspected.
- Every Python fence in the chart, output and large-data references executed.
  SVG export forced lazy chart validation. HTML, PNG, SVG, PDF and WebP export,
  canonical pick and range selection passed.
- All three Reflex examples constructed and passed actual compiler dry runs
  with XY 0.0.8 and Reflex 0.10.0 in separate app processes. Static, state-data
  and inline-event tiers were checked. Pyplot plot/legend/PNG/close also passed
  and its image was inspected.
- The independent diagnostic contract passed 5/5 cases, including copied-bundle
  boundaries, path collision, actual native outputs and a missing-package error.
- Final browser helper controls passed 9/9, including real paint, absent labels,
  hidden SVG text, ancestor zero-opacity text, blank canvas, blocked HTTP,
  console error and page error. The evaluator's visibility controls pass 4/4.
- Source/runtime/full authoring audits report zero issues and the final hash
  above. Metadata-only qualitative assistant review selected five XY requests
  and rejected five near misses. This is not measured automatic discovery.

Commands, retained evaluator failures, helper controls and profile hashes are
recorded in [the independent review](review-20261024.md). The diagnostic
contract is [reflex-xy-diagnostic.py](../contracts/reflex-xy-diagnostic.py).

## Isolated forward tests

The required Spark attempt was retained as
`evaluations/runs/20261024-reflex-xy-contract-spark-1`. The provider rejected
`gpt-5.3-codex-spark` with this ChatGPT account before any tools ran. It produced
no artifacts and is an **infrastructure failure**, not a skill pass.

The deliberate replacement model is `openai-codex/gpt-5.6-sol`, recorded in
SKILLS.md before use. All evaluated cases use the runtime payload and
`--mode json --strict`. No output, model, isolation, payload integrity or
zero-tool-error gate was waived. The independent artifact validator is
[reflex-xy.py](../contracts/reflex-xy.py); it regenerates source outputs,
checks original records, parses native files, opens HTML with HTTP(S) blocked,
checks actual visible labels, dispatches basic pointer input and captures pixels.
Manual inspection checks layout, source mapping, missing-value gaps and prose.

| Case | Prompt | Exact required outputs | Repetitions |
| --- | --- | --- | --- |
| Contract smoke | [contract](../pi-prompts/reflex-xy-contract.md) | `artifacts/probe/chart.html`, `.svg`, `.png`, `artifacts/probe.json` | 1 |
| Naturalistic forward | [scatter](../pi-prompts/reflex-xy-naturalistic.md) | `app.py`, `results/cloud.html`, `results/cloud.svg` | 3; require at least 2 joint passes |
| Generalization | [time series](../pi-prompts/reflex-xy-generalization.md) | `app.py`, `results/trend.html`, `results/trend.png` | 3; require at least 2 joint passes |
| Boundary recovery | [offline callback](../pi-prompts/reflex-xy-boundary.md) | `design.md`, `app.py`, `results/selection.html` | 1 |

Recorded final run IDs use
`20261024-reflex-xy-v4-<case>-sol-<repetition>`. Reproduce a case with the
following command, replacing the case, run ID and output list from the table:

```powershell
uv run --script scripts/run-pi-skill-eval.py reflex-xy `
  --prompt-file evaluations/pi-prompts/reflex-xy-naturalistic.md `
  --model openai-codex/gpt-5.6-sol --mode json --strict `
  --run-id 20261024-reflex-xy-v4-naturalistic-sol-1 `
  --timeout-seconds 600 `
  --expect-output app.py --expect-output results/cloud.html `
  --expect-output results/cloud.svg
```

Contract smoke additionally uses `--require-exact-command-from-prompt` and
`--expect-output-json-field artifacts/probe.json::passed=true`. Every named
artifact has a separate `--expect-output` flag. Existing run directories are
immutable evidence; choose a fresh run ID for a new reproduction.

Independent checking and read-surface review use:

```powershell
uv run --script evaluations/contracts/reflex-xy.py `
  evaluations/runs/<run-id> --case <case> `
  --output evaluations/runs/<run-id>/independent-check.json
uv run --script scripts/summarize-pi-json-events.py `
  evaluations/runs/<run-id>/events.jsonl `
  --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error `
  --output evaluations/runs/<run-id>/read-surface.json
```

Final V4 outcomes:

| Run suffix after `20261024-reflex-xy-v4-` | Strict harness | Independent artifacts | Manual review | Joint result |
| --- | --- | --- | --- | --- |
| contract-sol-1 | Pass | Pass | Pass | Pass |
| naturalistic-sol-1 | Fail: tool error | Pass | Pass | Fail |
| naturalistic-sol-2 | Fail: tool error | Pass | Pass | Fail |
| naturalistic-sol-3 | Pass | Pass | Pass | Pass |
| generalization-sol-1 | Pass | Pass | Pass | Pass |
| generalization-sol-2 | Pass | Pass | Pass | Pass |
| generalization-sol-3 | Pass | Pass | Pass | Pass |
| boundary-sol-1 | Pass | Pass | Pass | Pass |

Contract and boundary each pass 1/1; generalization passes 3/3; naturalistic
passes 1/3 and misses the required 2/3. Keep `validating`. The first naturalistic
agent supplied unsupported `xy.text(size=12)` before correcting it. The second
asserted that an unmapped sample identifier must appear in a tooltip, despite
the skill's metadata caveat; its actual hover channels rendered correctly.
Both are **agent failures** under the unchanged strict zero-tool-error gate.
No repeat was added to replace either failure.

All eight final artifacts passed the independent validator and manual review;
all eight browser loads recorded zero HTTP(S) requests and JavaScript errors.
All eight exact outputs and payload-integrity checks pass. Trace review finds
only the prompt, entrypoint, focused references/template and workspace outputs:
no acceptance fixtures, sibling skills, repository documentation or large
unrelated resources. The trace summaries retain the two tool errors. The
copied payload hash matches final source in all eight manifests.

The remaining release work is a fresh, prospectively defined naturalistic
cohort on an appropriately frozen subject that meets the existing threshold.
Do not pool earlier successful runs or convert artifact-only passes into joint
passes. Raw events, outputs, manifests, hashes, screenshots, read-surface and
independent/manual checks remain under the ignored run directories.

## Retained earlier subjects and corrections

V1 hash: `4a9ac4477a7d85c4baafabba1883d4b1459c7770082d1686f9a7bd405b92a697`.
Its eight artifacts passed independent and visual inspection. Strict results
were contract 1/1, naturalistic 0/3, generalization 2/3 and boundary 0/1.
Retained errors included an unguarded missing-package check, row dictionaries
passed as a column table, guesses at nonexistent annotation/callback APIs,
and ad hoc browser checks. Promoted transferable fixes into the bundle:
safe package detection, explicit row-to-column conversion, a public `xy.text`
recipe, tooltip metadata limits, and a deterministic offline browser verifier.

V2 was an interim six-run subject: contract 1/1, naturalistic 2/2,
generalization 0/2 and boundary 0/1 strict; all six artifacts passed independent
and manual checks. Remaining strict failures were exploratory agent errors,
including guessed callbacks-as-methods and a mismatched encoded label. A
separate negative control found that the new helper accepted hidden SVG label
text. That **skill defect** was fixed before V3 by checking actual label
visibility and ancestor opacity. The evaluator had the same visibility weakness;
its independent DOM-range check was repaired and verified with negative controls.
The earlier delivered chart labels were actually visible in inspected pixels.

V3 strict results were contract 1/1, naturalistic 2/3, generalization 0/3 and
boundary 0/1. All eight artifacts passed the corrected independent validator
and manual inspection, with source rows, gaps and visible notes intact.
Original tool errors remain failures. Two generalization attempts demonstrate
an actual Windows shell encoding failure: the model's command contained an em
dash but Python received a replacement character, causing a strict label mismatch.
Other failures were case/fragment expectations and an unsuccessful ad hoc hover
probe. V4 makes case-sensitive DOM matching and ASCII command fragments explicit;
it retains Unicode in source files and requires screenshot review for annotations.
It changes no executable script. Canvas/DOM text has a limited automatic surface;
the actual V3 time-series notes were visible DOM annotation labels, documented
in each generalization run's `independent-annotation-dom.json`.

Earlier subjects are retained and are not pooled into V4 acceptance. No model
output was edited to turn a failed run into a pass. The independent review
also retains a Python environment contamination failure classified as harness,
followed by an isolated-interpreter correction in the evaluator.

## Repository gates and delivery boundaries

The following commands pass on this change:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

The colorset inventory records XY-native/user-selected paint honestly; this
skill does not claim exact repository colorset compliance for upstream chrome
or continuous color maps. No published example set was added, so the Pages
catalog and build are unchanged. Existing unrelated work was preserved.

Frontend npm builds, deployed Reflex event delivery, all notebook hosts,
all chart families and hardware performance were not established by these
checks. Compiler dry runs and browser snapshot verification have distinct
scopes. No public deployment, Git commit or push is part of this task.
