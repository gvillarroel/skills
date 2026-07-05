Use the loaded D3 Animated SVG skill to create exactly `rotating-dot-rings.html` in the current workspace.

The artifact must be a self-contained standalone HTML file with one inline SVG named `rotating-dot-rings`.

Use this exact builder command first:

```powershell
uv run --script skills/d3-animated-svg/scripts/build_rotating_dot_rings.py rotating-dot-rings.html --gap-percent 0.07 --gap-center-degrees -48
```

Requirements:

- Use `d3-pattern-rotating-dot-rings`.
- Show 8 to 14 concentric rings made from individual gray dot circles.
- Remove about 7 percent of each ring's source circles from one deterministic angular sector so the pattern has intentional white space.
- Ring 0 must rotate clockwise, ring 1 counterclockwise, ring 2 clockwise, and so on.
- Expose root data attributes for `data-pattern-id`, `data-pattern-family`, `data-ring-count`, `data-dot-count`, `data-source-dot-count`, `data-gap-dot-count`, `data-gap-percent`, `data-gap-sector-center-degrees`, and `data-direction-rule`.
- Expose each ring as `.dot-ring` with `data-ring-index`, `data-direction`, `data-radius`, `data-dot-count`, `data-source-dot-count`, `data-gap-dot-count`, `data-gap-percent`, and `data-gap-sector-center-degrees`.
- Expose every visible point as `.rotating-dot`.
- Use deterministic geometry, SVG-native animation, a white background, title/desc accessibility nodes, and no external network references.
- If the skill provides a self-contained HTML checker, use it after generation.

Do not read files outside the current workspace. Write the exact requested path `rotating-dot-rings.html`.
