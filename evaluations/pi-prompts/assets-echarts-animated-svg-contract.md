Copy the bundled static-bar-chart.svg template to input.svg, then execute
this exact command:

Run the fenced command as its own shell call, separate from copying or validation.

```bash
uv run --script skills/echarts-animated-svg/scripts/animate_echarts_svg.py input.svg --chart-type bar --output output.svg
```

Validate the pair and write validation.json with the bundled validator.
Treat skills/echarts-animated-svg/ as read-only. Write all task files in the
current workspace. Use local tools without network access or other repositories.
