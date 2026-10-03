# Dense task overlap transparency — 2026-10-03

The scoped transparency change passes independent browser, pixel, SVG delivery
and data-preservation checks. The nine scope regions now use their existing
saturated colorset tokens at alpha `0.28`, declare semantic opacity and have no
decorative stroke. Their intersections reveal shared set membership. Task
dots and external label faces remain opaque; labels use maximum-contrast black
or white against their actual composited backings.

The retained opaque baseline has 18 alpha/declaration findings. The final CS1
fixture passes 12 states: desktop/mobile, normal/reduced motion, initial settled
rendering and two replays. Four helper-exported SVG states and four SVG states
from the production `render_d3_svg.py` route also pass. Actual single/double/
triple intersection pixels differ from the source-over model by at most
0.7456 channel units. Minimum measured text contrast is 11.9083:1.

All 1,308 per-state set/task geometry, membership and leader records match the
baseline. Regenerating the standalone layout outside the skill bundle matches
the published layout byte-for-byte. Five negative controls are rejected; an
ordinary unmarked filled rectangle still becomes opaque while all nine
declared set regions retain alpha `0.28`.

The shared-file treemap regression passes 12 CS1 states and 144 exact node
comparisons. Its renderer is unchanged after line-ending normalization. The
previous [36-state treemap report](treemap-tones-visual-20261003.json) remains
bound to its original gallery hash. A single desktop CS2 smoke state also
passes for the shared overlap renderer.

An inherited fixture limitation remains: the bottom summary caption contacts
the T095 task label. It exists before and after the transparency change and is
visible in the production SVG. This pass preserves original task/label
geometry; it does not claim that every SVG text pair is collision-free. The
generated collision counts describe the task-label model. Baseline and final
screenshot pointers are:

- `projects/task-overlap-transparency/artifacts/baseline/overlap-1440-normal-0-card.png`
- `projects/task-overlap-transparency/artifacts/final-cs1/overlap-1440-normal-0-card.png`
- `projects/task-overlap-transparency/artifacts/production-export/dense-overlap.png`

The [durable JSON report](task-overlap-transparency-visual-20261003.json) records
exact commands, source and artifact hashes, computed paint, negative controls,
manual review, retained scanner-development failures and scope limits. Bulky
captures and the frozen baseline remain in ignored project artifacts. The
canonical runtime remained frozen throughout final verification.
