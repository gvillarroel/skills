# Native footer legend contract

The single predeclared attempt `20261024-reflex-xy-footer-legend-contract-sol-1`
passed its strict harness, independent source/data/native-layout checks, trace
audit, and manual SVG/HTML screenshot review on 2026-10-24. The model was
`openai-codex/gpt-5.6-sol`, retaining the recorded Spark exception. Both the
18-file isolated copied payload and the 18-file canonical runtime remained
unchanged at final digest
`7c045720cd6a24dcab11bcafc57a310868da8093686083a179a2653a75ba360a`.
This is a scoped result, separate from earlier subjects; the skill remains
`validating`.

The command was `uv run --script projects/reflex-xy/scripts/run_footer_legend_pi.py`.
It invoked the normal isolated runtime harness with JSON strict mode, the named
model, and all ten exact `--expect-output` paths. The task prompt is
[`reflex-xy-capabilities-footer-legend.md`](../pi-prompts/reflex-xy-capabilities-footer-legend.md).
The one-attempt runner refuses to replace retained evidence. No retries, task
repairs, waivers, or source edits followed the run.

Independent acceptance used
`uv run --script projects/reflex-xy/scripts/verify_footer_legend_pi.py`.
It replayed the editable PEP 723 source pinned to `xy==0.0.8`, confirmed the
original ordered observations and series/category names, and inspected the
actual exported XY traces. Each palette retains all twelve supplied line
vertices and all twelve correctly grouped bar values. Each family's paired
variants have identical native geometry, dimensions, labels, and footer layout,
with exact canonical authored paints and visibly distinct category colors.

The agent adapted the native recipe to a 960 × 600 figure with
`padding=(48,32,150,72)` and `xy.legend(loc="upper left", anchor=(0,-0.24),
ncols=2|3, style=...)`. Native bounding-box checks confirmed every legend name
and adjacent color key lies inside the exported figure, below the plot and
x-axis title, separate from the synthetic note, and without legend-label
collisions. Manual review covered all four native SVG renderings and all four
desktop HTML screenshots: the two high right-hand line endpoints and all bars
remain fully visible; axes, series names, and legend keys are readable. Offline
browser checks found no external requests or JavaScript errors. The fixed
960-pixel HTML width requires horizontal scrolling at 390 pixels, which the
focused prompt explicitly permitted. Notes accurately describe the fictional
data, footer layout, performed checks, and fixed-snapshot Python callback limits.
Original Pi artifact hashes remained unchanged.

The independent trace audit reconciled all 27 actual tool calls with their
completion records and found zero tool errors or policy findings. The required
model and prompt hash match; all copied and canonical runtime hashes and sizes
were independently verified. No ambient repository, acceptance example, sibling
skill, hidden parent traversal, or absolute source reads were found.

Raw run evidence is under
`evaluations/runs/20261024-reflex-xy-footer-legend-contract-sol-1/`.
The frozen plan and snapshots, strict harness result, independent source/data
check, native legend and axis bounding boxes, source replay, trace audit, manual
review, screenshots, and summary are under
`projects/reflex-xy/artifacts/footer-legend-pi/`.
