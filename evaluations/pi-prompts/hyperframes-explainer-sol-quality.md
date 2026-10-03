# Task

Create an original minimal explanatory video of a valve controlling the inlet
of a constant-area tank, with useful mechanical detail and synchronized motion.
Use the supplied skill as a read-only resource. No companion skill is installed;
choose its available standalone production resources and record the actual
producer. Do not read other runs or acceptance fixtures.

Deliver exactly 16 seconds at 1920 × 1080, 30 fps, using colorset1. The flow is
2 L/s initially, ramps to 5 L/s from t=4 through t=6, stays at 5 until t=10,
ramps to 1 L/s from t=10 through t=12, then stays at 1. The preview control domain
is 0 through 5 L/s. The tank starts empty, has no outflow, a constant cross-section
and capacity 80 L. Its actual analytic volume reaches 45 L at t=16.

Show a recognizable valve housing and actuator, a visible changing gate, connected
inlet transport, a calibrated reservoir cutaway with a graduated capacity ruler,
and both flow-rate and volume histories on fixed scales. Transport must follow
the integrated flow, remain continuous through ramps and stop at zero flow.
The initiating action, transport, filling speed and history slopes must explain
the same events. Use neutral mechanics, a consistent red quantity identity,
short direct values/units, no headline, no cards and no on-stage controls.

Create an editable SVG and asset plan with actual state hooks, native bounds,
ports, event moments and provenance. Run the skill's applicable import, build,
browser audit, native check, render and complete media validation. Inspect the
composed still and contact sheet, and repair actual findings before delivery.
Preview controls must recompute the full histories at zero/maximum input, reset
to the original events and support backward/forward seeks.

Create these exact artifacts; additional working files are allowed:

- `deliverables/scene.json` and `deliverables/asset-plan.json`.
- `deliverables/assets/mechanism.svg` and `deliverables/assembled.json`.
- `deliverables/import.json`.
- `deliverables/project/index.html`, `deliverables/project/preview.html` and
  `deliverables/project/manifest.json`.
- `deliverables/audit.json` and `deliverables/preview.png`.
- `deliverables/explanation.mp4`, `deliverables/media.json` and `deliverables/contact.jpg`.

Keep generated files and package caches outside the copied skill and inside this
workspace. Preserve every supplied fact, exact path and source quantity. Report
the explanatory purpose of the assets and the model's actual limitations.
