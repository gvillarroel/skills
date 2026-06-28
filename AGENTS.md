# Repository Instructions

## Purpose

This repository is the source of truth for a backlog of Codex skills to create, improve, and validate.

- Keep planned work in [SKILLS.md](SKILLS.md).
- Keep one concrete skill per directory under `.agents/skills/`, named with the skill name.
- Treat skill validation as part of the work, not an optional follow-up.

## Language Rules

- Write every skill and human-readable document in English.
- Write `SKILL.md`, reference files, `agents/openai.yaml`, backlog entries, validation notes, comments, and user-facing script output in English.
- Use non-English text only when it is required source material, a test fixture, or a quoted example. Surround it with English context.
- Code identifiers may follow existing APIs or domain terms, but prefer English for new names.

## Skill Backlog

Use [SKILLS.md](SKILLS.md) as the canonical list of skills to create or update.

Each backlog item should include:

- Skill name in lowercase hyphen-case.
- Status: `candidate`, `planned`, `in-progress`, `validating`, `done`, or `rejected`.
- Purpose and trigger contexts.
- Expected bundled resources, if any: `scripts/`, `references/`, or `assets/`.
- Validation notes and open questions.

Update the backlog whenever a skill is added, removed, renamed, rejected, or validated.

## Continuation Workflow

When continuing this repository, start from [SKILLS.md](SKILLS.md), especially the backlog table and recent validation notes. Treat each backlog row as the current state record for that skill.

- Move the skill status forward as work progresses, and leave open questions in the validation notes when a follow-up agent needs context.
- When changing skill behavior, run an isolated `pi` runtime validation before marking the skill `done`. If validation is not possible in the current pass, keep or move the skill to `validating` and record the blocker in [SKILLS.md](SKILLS.md).
- Keep acceptance fixtures and GitHub Pages example sources under the owning skill's `assets/examples/` directory, and keep reusable skill instructions under the matching `.agents/skills/<skill-name>/` directory.
- Regenerate GitHub Pages examples with `uv run --script scripts/build-pages.py` after changing examples that should be published.
- Keep generated media, local build output, screenshots, and large verification artifacts out of git unless they are intentionally small static examples stored under the owning skill's `assets/examples/` for Pages.
- Keep reusable or summarized skill evaluation material under `evaluations/`. Store bulky local evaluation runs under `evaluations/runs/`, which is ignored by git.
- Keep project-scoped scripts, notes, source material, and non-published deliverables under `projects/<project-id>/`. Use one stable lowercase hyphen-case project ID per subdirectory.
- Put generated project artifacts under `projects/<project-id>/artifacts/`, grouped by type such as `documents/`, `videos/`, `svgs/`, `gifs/`, `images/`, `screenshots/`, `data/`, `manifests/`, and `reviews/`. This folder is ignored by git.
- Use `output/` only for disposable legacy scratch output or tool build output that cannot reasonably be tied to a project.
- Before handing off, run the repo validator and payload check, then record any skill-specific validation commands in [SKILLS.md](SKILLS.md).

## Slidev ECharts Track

- Keep the reusable skill in `.agents/skills/slidev-echarts/`.
- Keep the runnable validation deck in `.agents/skills/slidev-echarts/assets/examples/slidev-echarts/`.
- Treat the example deck as the acceptance fixture for the skill. When the skill guidance changes, update the deck if needed and validate that it still builds and renders charts.
- For chart-type coverage, keep one dedicated reference file per chart type under `.agents/skills/slidev-echarts/references/charts/` and use shared synthetic data files under `.agents/skills/slidev-echarts/assets/examples/slidev-echarts/data/`.
- Keep generated Slidev build output, screenshots, and other transient verification artifacts out of skill directories. Use `projects/<project-id>/artifacts/` for project-specific verification artifacts that should be kept locally.

## Skill Authoring Rules

- Use one `.agents/skills/<skill-name>/` directory per skill.
- Use the owning skill's `assets/examples/` for acceptance fixtures and Pages example sources; do not add a new top-level `examples/` source tree.
- Name directories under `.agents/skills/` with lowercase letters, digits, and hyphens only.
- Keep skill names under 64 characters.
- Every skill directory must contain `SKILL.md`.
- In new skills, `SKILL.md` frontmatter must contain only `name` and `description`.
- The `name` field must match the directory name exactly.
- The `description` field must explain what the skill does and when Codex should use it.
- Keep the body of `SKILL.md` concise and procedural. Prefer imperative instructions.
- Use progressive disclosure: keep core workflow in `SKILL.md`, and move conditional or bulky detail into `references/`.
- Use `scripts/` only for deterministic or repeated operations.
- Use `assets/` only for files the skill needs as output resources or templates.
- Keep each skill self-contained. Required runtime references, templates, scripts, vendor shims, and examples must live inside that skill directory, not in parent directories, sibling skills, or repository-level docs.
- Do not add auxiliary documentation inside a skill such as `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, or `CHANGELOG.md` unless the user explicitly asks for it.
- Keep `agents/openai.yaml`, when present, aligned with `SKILL.md`.

## Pattern Promotion Rules

When an example, fixture, scene, chart, conversion setting, recording flow, audit rule, or troubleshooting path becomes reusable, update the owning skill before finishing the work.

- Store the transferable pattern in the skill directory, preferably in an existing `references/` file or a direct `references/pattern-recipes.md` file when no better owner exists.
- Keep examples as acceptance fixtures, not as the only source of reusable knowledge.
- When a gallery, fixture, or generated example grows large, split reusable patterns into compact per-pattern references and make the runtime path point to those references instead of the large fixture source.
- Document enough for an isolated skill-only workspace to recreate the pattern when practical: pattern name or ID, trigger context, input/data contract, implementation steps, validation command, and known pitfalls.
- Update [SKILLS.md](SKILLS.md) recent validation notes when a pattern is promoted, renamed, validated, or rejected.
- For published patterns, complete publication before handoff: run the Pages build and validators, commit the source example, references, validation notes, and catalog changes, push the Pages-deploying branch, and verify the GitHub Pages workflow so the stable pattern ID can be referenced by URL.
- If a pattern belongs to another skill, update that owning skill instead of duplicating the guidance locally.

## Example Catalog Rules

Published examples must be referenceable and discoverable from the repository's main examples page.

- Every published example set must have a stable lowercase hyphen-case ID. Use the same ID in source metadata, gallery DOM attributes, generated Pages cards, validation notes, and pattern references.
- When adding an example set under `.agents/skills/<skill-name>/assets/examples/`, add it to `PUBLISHED_EXAMPLE_SETS` in `scripts/build-pages.py` unless it is only a raw support folder for another published gallery. Support-only folders must be named in `UNLISTED_EXAMPLE_SOURCES` with a short comment.
- The main GitHub Pages index is the canonical list of published example sets. Do not publish a Pages example that is reachable only by knowing its path.
- Individual gallery items should also expose stable item IDs when the gallery contains more than one example. Prefer `id`, `data-example-id`, `data-pattern-id`, `data-chart-type`, or a domain-specific equivalent that appears in verification output.
- After changing published examples or the example catalog, run `uv run --script scripts/build-pages.py` and `uv run --script scripts/validate-skills.py`.
- When adding or changing a published pattern, treat GitHub Pages publication as part of the normal workflow: commit the source example, references, validation notes, and catalog changes, push the branch that deploys Pages, and verify the Pages workflow completed so the stable pattern ID can be referenced by URL.

## Isolated Skill Validation

Validate skills as standalone bundles before treating them as done. The target question is: can an agent with only the evaluated skill, a task prompt, and normal local tools produce a good result?

- Use `pi` as the isolated harness for forward tests. Use `gpt-5.3-codex-spark` through `--model openai-codex/gpt-5.3-codex-spark` unless a backlog note explicitly records a different model.
- Run `pi` from a temporary workspace under `evaluations/runs/`, not from the repository root. Copy only `.agents/skills/<skill-name>/` into that workspace.
- Use the runtime payload profile for normal skill-use tests: include `SKILL.md`, `agents/`, `references/`, `scripts/`, and runtime `assets/` such as templates, but exclude acceptance fixtures under `assets/examples/` and dependency folders such as `node_modules`. Use a full payload only when the task is to maintain or validate the fixture itself.
- Disable ambient context and skill discovery with `--no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes`, and load exactly the copied skill with `--skill skills/<skill-name>`.
- Treat the copied `skills/<skill-name>/` directory as a read-only resource during forward tests. Generated task files should be written to the workspace root or a requested project/artifact directory, not into the copied skill directory.
- If the prompt names exact output paths, the run must create those exact paths. Substituting descriptive filenames or default artifact directories counts as a validation failure unless the prompt explicitly allows it.
- Use `--expect-output` for every required artifact path so wrong or missing output paths fail the harness even when `pi` exits successfully.
- Use `--mode json` for at least one final validation run per changed skill, then inspect the read surface with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl
```

- A healthy runtime trace should read `SKILL.md` plus only the specific references, scripts, templates, or small vendor files needed for the task. If a normal runtime run reads `assets/examples/`, generated galleries, project artifacts, repository-level docs, sibling skills, or a large source file that is not directly required, treat that as a skill design problem and simplify the skill before passing it.
- Prefer compact references under roughly 10 KB for pattern recipes. If a task requires reading a larger file, document why; if a single gallery or fixture source is above roughly 50 KB and is read during normal runtime validation, split it into smaller in-skill references or add a script/template that avoids the large read.
- Prefer the repo helper:

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill-name> --prompt-file <prompt.md> --mode json --expect-output <artifact>
```

- Keep durable evaluation summaries or reusable prompts under `evaluations/`; keep bulky run folders under `evaluations/runs/`.
- Judge the output against the skill's intended trigger surface, not against hidden repository knowledge. Inspect generated artifacts when the skill produces visual, document, spreadsheet, or code output; use browser, Playwright, ffprobe, renderers, screenshots, or domain-specific validators as appropriate.
- If a skill-only `pi` run cannot produce quality work, reduce the skill's difficulty instead of raising evaluator expectations: add a clearer script, template, fixture, checklist, or compact in-skill reference.
- Never point a skill to repository files, sibling skills, parent directories, or project docs as required reading. If the skill needs a reference, copy or summarize it inside that skill's own `references/`, `scripts/`, or `assets/` tree.
- Record the command, date, model, pass/fail outcome, and any follow-up simplification in [SKILLS.md](SKILLS.md).

## Script Rules

Scripts may be TypeScript or `uv` Python.

- Put repo-level scripts in `scripts/`.
- Put skill-specific scripts in the relevant skill's `scripts/` directory.
- Put project-specific scripts in `projects/<project-id>/scripts/` when they are not intended to ship as skill resources or GitHub Pages examples.
- Python scripts must use `uv` script metadata and a shebang that defines the runtime:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

- TypeScript scripts must be `.ts` files and include a shebang or documented run command that uses a TypeScript runner such as `tsx`.
- Declare TypeScript dependencies in `package.json` when the repo or skill has one. For standalone scripts, document required packages in a short header comment.

## Validation Rules

Before finishing changes to skills or repository rules, run:

```powershell
uv run --script scripts/validate-skills.py
```

The validator checks repo structure, backlog presence, skill metadata, skill naming, and script conventions. It cannot prove that prose is English, so review language manually before finalizing.

When updating one skill, also run any skill-specific tests or representative scripts that were changed.
