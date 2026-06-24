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
- Do not add auxiliary documentation inside a skill such as `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, or `CHANGELOG.md` unless the user explicitly asks for it.
- Keep `agents/openai.yaml`, when present, aligned with `SKILL.md`.

## Pattern Promotion Rules

When an example, fixture, scene, chart, conversion setting, recording flow, audit rule, or troubleshooting path becomes reusable, update the owning skill before finishing the work.

- Store the transferable pattern in the skill directory, preferably in an existing `references/` file or a direct `references/pattern-recipes.md` file when no better owner exists.
- Keep examples as acceptance fixtures, not as the only source of reusable knowledge.
- Document enough for an isolated skill-only workspace to recreate the pattern when practical: pattern name or ID, trigger context, input/data contract, implementation steps, validation command, and known pitfalls.
- Update [SKILLS.md](SKILLS.md) recent validation notes when a pattern is promoted, renamed, validated, or rejected.
- For published patterns, complete publication before handoff: run the Pages build and validators, commit the source example, references, validation notes, and catalog changes, push the Pages-deploying branch, and verify the GitHub Pages workflow so the stable pattern ID can be referenced by URL.
- If a pattern belongs to another skill, update that owning skill instead of duplicating the guidance locally.

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
