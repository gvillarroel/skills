# Task

Create a minimal HyperFrames explanation of a vehicle changing speed. At 960 by
540, 12 fps for exactly 8 seconds, show a recognizable original vector vehicle
on a distance ruler, a velocity indication and synchronized distance history.
Speed begins at 2 m/s, ramps to 4 m/s from second 2 through second 4, and stays
there. The interactive speed domain is 0 through 6 m/s. The vehicle starts at
zero distance. Its travelled distance is the actual integral of speed, with a
fixed ruler/history domain of 0 through 48 m.

Use colorset2 explicitly: red identifies speed and blue identifies position and
travelled distance. Keep mechanical context neutral, labels sparse and direct,
and put no headline, title card or controls in the film. Use stable geometry and
one shared clock. A change in speed must affect visible motion and history slope
together. The vehicle must have enough structural features to be recognizable
and its position must agree with the ruler. Any wheel rotation must reflect
travelled distance, not an unrelated loop.

Keep `skills/hyperframes-explainer/` read-only. No other specialist skill is
installed here; select and document the standalone asset-production fallback
appropriate to this moment. Provide an asset plan and an editable SVG with actual
state hooks and retained provenance, and create these exact required artifacts:

- `deliverables/scene.json` and `deliverables/asset-plan.json`.
- `deliverables/assets/mechanism.svg` and `deliverables/assembled.json`.
- `deliverables/import.json`.
- `deliverables/project/index.html`, `deliverables/project/preview.html` and
  `deliverables/project/manifest.json`.
- `deliverables/audit.json` and `deliverables/preview.png`.
- `deliverables/explanation.mp4`, `deliverables/media.json` and `deliverables/contact.jpg`.

Run the applicable skill validation and inspect the actual composed preview and
movie contact sheet. Correct findings before delivery. Preview controls must
actually update the mechanism and reconstruct its history, including zero speed
and a reset. Keep working files and package caches in this workspace outside the
skill. Report what the assets explain and any actual limitations.
