First action: read this prompt at `../prompt.md`. Then run the exact command below once. After it exits successfully, read only `projects/metro-text-dependence-validation/artifacts/reviews/metro-audit-fixtures.json`, report whether `passed` is true, and stop. Do not list directories, do not run manual file-existence checks, do not read helper source, do not read audit source, do not rerun after a passing command, do not ask questions, and do not stop before the command finishes.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/validate_metro_audit_fixtures.py --output projects/metro-text-dependence-validation/artifacts/reviews/metro-audit-fixtures.json --no-install-browser --timeout-seconds 60
```

Task: validate the Metro audit fixture suite after tightening text-dependence and design-adherence gates.

The output report must pass and include these negative text-dependence fixture cases:

- `rendered-title-band-text-fails`
- `rendered-text-area-fails`
- `rendered-dominant-text-box-fails`
- `rendered-mark-to-text-density-fails`

Required exact output:

- `projects/metro-text-dependence-validation/artifacts/reviews/metro-audit-fixtures.json`
