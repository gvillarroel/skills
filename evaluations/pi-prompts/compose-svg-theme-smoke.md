# Compose theme command smoke

Use only the read-only `skills/compose-synchronized-svg/` bundle. Keep generated files in the workspace; do not read examples, sibling skills, repository context, or network sources.

Create a standalone SVG from the bundled compact brief template, using its supported editorial palette. Copy the template to `outputs/smoke/brief.json`, preflight it, compile `outputs/smoke/plan.json`, and compose `outputs/smoke/atlas.svg`. Do not modify the copied skill or patch the resulting SVG. Run the bundled static validator and save `outputs/smoke/static.json` with `ok: true`.

This is a deterministic command smoke, so use these commands after preparing the exact brief path. In Git Bash on Windows create `.tmp` and set `TMPDIR` to that workspace directory for each `uv` command.

```text
uv run --script skills/compose-synchronized-svg/scripts/preflight_svg_brief.py --brief outputs/smoke/brief.json --json
uv run --script skills/compose-synchronized-svg/scripts/compile_synchronized_svg_plan.py --brief outputs/smoke/brief.json --output outputs/smoke/plan.json --force --json
uv run --script skills/compose-synchronized-svg/scripts/compose_synchronized_svg.py --spec outputs/smoke/plan.json --output outputs/smoke/atlas.svg --force --json
uv run --script skills/compose-synchronized-svg/scripts/validate_synchronized_svg.py outputs/smoke/atlas.svg --output outputs/smoke/static.json --json --min-modules 6 --min-asset-types 6 --min-renderer-families 5
```

Do not launch a browser for this case. Briefly report the exact files and observed validation result.
