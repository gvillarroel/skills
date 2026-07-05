# HTML Video Metro Pattern Smoke Quick Command

Use the loaded `html-d3-anime-video-workflow` skill as an executable tool bundle.

Read `../prompt.md` first. Then run this exact command from the isolated workspace. Run it verbatim, with no path substitutions, no placeholder project IDs, and no script-source inspection before the command:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/validate_metro_pattern_smoke.py --patterns dependency-map,evidence-ladder --output projects/metro-pattern-smoke-quick/artifacts/reviews/metro-pattern-smoke.json --workdir projects/metro-pattern-smoke-quick/artifacts/reviews/metro-pattern-smoke-work --no-install-browser --timeout-seconds 180
```

Required exact outputs:

- `projects/metro-pattern-smoke-quick/artifacts/reviews/metro-pattern-smoke.json`

After the command finishes, verify the JSON report has `passed: true`, `patternCount: 2`, and an empty `failedPatterns` list. Do not modify the copied skill directory. Do not answer with a generic command template; the exact output path above must exist.
