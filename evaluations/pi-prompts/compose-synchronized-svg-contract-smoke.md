Use the loaded `compose-synchronized-svg` skill to run a deterministic compose, validate, and browser-audit contract smoke test.

Work only from this prompt and the loaded skill at `skills/compose-synchronized-svg/`. Treat the entire skill directory as read-only. Do not edit, copy back into, or generate files inside it. Do not inspect parent directories, sibling skills, repository documentation, evaluation files, hidden context, or the network. Do not enumerate the workspace or look for alternative examples. Do not use remote resources, package installation, or substitute tools.

Run this exact shell command from the workspace root, including the `bash -lc` wrapper. Copy it byte-for-byte in one tool call. The validator flag is exactly `--min-asset-types`; `--min-2-asset-types` does not exist. Never type a variant and never retry a corrected command:

```bash
bash -lc 'mkdir -p outputs .tmp && cp skills/compose-synchronized-svg/assets/templates/composition-brief.json outputs/composition-brief.json && TMPDIR="$(pwd)/.tmp" uv run --script skills/compose-synchronized-svg/scripts/preflight_synchronized_svg_brief.py --brief outputs/composition-brief.json --json && TMPDIR="$(pwd)/.tmp" uv run --script skills/compose-synchronized-svg/scripts/compile_synchronized_svg_plan.py --brief outputs/composition-brief.json --output outputs/composition-plan.json --force --json && TMPDIR="$(pwd)/.tmp" uv run --script skills/compose-synchronized-svg/scripts/compose_synchronized_svg.py --spec outputs/composition-plan.json --output outputs/composed.svg --report outputs/composition-report.json --force --json && TMPDIR="$(pwd)/.tmp" uv run --script skills/compose-synchronized-svg/scripts/validate_synchronized_svg.py outputs/composed.svg --require-time-sync --min-modules 6 --min-asset-types 6 --min-renderer-families 5 --min-shared-sources 1 --min-modules-per-shared-source 2 --min-encodings-per-shared-source 2 --output outputs/static-validation.json --json && TMPDIR="$(pwd)/.tmp" uv run --script skills/compose-synchronized-svg/scripts/audit_synchronized_svg.py outputs/composed.svg --report outputs/browser-audit.json --screenshot outputs/overview.png --compact-report'
```

Do not change the command, flags, template, or paths. These seven exact files are required:

- `outputs/composition-brief.json`
- `outputs/composition-plan.json`
- `outputs/composition-report.json`
- `outputs/composed.svg`
- `outputs/static-validation.json`
- `outputs/browser-audit.json`
- `outputs/overview.png`

The SVG must be nonblank, final, self-contained, and free of placeholders. Both validation reports must contain `"ok": true`. A successful process exit without those values does not satisfy the request.

Do not run another command, read, listing, or verification after the exact command. The evaluation harness independently checks the files and both required JSON `ok` fields. At the end, report the seven paths and that the exact command completed; do not claim that the browser report contents were printed. Keep `skills/compose-synchronized-svg/` unchanged.
