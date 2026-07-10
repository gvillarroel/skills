# Isolated Metro Pattern Smoke Validation

Read `../prompt.md` first. Then run the exact command below from the current workspace root. Do not inspect script source. Do not read `assets/examples`. Use a shell timeout of at least 600 seconds.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/validate_metro_pattern_smoke.py --output projects/metro-pattern-smoke-runtime/artifacts/reviews/pattern-smoke.json --workdir projects/metro-pattern-smoke-runtime/artifacts/reviews/pattern-smoke-work --patterns scenario-tree --no-install-browser --timeout-seconds 180 --masonry-layout
```

Required exact outputs:

- `projects/metro-pattern-smoke-runtime/artifacts/reviews/pattern-smoke.json`

The output JSON must pass and prove the Metro design contract:

- `passed` is `true`
- `aggregateMetrics.failedPatternCount` is `0`
- `aggregateMetrics.maxRenderedInternalPaddingPx` is `0.0`
- `aggregateMetrics.totalZeroPaddingGeometryViolationCount` is `0`
- `aggregateMetrics.totalUntaggedInsetRectViolationCount` is `0`
- `aggregateMetrics.maxMasonryTextElementCount` is `0.0`
- `aggregateMetrics.maxMasonryTextCharacterCount` is `0.0`
