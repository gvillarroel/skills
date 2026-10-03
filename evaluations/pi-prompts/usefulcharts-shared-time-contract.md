Read this prompt first. Treat `skills/usefulcharts-style/` as read-only. Work only
inside this isolated workspace; do not use the network or discover other skills.

This is a deterministic command-contract check for measured calendar labels.
Write `measured.json` with the exact object below, execute exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/pack_shared_rows.py measured.json --output deliverables/layout.json
```

Then write a short English explanation to `deliverables/review.md`. Explain
which entities share a track and how time coordinates are preserved. Do not
render a chart in this packing-only check.

```json
{"mode":"numeric","width":900,"top":80,"gap":12,"track_gap":10,"row_gap":24,"compact_groups":true,"groups":[{"id":"survey","members":["alpha","beta","alpha-return"],"header_height":40,"label_width":160},{"id":"cargo","members":["gamma"],"header_height":40,"label_width":150}],"records":[{"id":"alpha","owner":"alpha","x0":100,"x1":240,"height":80},{"id":"beta","owner":"beta","x0":180,"x1":320,"height":80},{"id":"alpha-return","owner":"alpha","x0":380,"x1":500,"height":80},{"id":"gamma","owner":"gamma","x0":550,"x1":750,"height":80}]}
```
