# Connected JSON chart requests

Use this reference when authoring requests for the deterministic connected
`xy_render_chart` adapter, especially when the tool is absent from a constrained
workspace. This is the adapter's XY 0.0.8 subset, not arbitrary Python kwargs.
Prefer the actual tool's current capabilities when available and allowed.

Use `preset:"line"` with data x/y for a simple line, or `preset:"sankey"` with
ordered node labels and `[sourceLabel,targetLabel,value]` links. Presets do not
accept arbitrary top-level Python kwargs or chart components. For a line plus
objective, multiple marks or explicit axes/legend, use version 1:

```json
{
  "version":1,"factory":"chart","colorset":"colorset1",
  "title":"Synthetic hourly latency","width":800,"height":420,
  "marks":[
    {"kind":"line","args":[[0,1,2,3],[120,130,160,190]],"kwargs":{"name":"Observed","color":"$primary","width":2.5}},
    {"kind":"line","args":[[0,1,2,3],[150,150,150,150]],"kwargs":{"name":"150 ms objective","color":"$muted","dash":"dashed"}}
  ],
  "components":[
    {"kind":"x_axis","kwargs":{"label":"Hour (UTC)"}},
    {"kind":"y_axis","kwargs":{"label":"Latency (ms)"}},
    {"kind":"legend","kwargs":{"loc":"lower right"}}
  ]
}
```

Marks and components use `kind`, not `type`. A line is a mark, not a component.
Keep x/y arrays paired. The example uses the otherwise empty lower-right
region for its legend; inspect the actual chart before choosing that position
for different data. Preserve objective/observations and do not add invented data.

The connected adapter accepts declarative allowlisted construction, with no
arbitrary code execution, source URLs or filesystem paths. Colorset 1 is the
default; Colorset 2 requires explicit opt-in. A constructor name or method in
native XY does not automatically identify an adapter capability.

Check a finite line or label-based Sankey request with:

```sh
python <bundle>/scripts/check_connected_spec.py --spec request.json --report validation.json
```

This checker intentionally covers these focused recipes only. It is not the
full adapter schema or renderer. A passing check still needs the actual tool,
export inspection, and host UI tests for any corresponding claims.
