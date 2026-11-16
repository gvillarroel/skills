# Solid items and outlined groups

Use only the loaded read-only skill and normal local tools. Create `scene.html`
as a clean standalone explanatory SVG: a white outlined group containing three
small process boxes connected in sequence, plus a separate small data mark.
Use essential short labels only, with no visible heading or decorative panels.

Apply the current surface guidance through the shared runtime. Ordinary boxes
are solid gray without borders; the current box becomes solid primary red with
readable white internal text. The group keeps its white interior and discreet
outline. Keep the separate data mark's actual gray fill stable using an encoding
annotation. Preserve geometry and choose semantic item/group roles rather than
pixel size cutoffs or color-area quotas.

Expose a pure renderAt(seconds) and snapshot(). Show a different selected box
at times 0, 1 and 2, with the red guiding point beside the corresponding target.
No autonomous timer is needed for this three-state diagnostic. Use the bundled
standalone inspector to create `style-check.json` and `preview.png`. Correct real
text/stroke/guide or surface-style findings, then verify repeated seeking.

Write `decisions.json` explaining group versus item roles, internal text contrast,
the stable encoded mark, reusable helpers and verification limits. Do not claim
that this standalone diagnostic is a narrated or native-editor video.

Required outputs: scene.html, style-check.json, preview.png, decisions.json.
