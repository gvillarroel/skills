# Colorset Selection and Semantic Paint

The bundled [colorsets.json](../assets/palettes/colorsets.json) is the exact token
source. It preserves the repository's colorset1 and colorset2 definitions as a
self-contained runtime resource. Use one active palette for a film.

## Prefer colorset1

Use `#f7f7f7` or `#ffffff` for the stage, `#333e48` or `#1c1c1c` for readable
labels and structure, `#9e1b32` for the initiating entity or primary changing
quantity, and neutral grays for supporting structure. Keep repeated entities on
the same role across the mechanism, readout and history curve.

Use position, geometry, direct labels, outline/fill and dash patterns before
another hue. Secondary does not automatically mean pink: `#ffccd5` is a
last-resort category token, outside default assignments. Pale gray is suitable
for structural decoration, not small essential text. Exact palette membership
alone does not establish contrast.

## When colorset2 is justified

Choose it when the user explicitly requests colorset2/extended color, or when
simultaneous semantic categories cannot remain distinguishable using colorset1
and redundant cues within the requested compact layout. Document which categories
need separation and what colorset1 alternatives were insufficient.

The brief's `palette` contains `mode`, `decision` and `reason`:

- colorset1: `decision: default` or `explicit`.
- colorset2: `decision: explicit` or `semantic-capacity`; write a concrete reason.

An increased node count, polish, accessibility, excitement or aesthetic variety
does not by itself justify extended hue. If layout or labels can fix ambiguity,
keep colorset1. Preserve an explicit user colorset1 request and fix the layout.

Colorset2 keeps the brand anchors and adds `secondary` blue `#007298`, `tertiary`
orange `#e77204`, `positive` green `#45842a`, `attention` yellow `#f1c319`, and
`special` purple `#652f6c`. Use only the needed roles. An accepted colorset2 render
must visibly use an extended token on a semantic mark, not merely declare it in
unused CSS. Keep labels dark on light surfaces and add a readable label backing
when it overlaps a saturated mark. Color never carries the only identity cue.

## Runtime paint

Select paints through role names in the brief. The runtime resolves all stage,
text, mark, focus and structure paints to exact six-digit tokens. Use opacity,
geometry or discrete role changes for motion; do not interpolate through arbitrary
RGB colors, add gradients or sample an image palette for a technical mechanism.

The browser audit checks actual computed paint, essential text contrast and
colorset2 usage. Inspect the rendered image as well, including any imported asset.
