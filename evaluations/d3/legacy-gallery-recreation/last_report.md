# Legacy D3 Skill Arena Gallery Recreation

Status: archived historical dry run; not Harbor release evidence.

This pre-consolidation fixture has no development/validation/holdout boundary.
Do not use it for evolution, candidate selection, or final validation of the
unified `d3` skill. The native Harbor study under `evaluations/d3/` supersedes
it for release decisions.

Validation run:

- Historical command: `node C:\Users\villa\dev\skill-arena\bin\skill-arena.js evaluate evaluations/d3/legacy-gallery-recreation/evaluation.yaml --dry-run --requests 1 --max-concurrency 1`
- Date: 2026-06-22
- Prompts: 202
- Profiles: 1 (`skill`)
- Variants: 1 (`pi-codex-spark-5-3`)
- Planned cells: 202
- Unsupported cells: 0

Isolation checks from the generated `promptfooconfig.yaml`:

- The only profile is `skill`.
- The generated provider has `SKILL_ARENA_ALLOWED_SKILLS: d3-animated-svg`.
- The generated provider has `SKILL_ARENA_ISOLATION: strict`.
- The generated provider routes to Pi with `model: openai-codex/gpt-5.3-codex-spark`.
- The generated provider sets `disable_other_skills: true`.

Assertion checks:

- The shared evaluation assertion is `type: javascript`.
- The JavaScript assertion resolves the execution workspace from provider metadata.
- For each prompt, it reads `source-all/<case>.svg` and `deliverables/<case>/candidate.svg`.
- It checks SVG root presence, exact viewBox, minimum element count, source mark families, animation coverage, source color-role overlap, font-size range, text-node density, and `data-pattern-id` metadata when present in the source.
- A smoke test accepted all 202 source SVGs as source-as-candidate fixtures and rejected a deliberately bad candidate SVG.

The dry run generated Promptfoo configuration without running the 202 Pi evaluation requests.
