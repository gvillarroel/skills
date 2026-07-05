Read `../prompt.md` first. Then run this exact command once, without reading script source files first:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/plan_metro_pattern_mix.py --prompt-file ../prompt.md --output projects/metro-pattern-mix-validation/artifacts/reviews/pattern-mix.json --require-anchor LLM --require-anchor MCP --require-anchor agent
```

After the command finishes, read only `projects/metro-pattern-mix-validation/artifacts/reviews/pattern-mix.json` and report whether it passed.

Required exact output:

- `projects/metro-pattern-mix-validation/artifacts/reviews/pattern-mix.json`

Task source:

Create a Metro Minimal Tonal Motion pattern-mix plan for a low-text visual explainer suite about LLM behavior, MCP tool integration, and agent execution. The plan must not start from labeled cards or title bands. It must use colorset1, square 0-radius geometry, zero internal padding, and multiple gray hierarchy levels. The result should name enough visual-density patterns, functional zones, motion systems, camera movement, transition contracts, and anti-pattern risks to prevent a boxes-plus-labels scaffold.

Required anchors:

- LLM
- MCP
- agent
