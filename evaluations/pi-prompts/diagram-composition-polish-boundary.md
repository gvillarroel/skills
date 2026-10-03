Use diagram-composition to repair and combine two small imported SVG views.
Both show the same Source object and must use blue #276bc8 consistently. The
first view's upstream line is an undirected connection entering Source from the
left. Preserve it, but make the line meet the box cleanly. The second view has
the same object with a descriptive label. Keep all text and the Source identity.
These SVGs are editable input material; save them in the workspace first:

First view:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
<rect x="80" y="60" width="260" height="120" rx="8" fill="#e99a88" stroke="#276bc8" stroke-width="2.4"/>
<text x="110" y="115" font-size="20" fill="#cbd3da">Source</text>
<path d="M10 90H200" fill="none" stroke="#555d66" stroke-width="2"/>
</svg>

Second view:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
<rect x="80" y="60" width="260" height="120" rx="8" fill="#f5f7f9" stroke="#9e1b32" stroke-width="2.4"/>
<text x="110" y="115" font-size="20" fill="#26323d">Source</text>
<text x="110" y="148" font-size="16" fill="#536575">Shared reference</text>
</svg>

Arrange the views side by side on a 1000 by 460 canvas, displayed at 1000px with
labels at least 14px. Add one undirected identity connection between their Source
objects. Keep it distinct from the supplied upstream connection. Preserve the
original inputs and deliver repaired editable panels in out/panels/ plus exactly
out/plan.json, out/figure.svg, out/report.json, out/audit.json, out/preview.png,
and out/review.md. Verify the result. Document the repairs and any limitations.
The loaded skills/diagram-composition/ directory is read-only. Keep generated
files inside this workspace. Do not read other skills, use the network, or
install tools.
