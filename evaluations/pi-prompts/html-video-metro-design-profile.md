First action: read this prompt at `../prompt.md`. Then run the exact command below from the isolated workspace root. Do not list directories, do not inspect script source, do not ask questions, and do not write into the copied skill directory.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/validate_metro_design_profile.py --output projects/metro-design-profile-runtime/artifacts/reviews/design-profile-validation.json
```

Required exact output:

- `projects/metro-design-profile-runtime/artifacts/reviews/design-profile-validation.json`

After the command finishes, read only the required JSON report. Report whether `passed` is true and stop.
