# Codex Skills Repository: repository guide

A maintained collection of reusable skills, compact references, deterministic helpers, and acceptance examples. Canonical bundles live in `skills/`; the backlog and validation status live in `SKILLS.md`.

## Layout

| Path | Responsibility |
| --- | --- |
| `skills/` | Canonical skill bundles, including runtime references and acceptance examples. |
| `SKILLS.md` | Authoritative backlog, status, and validation notes. |
| `scripts/` | Repository validators, installation helpers, and Pages builder. |
| `evaluations/` | Durable summaries; bulky runs remain ignored. |
| `projects/` | Project-specific source material and ignored generated artifacts. |
| `docs/` | Tracked human documentation; never generated build output. |
| `dist/pages/` | Ignored, reproducible GitHub Pages build output. |

## Documentation policy

- Keep the root `README.md` focused on purpose, critical constraints, and the first useful action. Put detailed procedures in `docs/`.
- Maintain `docs/README.md` as the navigation index whenever a guide is added or moved.
- Preserve existing specification, ADR, skill-contract, and evidence locations. Link to their owners instead of copying authoritative content.
- Keep implementation, configuration, source data, and generated output separate. Do not create empty folder hierarchies without a concrete need.
- Use portable relative links. Update both outgoing links and inbound references when moving a document.
- Document prerequisites, commands, expected outcomes, and limitations. Never describe an unrun check as verified.

## Change workflow

1. Read `AGENTS.md`, this index, and the relevant source contract.
2. Inspect `git status` and preserve pre-existing changes and staged files.
3. Make a focused change and update affected documentation in the same change.
4. Run the applicable checks below, inspect the diff, and record any unavailable prerequisite.
5. Stage explicit paths. Publish only when authorized; do not force-push or merge unrelated work.

## Validation

```sh
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

When published examples or the Pages pipeline change, also run `uv run --script scripts/build-pages.py` and `uv run --script scripts/validate-pages-pattern-format.py`. Skill behavior changes additionally require the isolated forward tests defined in AGENTS.md.

## Data and operating boundaries

Never edit installed copies under `.agents/skills/` as canonical source. Keep model runs, generated media, credentials, and project artifacts out of Git. Pages builds must write only to `dist/pages/` and must not remove or overwrite authored documentation in `docs/`.

[Back to the documentation index](README.md).
