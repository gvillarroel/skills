# Calibrated Mechanism Composition

Use the bundled composer when the actual explanation matches one of these
mechanisms. It supplies editable original artwork and exact state hooks, keeping
the art direction reproducible without requiring a companion skill.

## Contents

- [Preserve the supplied facts](#preserve-the-supplied-facts)
- [Compose, inspect, import](#compose-inspect-import)
- [Editable assets and causal meaning](#editable-assets-and-causal-meaning)
- [Quality and delivery](#quality-and-delivery)

| Kind | Required model | What the composition explains |
| --- | --- | --- |
| `inlet` | One nonnegative L/s source and its analytic integral from zero in L; constant cross-section and no outflow/losses | Visible valve opening, connected transport, calibrated reservoir fill, input-rate history and accumulated-volume history |
| `vehicle` | One nonnegative m/s source and its analytic integral from zero in m | Recognizable moving vehicle, actual wheel/road contact, clockwise distance-based rolling, distance ruler, velocity indication and both histories |

Prefer this composer for a matching rate/integral explanation instead of drawing
a weaker schematic from scratch. Use selected specialist skills or custom SVG
for other subjects, conservation, outflow, negative inputs or spatial claims.
Never relabel an inlet as another mechanism merely to use the helper.

## Preserve the supplied facts

Initialize a project-owned numerical model with `explainer.py init`, using the
requested dimensions, frame rate, duration, values, units, control domain and
event timing. Write it to a working file such as `model.json`; the composer
creates the requested final unexpanded scene separately. For extra events, edit
the model with parsed JSON before composition. Preserve every event.

The quantity expression must be `{"integrate":["<source>","time"]}`. The helper
preserves sources, derived expressions, events, output, palette and invariants.
It replaces only the illustrative layout and marks. Use an even landscape
canvas of at least 960 × 540. Smaller or portrait work needs a custom layout.

## Compose, inspect, import

Substitute the actual bundle and exact requested paths. Run one gate per call
and inspect its `ok` before proceeding:

```text
uv run --script <skill-root>/scripts/explainer.py init --brief model.json --report init.json --width 960 --height 540 --fps 12 --duration 8 --initial 2 --maximum 5 --target 5 --at 2 --ramp 2 --source rate --source-unit L/s --quantity volume --quantity-unit L
uv run --script <skill-root>/scripts/compose_mechanism.py --brief model.json --output scene.json --svg assets/mechanism.svg --plan asset-plan.json --kind inlet --capacity 40 --report composition.json
uv run --script <skill-root>/scripts/import_assets.py --brief scene.json --plan asset-plan.json --output assembled.json --report import.json
uv run --script <skill-root>/scripts/explainer.py build --brief assembled.json --project project --report build.json
```

For the vehicle, initialize `speed` in m/s and `distance` in m using the real
values/domain/events. Add `--palette colorset2` only when requested or justified.
Use `--kind vehicle` and omit `--capacity`. The ruler/history cover maximum speed
× duration and the full vehicle fits at that maximum. An inlet's `--capacity`
must cover maximum flow × duration; if omitted, that product is used. Reject an
undersized capacity rather than clamping overflow or changing the control domain.

The helper infers the sole source and its integral; select ambiguous quantity
IDs with `--source` and `--quantity`. Optional `--source-label` and
`--quantity-label` change short direct labels. Outputs must be distinct from the
input model and must not already exist. Preserve generated files for editing;
use fresh paths to compose another variant. Do not run the blank SVG scaffold
for this route: the composer creates the complete SVG and plan itself.

The optional `--palette` flag only asserts the palette already selected in the
input model; it cannot change that selection. Set an explicit second palette
during initialization or a parsed model edit. Inspect the build report's `next`
and install dependencies before invoking the browser/native scripts.

## Editable assets and causal meaning

The plan names the actual bundled producer, event moments, native bounds, ports
and bindings. It does not claim an unavailable specialist was invoked. SVG IDs
identify actuator, gate, fluid, waterline, tracers, wheels, road, ruler and values.
Edit these project-owned IDs with an XML/JSON parser when necessary, then reimport
and rebuild with `--refresh`.

Inlet tracer phase follows accumulated volume, stays continuous through ramps
and stops at zero flow. Tracers indicate transport qualitatively. Valve geometry
illustrates a control, not a measured hydraulic law. Fill uses the same
zero/capacity edges as the actual graduated ruler. Vehicle position uses the
rear wheel centre as the distance anchor; its pointer/ruler share that origin,
and wheel rotation is travelled pixel distance divided by radius.

Repeated flow markers advance at most one quarter of their spacing per frame at
the legal maximum input. The phase remains proportional to accumulated volume;
its fixed scale also respects the requested fps, avoiding apparent reverse flow
at low frame rates. Record that pacing in `composition.calibration` and verify
actual consecutive frame geometry, not only widely separated event stills.

`composition.calibration` records these contracts outside the film. One dominant
mechanism and two complementary fixed-domain histories use direct values/units,
neutral mechanical context and no headline/cards. Colorset1 remains the default;
colorset2 paints input red and quantity blue only when selected in the model.
One canonical state and seekable clock drive all geometry.

## Quality and delivery

Inspect the composed still before encoding. Run the browser audit, native
HyperFrames check, exact render and full media verification in the main workflow.
Inspect event onset/midpoint, final hold, zero/max controls and reverse seeks.
Calibrated geometry still requires real label, contact, overlap and motion review.

Maintainer validation:

```text
uv run --script <skill-root>/scripts/test_composition.py --work-dir artifacts/composition-tests
```
