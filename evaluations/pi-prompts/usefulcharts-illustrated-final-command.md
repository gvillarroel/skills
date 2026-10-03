Use the loaded usefulcharts-style skill for a deterministic evaluator contract. This is not a visual-quality test; do not declare that you saw real poster images.

Run these exact commands. The first checks review evidence gates. The second checks panel semantics and the nested-SVG export and clipping boundaries:

```sh
uv run --script skills/usefulcharts-style/scripts/test_illustrated_review.py
```

```sh
uv run --script skills/usefulcharts-style/scripts/test_panel_poster.py
```

Then create deliverables/result.json containing schema_version: 1, boundary_suite_pass: true only if both suites passed, and visual_quality_reviewed: false. Create deliverables/review.md describing the evaluator's actual scope and the distinction between viewport geometry and image-content bounds. Keep the skill unchanged. Use only the specific runtime resources needed for this command contract. These exact output paths are required.
