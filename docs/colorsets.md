# Colorsets and output coverage

Every authored visual output in this repository must use one active colorset. The exact machine-readable definition is [colorsets.json](colorsets.json). Runtime skills keep their own copy or equivalent finite token definition so an isolated bundle never depends on repository documentation or a sibling skill.

Default to colorset1: white and gray surfaces, dark readable labels and red emphasis. Use colorset2 when requested or when the output requires simultaneous semantic categories that cannot be distinguished clearly with labels, geometry and neutral/red roles. Record the active colorset in a manifest, SVG attribute or HTML attribute. Keep the choice consistent across panels, previews, exports and video wrappers.

| Role | Colorset1 | Colorset2 additions |
| --- | --- | --- |
| Stage / surface | `#f7f7f7` / `#ffffff` | Same |
| Labels / strong structure | `#333e48` / `#1c1c1c` | Same |
| Primary / dark primary | `#9e1b32` / `#6d1222` | Same |
| Emphasis | `#e8002a` | Same |
| Secondary | Neutral or redundant geometry | `#007298`, dark `#004d66`, bright `#00ace6`, soft `#cdf3ff` |
| Positive | Neutral or direct label | `#45842a`, dark `#294d19`, bright `#36b300`, soft `#dbffcc` |
| Special | Neutral or direct label | `#652f6c`, dark `#431f47`, bright `#9e00b3`, soft `#f9ccff` |
| Orange category | Neutral or direct label | `#e77204`, dark `#994a00`, bright `#ff9633`, soft `#ffe5cc` |
| Attention | Red or direct label | `#f1c319`, dark `#98700c`, bright `#ffd332`, soft `#fff4cc` |
| Borders / quiet structure | `#cfcfcf` / `#e7e7e7` | Same |

Pink `#ffccd5` is available in both sets but is a last-resort extra category, not the default secondary fill. Exact membership does not establish contrast; inspect small labels, saturated backings, thin lines and animation states independently.

Apply the contract to authored base paint: CSS, SVG fill/stroke, gradient stops, chart options, canvas colors, material/vertex colors, terminal presentation themes and video wrapper/canvas. Alpha compositing, antialiasing, physical shading and lossy codec pixels can produce derived tones; they must not be misrepresented as additional authored palette tokens. Technical categorical marks should switch among discrete tokens instead of synthesizing unrelated hues.

Preserve source fidelity explicitly. Downloaded photos, videos, textures/HDRIs, original brand artwork, embedded source artwork and requested exact-RGB conversion modes keep their original colors and provenance. Their authored frame, controls, captions and diagrams still follow a colorset. Resolve `currentColor` at the consuming surface. Do not claim these original pixels satisfy the authored contract or silently modify source identity.

The [34-skill output inventory](../evaluations/colorset-audit/coverage.json) records formats and paths, including nonvisual data/report outputs and source-fidelity boundaries. The [audit record](../evaluations/colorset-audit/validation-20261002.md) reports actual tests and remaining limits. Run:

```powershell
uv run --script scripts/validate-colorsets.py
uv run --script scripts/validate-colorsets.py --input path/to/output.svg --colorset colorset1
uv run --script scripts/test-colorsets.py
```

The repository checker verifies complete inventory, canonical palette copies and declared artifact paint. For HTML it checks actual CSS and inline SVG; embedded vendor/decoder/source-color tables are input data, so dynamic script output requires browser inspection. It is a static gate, not a substitute for inspecting computed browser/canvas/WebGL state, raster/video output, meaningful semantic roles or user-requested behavior. Keep those checks in the owning renderer and its independent evaluation.
