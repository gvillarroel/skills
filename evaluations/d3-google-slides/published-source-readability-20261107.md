# Published D3 source readability fixes

The November 7, 2026 review compared the browser originals with 956 rendered Google Slides pages. It identified several cases where a faithful transfer preserved a source problem.

- The Agent Loop Partial Covers fixture loaded its backing bitmap, but solid-fill normalization made a thin white veil opaque. The fixture and reuse recipe now mark the veil as semantic opacity. The browser verifier checks the 980 × 618 bitmap, a computed veil opacity of 0.08, five ordered partial covers, and the pixel effect of hiding the bitmap in each of the three published gallery editions.
- The Population Pyramid placed age labels on the split between two colored bars. The gallery renderer and reuse recipe now reserve an age gutter while preserving the encoded widths of all 18 bars. The composition variant puts the group headings above their columns and keeps the numeric age labels between the bars. The browser verifier checks the gutter in all four renderings.
- Composition previews mark the Replay control as presentation-only. Their SVGs supply an optional focus rectangle when the artwork fits with room to breathe. The interactive page retains the original viewport and its Replay control. Exporters can use the frame and omit the surrounding preview chrome.

```powershell
uv run --script projects/d3-slides-catalog/scripts/verify_agent_loop_source.py --channel msedge
uv run --script projects/d3-slides-catalog/scripts/verify_pyramid_source.py --channel msedge
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/build-pages.py
```

The agent-loop check records rendered screenshots and bitmap paint evidence. The pyramid check verifies label-to-bar clearance from the rendered DOM and checks the widths against the quantitative scale. The settled composition is also reviewed in the native Slides export.
