# Reusable line world patterns

These runtime recipes work without the acceptance movie or another skill.

| Pattern ID | Trigger and input contract | Construction and validation |
| --- | --- | --- |
| line-world-balanced-frame | Clean presentation without requested titles | Use essential labels and values only; center meaningful geometry and give paired views comparable visual weight. Recompose the overview as a compact two-by-two world. Check useful bounds, breathing room and visual balance at rest, rather than retaining an empty headline strip. Only explicit short entries in `presentation.contextLabels` appear as context. |
| line-world-guided-relations | Explain relationships among a few named objects; stable entity IDs | Precompute endpoints; draw thin connections; move one red dot along actual paths; reveal labels after landing. Seek backward/forward and check deterministic endpoint identity. |
| line-world-camera-handoff | Move between related visual islands in one larger space | Keep world coordinates fixed. Interpolate camera translation/scale from the same clock; lead with the dot and settle before reading. Audit midpoint and final target bounds. Preview drag offsets never enter capture. |
| line-world-table-focus | Compare exact paired values for 2–8 rows, with units and stable IDs | Table left, fixed-domain paired marks right. One row focus event updates row line, mark, annotation and dot. Check every selected pair against source data and chart pixel lengths. |
| line-world-linked-history | Relate entities to equal-length observations over time | Hold a shared x/y domain; reveal paths deterministically, directly label selected endpoint, retain row identity. Verify dates or use a truthful observation-index label; preserve missing-data semantics when extending. |
| line-world-category-expansion | Simultaneous categories need additional hue | Declare colorset2 and its reason; preserve the red guide and map new hues only to category identities. Validate computed paint against bundled tokens; the colorset1 edition retains labels/shapes. |

Run `render_line_world.py --audit-only` on the generated project for browser,
data, palette, determinism and screenshot evidence. For a new geometry form,
extend the project-specific bounds/semantic checks rather than claiming the
starter's audit covers arbitrary custom SVG.
