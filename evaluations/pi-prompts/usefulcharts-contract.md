Use the usefulcharts-style skill to render its small starter brief as an editable educational poster. Treat `skills/usefulcharts-style/` as read-only. Work only in this isolated workspace; do not inspect parent directories or other skills. The template's invented dataset is suitable for this command-contract case.

Create these exact nonempty outputs: `deliverables/chart.svg`, `deliverables/chart.html`, and `deliverables/layout.json`. Preserve all source nodes and typed edges. Keep the synthetic-data note visible.

Run this command exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py skills/usefulcharts-style/assets/templates/starter.json --svg deliverables/chart.svg --html deliverables/chart.html --report deliverables/layout.json
```

Inspect the output inventory and layout report. Do not install browsers for this contract case; an independent evaluator will render the SVG. This is an isolated artifact task: do not run Git commands or inspect repository status. Briefly state the outcome and distinguish preflight validation from visual inspection.
