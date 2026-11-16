# Qualitative color hierarchy

Use only the loaded read-only skill and normal local tools. Create a clean
explanatory reading frame at `figure.html` for five independent sensor entities
measured over time, including two crossing lines. Use synthetic data and disclose
that in `decisions.json`. Expose a deterministic renderAt(seconds) and snapshot().

Apply the skill's composition direction: predominantly white in overall visual
character, grayscale structure and readable context, selective primary-red
attention. These are qualitative design choices, not pixel quotas or background
proportions. The five independent entities need stable distinct identities;
use appropriate bundled colorset2 hues for their lines and essential legend.
Keep the main attention point primary red and beside its current target.
Use only essential labels, values and units; no visible title or decorative cards.

Validate the reading frame with the bundled standalone focus inspector at
times 0, 1 and 2, writing `focus-check.json` and `preview.png`. Correct actual
label/stroke/guide issues if found. Record the color mapping, why the extra
entity colors are useful, how white/gray/red visual hierarchy is expressed,
and the verification limits in `decisions.json`. Do not invent numerical color
pass thresholds or claim a native video export for this static diagnostic.

Required outputs: figure.html, decisions.json, focus-check.json, preview.png.
