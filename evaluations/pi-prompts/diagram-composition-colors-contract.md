Use diagram-composition to verify its shared-color workflow on a small two-panel
figure. The left panel is an unordered hub: an Archive is connected directly to
Grains and Legumes. The right panel is a matrix with the columns Collection and
Container: Grains uses jars, Legumes uses envelopes. There is no process or
chronological order. The same Grains concept must use #276bc8 in both panels;
Legumes must use #9e1b32 in both. Essential text stays dark. Use 1200 by 500,
displayed at 1200px, minimum text 14px. Use one row and two equal grid columns.

Author out/brief.json with native hub and matrix objects, canonical concepts with
colors, and concept bindings. Use the bundled build_panels.py to create
out/plan.json and editable SVGs in out/panels/, then compose_diagram.py to create
out/figure.svg and out/report.json. Run the bundled browser audit to create
out/audit.json and out/preview.png. Inspect its screenshot and finish with a final
audit without --inspect. Provide out/review.md describing the two forms and
verified palette coverage. If a draft finding occurs, repair the source brief
and regenerate your own outputs with --overwrite.

The loaded skills/diagram-composition/ directory is read-only. Keep generated
files inside this workspace. Do not read other skills, use the network, or
install tools. All inputs are supplied here.
