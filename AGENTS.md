# Repository Instructions

## Purpose

This repository is the source of truth for a backlog of Codex skills to create, improve, and validate.

- Keep planned work in [SKILLS.md](SKILLS.md).
- Keep one concrete skill per top-level directory, named with the skill name.
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
- Keep acceptance fixtures under `examples/` and reusable skill instructions under the matching top-level skill directory.
- Regenerate GitHub Pages examples with `uv run --script scripts/build-pages.py` after changing examples that should be published.
- Keep generated media, local build output, screenshots, and large verification artifacts out of git unless they are intentionally small static examples for Pages.
- Before handing off, run the repo validator and payload check, then record any skill-specific validation commands in [SKILLS.md](SKILLS.md).

## Slidev ECharts Track

- Keep the reusable skill in `slidev-echarts/`.
- Keep the runnable validation deck in `examples/slidev-echarts/`.
- Treat the example deck as the acceptance fixture for the skill. When the skill guidance changes, update the deck if needed and validate that it still builds and renders charts.
- For chart-type coverage, keep one dedicated reference file per chart type under `slidev-echarts/references/charts/` and use shared synthetic data files under `examples/slidev-echarts/data/`.
- Keep generated Slidev build output, screenshots, and other transient verification artifacts out of skill directories. Use `output/` for verification artifacts that should be kept.

## Skill Authoring Rules

- Use one top-level directory per skill.
- Use `examples/` for non-skill example artifacts; do not treat it as a skill directory.
- Name skill directories with lowercase letters, digits, and hyphens only.
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

## Script Rules

Scripts may be TypeScript or `uv` Python.

- Put repo-level scripts in `scripts/`.
- Put skill-specific scripts in the relevant skill's `scripts/` directory.
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
