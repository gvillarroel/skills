Use the Line World Video skill to create an editable starter at exactly `film/`.
Keep `skills/line-world-video/` read-only. Use only this skill and normal local
tools; do not inspect other skills, repository files, global configuration or
acceptance examples. Do not render a movie or install npm packages for this test.

Run this command from the workspace root:

```text
uv run --script skills/line-world-video/scripts/line_world.py init --project film
```

Deliver `film/index.html`, `film/preview.html`, `film/story.json`, `film/timing.json`
and `film/selection.json`. Check that all seven beat boundaries are contiguous,
the total duration is 56 seconds, and every row has a reading window. Write
`check.json` with the observed duration, row count, palette and pass boolean.
