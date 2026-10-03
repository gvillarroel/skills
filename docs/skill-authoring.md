# Skill authoring and bundle validation

Canonical skills live in `skills/`. Authoring checks apply both to those sources
and to the files agents actually receive. The policy uses the
[Claude skill authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
and the repository's stricter naming, independence, and evaluation rules.

## Enforced checks

The validator rejects duplicate YAML keys; invalid or reserved names;
descriptions exceeding 1,024 characters, containing XML delimiters, or using
first- or second-person address or imperative capability openings; empty or
oversized entrypoints; Windows
resource paths; unrouted references; and long references without working
contents links near the top. Repository names remain shorter than 64
characters and entrypoint bodies remain below 500 lines.

Link each runtime reference file directly from `SKILL.md`, and select only
the resource matching the task. Directory links and intermediate indexes do
not replace those links. Keep the navigation concise: large collections use
one short link per recipe, while their implementation details stay in references.

Keep defaults and essential operational constraints in the entrypoint. Put
task-specific detail in references, deterministic operations in scripts, and
output resources in assets. Review description triggers, workflow clarity,
degrees of freedom, terminology, fallback behavior, script dependencies, and
actual outputs manually; static checks cannot establish their quality.

## Commands

Run the normal repository gate and an audit of actual copied bundles:

```powershell
uv run --script scripts/validate-skills.py
uv run --script scripts/audit-skill-authoring.py --check-bundles --output evaluations/runs/skill-authoring-audit.json
```

Validate an arbitrary generated bundle without requiring a repository backlog:

```powershell
uv run --script scripts/validate-skills.py --skill path/to/generated-skill
uv run --script scripts/validate-skills.py --skill path/to/runtime-skill --profile runtime
```

The [standalone authoring checker](../skills/repository-reviewer-creator/scripts/check_skill_authoring.py)
ships inside `repository-reviewer-creator`. Its generated-reviewer validator
uses the same policy without requiring this repository at generation time.
The repo gate adds resource resolution, script conventions, metadata, and
independence checks. Run regression coverage with:

```powershell
uv run --script skills/repository-reviewer-creator/scripts/test_skill_authoring.py
uv run --script skills/repository-reviewer-creator/scripts/test_validate_reviewer.py
uv run --script scripts/test-bundle-validation.py
uv run --script scripts/test-pi-eval-harness.py
```

## Bundle boundaries and release evidence

The runtime profile excludes acceptance fixtures under `assets/examples/`,
dependencies, caches, and build output. Fixture-maintenance tasks require the
full profile. Maintenance references can name excluded acceptance fixtures;
operative Markdown links must still resolve in a runtime copy. Both profiles
must retain all required runtime references, scripts, and templates.
The audit also compares every copied file with its source-profile hash,
freezes the complete skill inventory, and rejects sources modified or skills
added/removed during the audit. Rerun it after authoring finishes.

`sync-local-skills.py` validates sources before copying and validates the
resulting installed bundles. Its `--check` mode checks both source-owned file
identity and installed structure; it preserves extra local files and reports
invalid ones. `run-pi-skill-eval.py` validates source and copied bundles before
launching an agent. CI repeats the authoring regressions and audits both
profiles for every canonical skill.

Keep behavioral release evidence separate from authoring compliance. Preserve
the model, exact outputs, independent inspection, read surface, payload hash,
and every failure required by [the evaluation methodology](../evaluations/README.md).
Do not promote a skill to `done` based only on this static audit. Existing
provider, credential, quality, or user-imposed evaluation blockers remain
visible in [the backlog](../SKILLS.md).

The [2026-10-02 audit](../evaluations/skill-authoring/20261002-review.md) records
the complete skill inventory, repairs, bundle results, and forward-test scope.

The [D3 validation closeout](../evaluations/skill-authoring/20261002-d3-validation.md)
records the final frozen runtime passes and the latest complete bundle audit.
