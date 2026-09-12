# Select distinct illustrative emblems

Use this guide when a poster repeats small category symbols or a requested object must be recognizable in a 29–50-unit image panel. These bundled devices are original illustrations, not authentic institutional logos. For a factual identity that depends on a particular seal, crest or portrait, use the correct sourced asset instead.

## Match the pictured subject

| Icon | Visible subject | Useful distinction |
| --- | --- | --- |
| `star` | Eight-point celestial star with small surrounding stars | A celestial landmark; not a compass rose. |
| `sun` | Rayed solar face | A solar or calendar theme; distinct from the star. |
| `compass` | Graduated compass rose | Orientation or navigation. |
| `astrolabe` | Suspended circular instrument with a pointer and engraved scales | An instrument; distinct from a globe. |
| `orbit` | Globe with an inclined orbital path and small satellite | Space or orbital work. |
| `globe` | A mounted graticule globe | Geographic scope; no claimed territorial distribution. |
| `wheel` | Wooden spoked wheel | Mechanical craft; distinct from a toothed gear. |
| `gear` | Toothed mechanical wheel | Machinery or mechanical transmission. |
| `lens` | Convex lens with converging rays | Focusing light; distinct from a dispersing prism. |
| `prism` | Triangular prism with separated colored rays | Dispersion or spectroscopy. |
| `anchor` | Ring, shank, stock and curved flukes | A maritime device; distinct from a vessel. |
| `ship` | Sailing vessel with masts and a hull | Voyages or seamanship. |
| `tower` | Battlemented stone tower | A fortified or civic structure. |
| `observatory` | Domed observing building | An astronomical institution. |

Set a node's `icon` to the intended subject and give it an appropriate `icon_width`. The color block continues to identify the node's category. Small natural-material colors inside an emblem do not change that category. Preserve supplied image identifiers and author/source assignments.

Use a selected emblem where it makes an institution easier to find. Do not turn every supporting name into an illustrated card or manufacture a distinct symbol for every node merely to create variety. If the same object is appropriate for two records, honest repetition is preferable to an unrelated substitute. A different silhouette is useful only when its meaning fits.

## Review at its actual size

Render and open the final poster PNG. Inspect one ordinary small panel, one landmark and their surrounding names. Check that the silhouette survives, fine details do not form an illegible blob, and the image panel does not dominate its text. The normal record geometry and category colors should remain coherent after replacing an image.

For maintenance, `uv run --script <skill-dir>/scripts/test_editorial_art.py` compares actual Chromium-rendered pixels at 29, 37 and 50 units. It rejects the formerly identical subject pairs, blank marks, oversized geometry and external image dependencies. This is a regression check, not proof that a symbol is historically accurate or that the whole poster meets the reference's editorial standard.
