# Skill Evaluations

Use this directory for reusable evaluation definitions, summaries, and notes for skills in this repository.

- Store bulky local run outputs under `evaluations/runs/`; that directory is intentionally ignored by git.
- Keep durable evaluation configs or small summaries in tracked files outside `evaluations/runs/`.
- Reference the validated skill by name and include the command, date, and pass/fail outcome.
- Keep generated screenshots, rendered media, local build output, and dependency folders out of git.

## Runtime Harness

Use `scripts/run-pi-skill-eval.py` for forward validation. The default runtime profile copies only `.agents/skills/<skill-name>/` into an isolated workspace and excludes `assets/examples/`, dependency folders, and build output.

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill-name> --prompt-file evaluations/pi-prompts/<prompt>.md --mode json --expect-output <artifact>
```

The default model is `openai-codex/gpt-5.3-codex-spark`. Keep that default unless a validation note records a deliberate exception.

## Prompt Files

Store reusable prompt files under `evaluations/pi-prompts/`. A good prompt:

- Names the skill being evaluated.
- Requests exact output paths in the isolated workspace.
- States that the copied `skills/<skill-name>/` directory is read-only.
- Avoids references to repository files outside the copied skill.
- Uses a task small enough to test the skill's core behavior without relying on the full acceptance gallery.

## Pass Criteria

A runtime validation passes only when all of these are true:

- `pi` exits successfully.
- Every `--expect-output` artifact exists, is a file, and is non-empty.
- The generated artifact satisfies the task after direct inspection or a medium-specific validator.
- The JSON trace shows that the run read only the target skill's focused runtime files.

Summarize JSON-mode traces with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl
```

If a normal runtime trace reads `assets/examples/`, a large gallery source, generated project artifacts, repository-level docs, sibling skills, or parent-directory references, treat the result as a validation failure. Lower the skill difficulty by adding a compact reference, deterministic script, template, or local vendor asset inside the skill, then rerun the harness.
