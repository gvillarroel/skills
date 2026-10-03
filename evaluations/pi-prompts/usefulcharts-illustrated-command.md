Use the loaded usefulcharts-style skill for a deterministic evaluator contract. This is not a visual-quality test; do not declare that you saw real poster images.

Run the bundled evaluator's boundary suite with this exact command:

```sh
uv run --script skills/usefulcharts-style/scripts/test_illustrated_review.py
```

Then create deliverables/result.json containing schema_version: 1, boundary_suite_pass: true only if all tests passed, and visual_quality_reviewed: false. Create deliverables/review.md describing the helper's actual scope and at least two failure cases exercised by the suite. Keep the skill unchanged. Use only the specific runtime resources needed for this command contract. These exact output paths are required.
