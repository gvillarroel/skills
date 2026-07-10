# Skill Evaluation Methodology

Use this directory for repeatable evaluation definitions, prompts, compact results, and review notes. The objective is to answer one question: can an agent with only the target skill, the task prompt, and normal local tools produce a correct result without hidden repository knowledge?

Use `openai-codex/gpt-5.3-codex-spark` as the default forward-test model. Record any deliberate model exception in `SKILLS.md`.

## Evidence Layout

- Store reusable prompts under `evaluations/pi-prompts/`.
- Store independent acceptance contracts under `evaluations/contracts/`.
- Store compact, durable summaries directly under `evaluations/` or a skill-specific subdirectory.
- Store raw prompts, copied workspaces, JSONL events, stdout, stderr, manifests, and generated artifacts under `evaluations/runs/`. This directory is ignored by Git.
- Keep screenshots, rendered media, and dependency folders out of tracked evaluation paths.

Every recorded result must identify the skill, case, date, model, command, required outputs, validators, pass/fail outcome, and failure classification. Link the durable result from the matching `SKILLS.md` validation note.

## Release Gates

Run the gates in order. Stop and repair the earliest failing layer before interpreting later results.

### Gate 0: Static repository integrity

```powershell
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
```

Also compile or test every changed skill-specific script. Run the relevant fixture or example checks when the change affects a published example.

### Gate 1: Deterministic skill checks

Run bundled validators, builders, schema checks, and exact-path smoke tests without an LLM. These checks prove that the reusable machinery works; they do not prove that an agent can use the skill.

Prefer small fixtures. Verify exit codes, exact output paths, non-empty files, machine-readable fields, and deterministic reruns.

### Gate 2: Isolated Spark forward tests

Use the runtime payload unless the task explicitly maintains an acceptance fixture. The runtime profile copies only the target bundle and excludes `assets/examples/`, dependency folders, caches, and build output.

Use strict JSON mode for release evidence:

```powershell
$RunId = "<date>-<skill>-<case>-spark-1"
uv run --script scripts/run-pi-skill-eval.py <skill> `
  --prompt-file evaluations/pi-prompts/<case>.md `
  --mode json `
  --strict `
  --run-id $RunId `
  --expect-output <exact-workspace-relative-artifact>
```

Repeat `--expect-output` for every required artifact. Use `--expect-output-json-field path::field=value` for objective JSON gates. Add `--require-exact-command-from-prompt` only for command-contract cases; naturalistic cases should leave the implementation path open.

Strict mode requires:

- JSON events and at least one exact, non-empty output.
- `../prompt.md` as the first completed tool read.
- the observed provider/model to equal `openai-codex/gpt-5.3-codex-spark`.
- valid JSONL and zero tool errors.
- for the default `runtime` profile, no reads from `assets/examples/`; both profiles forbid sibling skills and paths that resolve outside the isolated workspace other than canonical `../prompt.md`. Absolute tool paths inside the workspace are normalized before policy checks.
- no add, remove, or modification inside the copied read-only skill payload, verified by SHA-256 before and after the run.

`--profile full --strict` is reserved for fixture-maintenance tasks. It permits reads from the target skill's own `assets/examples/` while retaining model, tool-error, sibling-skill, outside-workspace, exact-output, and integrity gates. Do not add the runtime-only `assets/examples` forbid regex when summarizing a full-profile trace.

The harness writes `run-manifest.json`, `artifact-check.json`, `event-check.json`, `skill-integrity-check.json`, optional `json-field-check.json`, and `evaluation-result.json`. The manifest records prompt and payload hashes, model settings, tool versions, platform, and Git revision state.

### Gate 3: Independent artifact validation

Do not accept the agent's self-report as the grader. Inspect the generated artifact after `pi` exits and run an independent validator from the evaluator side.

- Code and data: compile, run tests, validate schemas, and inspect key values.
- HTML/SVG: serve when required, use Playwright, inspect DOM contracts, capture desktop/mobile screenshots, and check the final state.
- Slidev: build, traverse slides and click states, check charts/media, and audit overflow, clipping, contrast, and blank states.
- Video: use `ffprobe`, inspect duration/dimensions/frame rate/audio, generate a contact sheet, sample motion, and check frozen or blank intervals.
- Documents and PDFs: render pages and inspect layout, clipping, typography, and pagination.
- GIF and animated SVG: inspect dimensions, duration, loop behavior, representative frames, and final-frame fidelity.

Store the validator command and result with the compact evaluation summary. A skill-owned validator is useful, but high-risk releases should also use an evaluator-owned contract or direct inspection.

### Gate 4: Trace and read-surface review

Create a compact trace summary and require the observed Spark model:

```powershell
uv run --script scripts/summarize-pi-json-events.py `
  evaluations/runs/$RunId/events.jsonl `
  --output evaluations/<skill>-<case>-read-surface.json `
  --require-model gpt-5.3-codex-spark `
  --require-tool-call `
  --fail-on-invalid-json `
  --fail-on-tool-error `
  --require-read ../prompt.md `
  --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' `
  --forbid-read-regex '(?i)^skills[\\/](?!<skill>([\\/]|$))'
```

Inspect the read list, not only `passed`. Normal runtime work should read `SKILL.md` plus only the focused references, scripts, templates, or small vendor files required by the task. Treat reads of large galleries, repository docs, project artifacts, sibling skills, or unrelated references as a design failure.

The trace is an evaluation record, not a security sandbox. Case-specific prompts should also forbid unnecessary repository discovery, network access, or external state changes, and reviewers should inspect shell commands for indirect reads that a read-tool policy cannot see.

## Case Design

Use distinct cases because a single scripted smoke test cannot prove general skill quality.

| Case | Purpose | Prompt style | Minimum use |
| --- | --- | --- | --- |
| `contract-smoke` | Prove exact paths and bundled scripts work | May include an exact command | Every changed skill |
| `naturalistic-forward` | Prove the agent can select and apply the workflow | User-like request, no implementation recipe | Every changed skill |
| `boundary-recovery` | Prove behavior on ambiguity, invalid input, or a likely failure mode | State constraints and expected safe outcome | Complex or high-risk skills |
| `generalization` | Prove the skill transfers beyond its acceptance fixture | New data, layout, domain, or scale | New skills and major revisions |
| `routing-control` | Test whether metadata triggers the right skill and avoids unrelated skills | Run without forced `--skill` selection | New or materially changed triggers |

For a narrow deterministic skill, use one contract smoke and one naturalistic case. For a complex visual, document, or video skill, add boundary/recovery and generalization cases. A routing control is separate from the isolated harness because `run-pi-skill-eval.py` intentionally forces exactly one skill.

### Prompt contract

A reusable prompt must:

- sound like a plausible user request;
- name exact workspace-relative output paths;
- state that `skills/<skill>/` is read-only;
- keep generated files in the workspace, not inside the skill;
- contain all task inputs or create small fixtures in the workspace;
- avoid repository paths, sibling skills, hidden expected answers, and acceptance galleries;
- define observable acceptance criteria without dictating the solution, except in a command-contract smoke test.

Do not tell the tested agent the suspected bug or desired refactor. Forward tests measure whether the skill generalizes, not whether the model can reproduce evaluator hints.

## Repetition and Thresholds

- Deterministic command-contract cases: one passing run after local deterministic checks.
- Naturalistic or generalization cases: three fresh runs; require at least two passes out of three.
- Safety-critical, destructive, or externally consequential workflows: require three passes out of three and direct human review.
- Never reuse a workspace between repetitions. Do not expose artifacts or conclusions from an earlier run.

Record every repetition, including failed attempts. Do not select only the best output. If a failure is due to infrastructure, rerun after recording the failure class; do not silently count it as a skill pass or regression.

## Pass Criteria

A case passes only when all applicable checks pass:

1. `pi` exits successfully and the observed model matches Spark.
2. Every exact artifact exists inside the workspace, is a regular non-empty file, and has a recorded SHA-256.
3. JSON field assertions and external validators pass.
4. The artifact satisfies the task after direct or medium-specific inspection.
5. The event trace is valid, contains no tool errors, and has an acceptable read surface.
6. The copied skill payload is unchanged.
7. The run did not depend on ambient repository context, sibling skills, acceptance fixtures, undeclared services, or hidden evaluator knowledge.

A zero exit code, a polished final message, or a validator JSON produced by the tested agent is not sufficient on its own.

## Failure Classification

Classify failures before changing the skill:

- `skill`: missing, ambiguous, bloated, or incorrect instructions/resources.
- `agent`: the skill was sufficient, but the sampled agent failed to apply it.
- `validator`: the acceptance check is incorrect, too weak, or too coupled to one implementation.
- `harness`: isolation, event parsing, path checks, timeout handling, or evidence capture failed.
- `infrastructure`: browser, codec, package registry, authentication, quota, or local tool failure.
- `external-service`: a required remote endpoint failed or changed.

Repair the owning layer. If a normal skill-only run cannot produce quality work, reduce the skill's difficulty with a clearer compact reference, deterministic script, template, or bundled vendor asset instead of weakening acceptance criteria.

## Status and Evidence Retention

Move a changed skill to `validating` until the required gates pass. Mark it `done` only after recording the command, date, model, cases, repetition result, artifact validation, and read-surface summary in `SKILLS.md`.

Raw runs are intentionally ignored and can grow quickly. Keep the latest passing release run, the failure that motivated a fix, and any run needed for an active investigation. Delete older local runs only as an explicit maintenance action after durable summaries and required artifacts have been preserved.
