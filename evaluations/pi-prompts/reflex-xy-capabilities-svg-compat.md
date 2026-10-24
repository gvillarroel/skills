Use the loaded skill's narrow native SVG compatibility helper for a command
contract. Keep the original evidence unchanged. First create exact path
`results/original.svg` with these bytes, including the final newline:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="160" height="100" viewBox="0 0 160 100"><title>Line symbol evidence</title><path d="M 20 30 L 40 50" fill="none" fill="#9e1b32" stroke="#9e1b32" stroke-width="2"/><circle cx="100" cy="50" r="8" fill="#007298"/></svg>
```

The duplicate fill attribute is the known input defect, so the original is not
valid XML. Run this command exactly from the workspace root:

```bash
uv run --script skills/reflex-xy/scripts/xy_svg_compat.py --input results/original.svg --output results/repaired.svg > results/repair.json
```

Deliver exact paths `results/original.svg`, `results/repaired.svg`, and
`results/repair.json`. Check that the repaired SVG is valid XML, has one path
with no fill and the same stroke/geometry, and preserves the circle and title.
The report must state one repaired path and valid SVG XML. Keep the original
malformed input; do not overwrite it or expand the repair to unrelated shapes.

Treat `skills/reflex-xy/` as read-only. Write generated files only in this
workspace outside `skills/`. Do not read acceptance examples, other skills,
parent directories, or repository documentation. Do not publish or deploy.
