# Task

Create an original minimal explanatory video of a variable inlet filling a tank.
Use the available skill as a read-only resource. No other specialist skill is
installed in this workspace; use its standalone vector-asset fallback.

At 960 by 540, 12 fps for exactly 8 seconds, show a recognizable valve actuator,
connected inlet, reservoir and volume ruler, with a synchronized stored-volume
history. Use colorset1, sparse direct labels with units, no headline or cards.
The input rate is 2 L/s initially, ramps to 5 L/s from second 2 through second 4,
and stays there. Its preview domain is 0 through 5 L/s. The ideal tank starts
empty, has no outflow, constant cross-section and capacity 40 L. At second 8 it
contains 31 L; changing the rate control must recompute the entire accumulation
history. Transport tracers are optional, but any used must stop at zero and keep
a continuous phase when the rate changes.

First define an asset plan and produce an editable subject-specific SVG, then
assemble it with the skill's SVG importer. Give the rotating/moving part and the
stored fill actual state bindings. Explain the actual asset-production choice
and its purpose in the plan; do not claim another skill was invoked. Native
plot geometry may overlay the imported art. Run import, build, bundled browser
audit, native HyperFrames check, render and full media verification. Inspect the
composed still and final movie contact sheet and repair actual findings.

Create exactly these required artifacts (additional working files are allowed):

- `deliverables/scene.json`: the unexpanded numerical scene brief.
- `deliverables/asset-plan.json`: asset plan with actual producer, moments and hooks.
- `deliverables/assets/mechanism.svg`: original editable mechanical illustration.
- `deliverables/assembled.json`: imported and state-bound scene.
- `deliverables/import.json`: successful import report.
- `deliverables/project/index.html` and `deliverables/project/preview.html`.
- `deliverables/project/manifest.json`: retained original SVG and asset provenance.
- `deliverables/audit.json` and `deliverables/preview.png`: passing composed-scene browser audit.
- `deliverables/explanation.mp4`: the exact video.
- `deliverables/media.json` and `deliverables/contact.jpg`: passing full movie verification.

Keep all commands and output paths relative to the task workspace root. Expected
authoring findings have exit zero: inspect the JSON's `ok` before proceeding.
Do not change the skill or read acceptance fixtures. Put any package cache inside
the generated project. Report what each asset contributes and any real limitation.
