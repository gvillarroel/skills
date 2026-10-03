# Thematic art-direction validation — 2026-09-12

The disclosed development case evaluates planning and prompt preparation for a subject-specific spacecraft poster. It does not test image generation, final aesthetic parity or a finished 95-record poster.

Before execution, register three fresh naturalistic Pi runs on the frozen runtime skill using the default `openai-codex/gpt-5.3-codex-spark` model. Required outputs are `design/art-direction.md` and `design/art-prompts.json`. Require at least two complete passes out of three, retain every outcome, and review the produced plans independently after execution. Evaluate a coherent subject-specific art direction, distinct reference-bound assets, sufficient production inputs, correct temporal encodings and a concrete visual repair process. A plan cannot claim the missing 90 records or completed reference-density evidence.

Commands and observed outcomes will be recorded after execution. Keep the overall skill `validating`; the application and planning case do not establish general visual parity.

## First cohort and focused repair

Retain `usefulcharts-theme-spark-{1,2,3}-20260912`. Execution passes 2/3: run 1 records two real Bash tool errors, including a PowerShell command sent to Bash and a failed local JSON check. All six requested files exist and every runtime payload stays unchanged. Independent review rejects production prompt readiness in all three plans: runs 1 and 3 bake forward/rightward trails into the Argo asset, while runs 2 and 3 propose unsupported successor geometry; camera/lighting instructions are inconsistent across subjects. Run 2 also proposes an ultra-wide background for its portrait poster. These are planning/prompt quality failures, not final rendering results.

The thematic reference now supplies a compact shared render contract, keeps dates in adjacent metadata, excludes raster trails, matches background aspect ratio and distinguishes separate hull identity from changed design. Register three fresh runs on this revised frozen bundle as `usefulcharts-theme-b-spark-{1,2,3}-20260912`, with the same task, default model, required paths and acceptance criteria. Keep both cohorts in the record.

## Revised cohort and acceptance boundary

Cohort B passes 3/3 strict executions with six exact artifacts, valid JSON, the requested model, zero tool errors, clean isolated read boundaries and unchanged 117-file runtime payload `fd03bcbd84d079770f69f5c862e1ff2d7787660b32c7d3e8154e58f22a255e8d`. It does **not** pass independent prompt-readiness review. B1 lacks a common camera and assumes an unsupported sibling design lineage; B2 does not read the required thematic reference and adds unsupported relative speed, motion blur and successor geometry; B3 improves shared camera/lighting and excludes trails but still labels Argo II next-generation and requires a different design merely because it is a separate hull. These are agent-level departures from the supplied instructions, retained as failures rather than counted as release evidence.

Across both cohorts, execution is 5/6 and complete acceptance is 0/6. The prompt pack outputs preserve the broad point/interval distinctions, but reliable reference-bound art preparation remains pending. The actual Star Trek application was authored and inspected directly with real image generation; its success does not erase the isolated failures. No image-generation capability, Luna comparison, blind generalization or model-ranking conclusion is supported by this planning-only case. The skill remains `validating`.

Run each cohort with:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-thematic-art-direction.md --mode json --strict --run-id <registered-run-id> --timeout-seconds 240 --expect-output design/art-direction.md --expect-output design/art-prompts.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<registered-run-id>/events.jsonl --output evaluations/runs/<registered-run-id>/read-surface.json --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
uv run --script projects/star-trek-starships/scripts/summarize_theme_validation.py
```

The trace command correctly fails for A1's retained tool error. See [all outcomes, payloads and output hashes](thematic-art-direction-summary-20260912.json) and [the separately verified visual application](starships-space-edition-20260912.md). Runtime resources remain below the per-reference read-size boundary; the new thematic guide is under 10 KB. No published gallery or Pages artifact is changed.

Repository validation passes: `validate-pattern-ids.py` (1,222 IDs), `validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py`, the skill creator's `quick_validate.py`, and `git diff --check`. `sync-local-skills.py` copies the two new/changed runtime files; its targeted `--check` matches all 134 canonical source-owned files. No bundled renderer code changed in this thematic revision.
