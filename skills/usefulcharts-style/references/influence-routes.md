# Short influence routes across institutional stories

Use this refinement of `usefulcharts-branching-lineage` when dotted influence paths take large loops around nearby institutions. Preserve solid descent or merger paths from source bottom to target top. An influence may leave or enter a side when that makes its distinct meaning and direction clearer.

## Compose the institutions first

Resolve the page before routing. If the brief used `layout: auto` or `layout: packed`, copy the measured node centers and widths from `layout.json`'s `resolved_layout.nodes`, retain all existing node fields, set the reported canvas dimensions and actual type sizes, and remove `layout`. Inspect this authored version before refining its paths. The helper rejects relative or automatic coordinates because absolute bends would otherwise become stale.

Keep every institution, date, category and relationship. Later traditions can expand beside earlier stories that terminate. Put the two predecessors of a merger near its successor. Source chronology provides a placement preference; a schematic page does not imply a proportional year axis. Move a local group when a proposed influence must cross several unrelated stories.

## Select attachments and corridors

For a simple manual repair, set an influence's `source_port` and `target_port` to `left`, `right`, `top` or `bottom`. Side positions are the center of the complete name/date/caption envelope. Reserve at least 18 units of open space immediately outside each attachment. An optional `via` array declares absolute orthogonal bends. Let the arrow point into the target side; the renderer does this automatically.

For several interacting influences, run:

```sh
uv run --script <skill-dir>/scripts/route_influences.py authored.json --output routed.json --report routing.json
uv run --script <skill-dir>/scripts/render_chart.py routed.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source routed.json --report browser.json --png poster.png
```

The helper compares four side-pair choices and the ordinary bottom/top choice. It measures length, bends and proper crossings against existing paths, while reserving complete node, family-label and inset rectangles. It freezes the resulting corridors in the editable brief so rendering order cannot silently change the proposal. Explicit influence ports or corridors are preserved unless `--replace-authored` is requested. Coordinates and facts stay unchanged. Review the returned JSON and final preview; the local cost is not an aesthetic score or proof of an optimal route.

Newly composed influences also reserve straight runs belonging to unrelated edges. The browser audit independently reports visible `unrelated-shared-run` warnings, including in preserved authored corridors. Review and repair unintended shared strokes; a geometry pass alone does not rule out a misleading junction. See [branch structure](branch-structure.md) when rerouting exposes a deeper arrangement problem.

## Inspect actual reading

Trace the longest influence from its named source to its arrowhead, then trace both branches of the busiest merger. Check the side attachment at reading scale and the complete poster at the same display width as the prior version. Dotted arrows should remain subordinate to the solid institutional history. Keep the category meaning unchanged through a merger.

Count actual rendered crossings only as a diagnostic. A crossing proxy from a placement solver can improve while the final router gets worse. A smaller canvas can shorten absolute paths while increasing bends or intersections; normalize comparisons to equal display width and inspect the result. Shared short endpoint segments are not automatically unrelated merged trunks. Do not promote a layout just because packing or browser geometry passes.

If the helper finds no clear attachment, move the specific neighboring institution or author the corridor. Repeatedly increasing the search bounds cannot fix a port inside another content envelope. The browser audit rejects detached or incorrectly declared ports and paths through any entity. Keep the full source and report any remaining visual mismatch.
