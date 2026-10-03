# Calibrated Composition Command Contract

Use `skills/hyperframes-explainer/` as a read-only resource. Create an inlet
composition at 1280 × 720, 12 fps and 8 seconds, using colorset1. The flow starts
at 1 L/s, ramps to 2 L/s from t=2 through t=4 and remains there. Its domain is
0 through 3 L/s; accumulation starts at zero with no outflow and capacity 24 L.
Create the exact numerical model, editable calibrated SVG, asset plan and
imported scene. Rendering a movie is not part of this command smoke.

Read the skill and relevant guidance, then run each command below verbatim in a
separate tool call. Inspect its report's `ok` before proceeding:

```bash
uv run --script skills/hyperframes-explainer/scripts/explainer.py init --brief deliverables/model.json --report deliverables/init.json --width 1280 --height 720 --fps 12 --duration 8 --initial 1 --maximum 3 --target 2 --at 2 --ramp 2 --source rate --source-unit L/s --quantity volume --quantity-unit L
```

```bash
uv run --script skills/hyperframes-explainer/scripts/compose_mechanism.py --brief deliverables/model.json --output deliverables/scene.json --svg deliverables/assets/mechanism.svg --plan deliverables/asset-plan.json --kind inlet --capacity 24 --report deliverables/composition.json
```

```bash
uv run --script skills/hyperframes-explainer/scripts/import_assets.py --brief deliverables/scene.json --plan deliverables/asset-plan.json --output deliverables/assembled.json --report deliverables/import.json
```

The seven required artifacts are `deliverables/model.json`,
`deliverables/scene.json`, `deliverables/assets/mechanism.svg`,
`deliverables/asset-plan.json`, `deliverables/composition.json`,
`deliverables/assembled.json` and `deliverables/import.json`. Keep all outputs
and caches in the workspace outside the skill. Preserve the model facts, use
three complementary views and record the actual bundled producer.
