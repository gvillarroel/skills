(function attachD3LogoDesign(root) {
  "use strict";

  const VIEW_BOX = "0 0 480 320";
  const SVG_NS = "http://www.w3.org/2000/svg";

  function deepFreeze(value) {
    if (value && typeof value === "object" && !Object.isFrozen(value)) {
      Object.freeze(value);
      Object.keys(value).forEach((key) => deepFreeze(value[key]));
    }
    return value;
  }

  const PATTERNS = deepFreeze([
    { id: "d3-logo-type-orbit", label: "Type Orbit", family: "typographic", geometrySignature: "textpath-circle", intentionalOmissions: [{ textRole: "tagline", when: "small-size", reason: "The compact 96 px lockup omits the tagline to preserve legibility." }] },
    { id: "d3-logo-bezier-wordpath", label: "Bezier Wordpath", family: "typographic", geometrySignature: "textpath-cubic" },
    { id: "d3-logo-variable-axis-wordmark", label: "Variable Axis Wordmark", family: "typographic", geometrySignature: "per-glyph-axis" },
    { id: "d3-logo-ligature-bridge", label: "Ligature Bridge", family: "typographic", geometrySignature: "initial-connector", intentionalOcclusions: [{ textRole: "initials", occluderRole: "ligature-connector", reason: "The connector intentionally crosses the joined initials.", maxOcclusionRatio: 0.22 }, { textRole: "initials", occluderRole: "ligature-anchor", reason: "The small connector terminals intentionally touch the joined initials at their attachment points.", maxOcclusionRatio: 0.03 }] },
    { id: "d3-logo-stencil-cuts", label: "Stencil Cuts", family: "typographic", geometrySignature: "masked-stencil-cuts" },
    { id: "d3-logo-letter-window", label: "Letter Window", family: "typographic", geometrySignature: "text-clip-window" },
    { id: "d3-logo-mirrored-monogram", label: "Mirrored Monogram", family: "typographic", geometrySignature: "mirror-transform-axis", intentionalOcclusions: [{ textRole: "initials", occluderRole: "mirror-joint", reason: "The small center joint intentionally pins the mirrored initials at their shared axis.", maxOcclusionRatio: 0.05 }] },
    { id: "d3-logo-glyph-rosette", label: "Glyph Rosette", family: "typographic", geometrySignature: "radial-glyph-repeat" },
    { id: "d3-logo-baseline-wave", label: "Baseline Wave", family: "typographic", geometrySignature: "per-letter-wave" },
    { id: "d3-logo-stack-offset", label: "Stack Offset", family: "typographic", geometrySignature: "offset-copy-stack" },
    { id: "d3-logo-slice-shift", label: "Slice Shift", family: "typographic", geometrySignature: "clip-slice-shift" },
    { id: "d3-logo-multi-stroke-wordmark", label: "Multi-stroke Wordmark", family: "typographic", geometrySignature: "multi-stroke-use" },
    { id: "d3-logo-extruded-wordmark", label: "Extruded Wordmark", family: "typographic", geometrySignature: "translated-depth-stack" },
    { id: "d3-logo-letter-weave", label: "Letter Weave", family: "typographic", geometrySignature: "crossing-mask-weave" },
    { id: "d3-logo-responsive-lockup", label: "Responsive Lockup", family: "typographic", geometrySignature: "responsive-lockup-states" },
    { id: "d3-logo-spiral-trace", label: "Spiral Trace", family: "generative", geometrySignature: "polar-radius-trace" },
    { id: "d3-logo-orbit-network", label: "Orbit Network", family: "generative", geometrySignature: "orbit-link-network" },
    { id: "d3-logo-grid-activation", label: "Grid Activation", family: "generative", geometrySignature: "modular-cell-activation" },
    { id: "d3-logo-contour-fingerprint", label: "Contour Fingerprint", family: "generative", geometrySignature: "scalar-field-contours" },
    { id: "d3-logo-voronoi-shards", label: "Voronoi Shards", family: "generative", geometrySignature: "voronoi-clipped-shards" },
    { id: "d3-logo-animal-facets", label: "Animal Facets", family: "generative", geometrySignature: "delaunay-animal-facets" },
    { id: "d3-logo-animal-surface-mask", label: "Animal Surface Mask", family: "generative", geometrySignature: "animal-surface-mask" },
    { id: "d3-logo-negative-space-reveal", label: "Negative Space Reveal", family: "generative", geometrySignature: "subtractive-negative-space" },
    { id: "d3-logo-folded-ribbon", label: "Folded Ribbon", family: "generative", geometrySignature: "folded-wide-ribbon" },
    { id: "d3-logo-boolean-lens", label: "Boolean Lens", family: "generative", geometrySignature: "overlap-intersection-lens" },
    { id: "d3-logo-radiant-pulse", label: "Radiant Pulse", family: "generative", geometrySignature: "variable-radial-rays" },
    { id: "d3-logo-parametric-wave", label: "Parametric Wave", family: "generative", geometrySignature: "closed-harmonic-curve" },
    { id: "d3-logo-kaleidoscope-wedges", label: "Kaleidoscope Wedges", family: "generative", geometrySignature: "mirrored-radial-wedges" },
    { id: "d3-logo-polar-halo", label: "Polar Halo", family: "generative", geometrySignature: "data-driven-polar-arcs" },
    { id: "d3-logo-aperture-iris", label: "Aperture Iris", family: "generative", geometrySignature: "overlapping-iris-blades" }
  ]);

  const TEXTURES = deepFreeze([
    { id: "d3-logo-micro-grid", label: "Micro Grid", geometrySignature: "orthogonal-tile-grid" },
    { id: "d3-logo-diagonal-hatch", label: "Diagonal Hatch", geometrySignature: "single-angle-hatch" },
    { id: "d3-logo-crosshatch", label: "Crosshatch", geometrySignature: "dual-angle-hatch" },
    { id: "d3-logo-halftone-dots", label: "Halftone Dots", geometrySignature: "modulated-dot-tile" },
    { id: "d3-logo-seeded-stipple", label: "Seeded Stipple", geometrySignature: "seeded-point-tile" },
    { id: "d3-logo-topographic-lines", label: "Topographic Lines", geometrySignature: "contour-line-tile" },
    { id: "d3-logo-voronoi-mosaic", label: "Voronoi Mosaic", geometrySignature: "cell-fragment-tile" },
    { id: "d3-logo-guilloche-waves", label: "Guilloche Waves", geometrySignature: "phase-wave-tile" },
    { id: "d3-logo-woven-checker", label: "Woven Checker", geometrySignature: "alternating-band-tile" },
    { id: "d3-logo-directional-fibers", label: "Directional Fibers", geometrySignature: "seeded-fiber-tile" }
  ]);

  const COMPOSITIONS = deepFreeze([
    { id: "d3-logo-heritage-orbit-lockup", exampleId: "type-orbit", patternId: "d3-logo-type-orbit", textureId: "d3-logo-diagonal-hatch", brand: "NORTHLIGHT", tagline: "Signal in motion", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.72, scale: 1.0, rotation: 0, textureStrength: 0.38, seed: 101 },
    { id: "d3-logo-rising-curve-lockup", exampleId: "bezier-wordpath", patternId: "d3-logo-bezier-wordpath", textureId: "d3-logo-directional-fibers", brand: "TIDELINE", tagline: "Move with purpose", colorset: "colorset2", font: "humanist", density: 0.9, curvature: 0.82, scale: 1.0, rotation: -4, textureStrength: 0.32, seed: 102 },
    { id: "d3-logo-variable-editorial-lockup", exampleId: "variable-axis-wordmark", patternId: "d3-logo-variable-axis-wordmark", textureId: "d3-logo-micro-grid", brand: "FORMFIELD", tagline: "A flexible identity", colorset: "colorset1", font: "editorial", density: 1.1, curvature: 0.45, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 103 },
    { id: "d3-logo-joined-initial-lockup", exampleId: "ligature-bridge", patternId: "d3-logo-ligature-bridge", textureId: "d3-logo-crosshatch", brand: "ARC UNION", tagline: "Built together", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.6, scale: 1.02, rotation: 0, textureStrength: 0.34, seed: 104 },
    { id: "d3-logo-stenciled-utility-lockup", exampleId: "stencil-cuts", patternId: "d3-logo-stencil-cuts", textureId: "d3-logo-seeded-stipple", brand: "IRONVALE", tagline: "Made to endure", colorset: "colorset1", font: "condensed", density: 1.2, curvature: 0.35, scale: 1.0, rotation: -2, textureStrength: 0.28, seed: 105 },
    { id: "d3-logo-textured-letter-window", exampleId: "letter-window", patternId: "d3-logo-letter-window", textureId: "d3-logo-voronoi-mosaic", brand: "LUMA", tagline: "See what is possible", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.5, scale: 1.08, rotation: 0, textureStrength: 0.58, seed: 106 },
    { id: "d3-logo-mirror-axis-lockup", exampleId: "mirrored-monogram", patternId: "d3-logo-mirrored-monogram", textureId: "d3-logo-woven-checker", brand: "AXIS", tagline: "Balanced by design", colorset: "colorset1", font: "editorial", density: 0.9, curvature: 0.55, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 107 },
    { id: "d3-logo-radial-glyph-emblem", exampleId: "glyph-rosette", patternId: "d3-logo-glyph-rosette", textureId: "d3-logo-guilloche-waves", brand: "AERIA", tagline: "Many voices, one form", colorset: "colorset2", font: "humanist", density: 1.2, curvature: 0.68, scale: 0.98, rotation: 8, textureStrength: 0.36, seed: 108 },
    { id: "d3-logo-wave-baseline-lockup", exampleId: "baseline-wave", patternId: "d3-logo-baseline-wave", textureId: "d3-logo-topographic-lines", brand: "SONORA", tagline: "Make the signal visible", colorset: "colorset1", font: "humanist", density: 1.0, curvature: 0.9, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 109 },
    { id: "d3-logo-echo-stack-lockup", exampleId: "stack-offset", patternId: "d3-logo-stack-offset", textureId: "d3-logo-halftone-dots", brand: "ECHOFORM", tagline: "Repeat with intent", colorset: "colorset2", font: "condensed", density: 1.1, curvature: 0.4, scale: 1.0, rotation: -5, textureStrength: 0.32, seed: 110 },
    { id: "d3-logo-sliced-motion-lockup", exampleId: "slice-shift", patternId: "d3-logo-slice-shift", textureId: "d3-logo-directional-fibers", brand: "KINETIQ", tagline: "Designed in motion", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.45, scale: 1.0, rotation: -3, textureStrength: 0.3, seed: 111 },
    { id: "d3-logo-outline-signal-lockup", exampleId: "multi-stroke-wordmark", patternId: "d3-logo-multi-stroke-wordmark", textureId: "d3-logo-micro-grid", brand: "SIGNAL", tagline: "Clarity through layers", colorset: "colorset2", font: "monospace", density: 1.0, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.22, seed: 112 },
    { id: "d3-logo-depth-step-lockup", exampleId: "extruded-wordmark", patternId: "d3-logo-extruded-wordmark", textureId: "d3-logo-diagonal-hatch", brand: "MONOLITH", tagline: "Depth without noise", colorset: "colorset1", font: "condensed", density: 1.1, curvature: 0.35, scale: 0.96, rotation: 0, textureStrength: 0.34, seed: 113 },
    { id: "d3-logo-woven-initial-lockup", exampleId: "letter-weave", patternId: "d3-logo-letter-weave", textureId: "d3-logo-seeded-stipple", brand: "INTERLACE", tagline: "Different paths, shared future", colorset: "colorset2", font: "editorial", density: 1.0, curvature: 0.74, scale: 1.0, rotation: 0, textureStrength: 0.4, seed: 114 },
    { id: "d3-logo-responsive-brand-family", exampleId: "responsive-lockup", patternId: "d3-logo-responsive-lockup", textureId: "d3-logo-guilloche-waves", brand: "MODULA", tagline: "One system, every space", colorset: "colorset1", font: "geometric", density: 0.9, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.25, seed: 115 },
    { id: "d3-logo-spiral-core-lockup", exampleId: "spiral-trace", patternId: "d3-logo-spiral-trace", textureId: "d3-logo-voronoi-mosaic", brand: "SPIRA", tagline: "Ideas in orbit", colorset: "colorset2", font: "humanist", density: 1.2, curvature: 0.86, scale: 1.0, rotation: 6, textureStrength: 0.34, seed: 116 },
    { id: "d3-logo-connected-orbit-lockup", exampleId: "orbit-network", patternId: "d3-logo-orbit-network", textureId: "d3-logo-woven-checker", brand: "NEXUS", tagline: "Connect what matters", colorset: "colorset1", font: "geometric", density: 1.1, curvature: 0.65, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 117 },
    { id: "d3-logo-modular-grid-lockup", exampleId: "grid-activation", patternId: "d3-logo-grid-activation", textureId: "d3-logo-directional-fibers", brand: "GRIDWORK", tagline: "Systems made visible", colorset: "colorset2", font: "monospace", density: 1.2, curvature: 0.4, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 118 },
    { id: "d3-logo-contour-medallion", exampleId: "contour-fingerprint", patternId: "d3-logo-contour-fingerprint", textureId: "d3-logo-diagonal-hatch", brand: "TERRAIN", tagline: "Defined by place", colorset: "colorset1", font: "editorial", density: 1.0, curvature: 0.7, scale: 1.0, rotation: 0, textureStrength: 0.42, seed: 119 },
    { id: "d3-logo-voronoi-window-lockup", exampleId: "voronoi-shards", patternId: "d3-logo-voronoi-shards", textureId: "d3-logo-guilloche-waves", brand: "VORO", tagline: "Order from fragments", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.5, scale: 1.02, rotation: 0, textureStrength: 0.46, seed: 120 },
    { id: "d3-logo-faceted-fauna-lockup", exampleId: "animal-facets", patternId: "d3-logo-animal-facets", textureId: "d3-logo-halftone-dots", brand: "WILDFOLD", tagline: "Built for open ground", colorset: "colorset1", font: "condensed", density: 1.2, curvature: 0.58, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 121 },
    { id: "d3-logo-surface-fauna-lockup", exampleId: "animal-surface-mask", patternId: "d3-logo-animal-surface-mask", textureId: "d3-logo-topographic-lines", brand: "ROAM", tagline: "Follow your nature", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.68, scale: 1.0, rotation: 0, textureStrength: 0.55, seed: 122 },
    { id: "d3-logo-hidden-initial-lockup", exampleId: "negative-space-reveal", patternId: "d3-logo-negative-space-reveal", textureId: "d3-logo-crosshatch", brand: "REVEAL", tagline: "Look twice", colorset: "colorset1", font: "geometric", density: 0.9, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.34, seed: 123 },
    { id: "d3-logo-ribbon-fold-lockup", exampleId: "folded-ribbon", patternId: "d3-logo-folded-ribbon", textureId: "d3-logo-micro-grid", brand: "CONTINUUM", tagline: "A path that keeps moving", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.84, scale: 0.98, rotation: 0, textureStrength: 0.3, seed: 124 },
    { id: "d3-logo-overlap-lens-lockup", exampleId: "boolean-lens", patternId: "d3-logo-boolean-lens", textureId: "d3-logo-seeded-stipple", brand: "SYNTHESIS", tagline: "Better at the intersection", colorset: "colorset1", font: "editorial", density: 1.0, curvature: 0.52, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 125 },
    { id: "d3-logo-radiant-core-lockup", exampleId: "radiant-pulse", patternId: "d3-logo-radiant-pulse", textureId: "d3-logo-halftone-dots", brand: "RADIANT", tagline: "Turn energy outward", colorset: "colorset2", font: "condensed", density: 1.2, curvature: 0.64, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 126 },
    { id: "d3-logo-harmonic-wave-lockup", exampleId: "parametric-wave", patternId: "d3-logo-parametric-wave", textureId: "d3-logo-crosshatch", brand: "HARMONIC", tagline: "Find the shared frequency", colorset: "colorset1", font: "monospace", density: 1.1, curvature: 0.88, scale: 1.0, rotation: 4, textureStrength: 0.34, seed: 127 },
    { id: "d3-logo-kaleidoscope-emblem", exampleId: "kaleidoscope-wedges", patternId: "d3-logo-kaleidoscope-wedges", textureId: "d3-logo-woven-checker", brand: "PRISMATA", tagline: "Many angles, one identity", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.62, scale: 1.0, rotation: 12, textureStrength: 0.4, seed: 128 },
    { id: "d3-logo-polar-data-lockup", exampleId: "polar-halo", patternId: "d3-logo-polar-halo", textureId: "d3-logo-voronoi-mosaic", brand: "CYCLE", tagline: "Measure the whole system", colorset: "colorset1", font: "humanist", density: 1.0, curvature: 0.56, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 129 },
    { id: "d3-logo-iris-aperture-lockup", exampleId: "aperture-iris", patternId: "d3-logo-aperture-iris", textureId: "d3-logo-topographic-lines", brand: "APERTURE", tagline: "Bring the idea into focus", colorset: "colorset2", font: "condensed", density: 1.1, curvature: 0.76, scale: 1.0, rotation: -8, textureStrength: 0.32, seed: 130 }
  ]);

  const FONT_STACKS = deepFreeze([
    { id: "geometric", label: "Geometric Sans", value: '"Avenir Next", "Century Gothic", Arial, sans-serif' },
    { id: "humanist", label: "Humanist Sans", value: '"Open Sans", "Segoe UI", Arial, sans-serif' },
    { id: "condensed", label: "Condensed Sans", value: '"Arial Narrow", "Roboto Condensed", "Liberation Sans Narrow", sans-serif' },
    { id: "editorial", label: "Editorial Serif", value: 'Georgia, "Times New Roman", serif' },
    { id: "monospace", label: "Monospaced", value: '"IBM Plex Mono", Consolas, "Courier New", monospace' }
  ]);

  const FONTS = deepFreeze(Object.fromEntries(FONT_STACKS.map((font) => [font.id, {
    id: font.id,
    label: font.label,
    value: font.value,
    family: font.value
  }])));

  const COLORSETS = deepFreeze({
    colorset1: {
      name: "basic-red-neutral-style",
      allowed: ["#000000", "#1c1c1c", "#333e48", "#363636", "#4f4f4f", "#696969", "#6d1222", "#828282", "#9c9c9c", "#9e1b32", "#b5b5b5", "#cfcfcf", "#e7e7e7", "#e8002a", "#f7f7f7", "#ffccd5", "#ffffff"],
      roles: { background: "#f7f7f7", surface: "#ffffff", ink: "#333e48", inkDark: "#1c1c1c", primary: "#9e1b32", primaryDark: "#6d1222", accent: "#e8002a", accentSoft: "#ffccd5", muted: "#828282", line: "#cfcfcf", quiet: "#e7e7e7" },
      sequence: ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a", "#cfcfcf"]
    },
    colorset2: {
      name: "full-color-style",
      allowed: ["#000000", "#004d66", "#007298", "#00ace6", "#1c1c1c", "#294d19", "#333e48", "#363636", "#36b300", "#431f47", "#45842a", "#4f4f4f", "#652f6c", "#696969", "#6d1222", "#828282", "#98700c", "#994a00", "#9c9c9c", "#9e00b3", "#9e1b32", "#b5b5b5", "#cdf3ff", "#cfcfcf", "#dbffcc", "#e77204", "#e7e7e7", "#e8002a", "#f1c319", "#f7f7f7", "#f9ccff", "#ff9633", "#ffccd5", "#ffd332", "#ffe5cc", "#fff4cc", "#ffffff"],
      roles: { background: "#f7f7f7", surface: "#ffffff", ink: "#333e48", inkDark: "#1c1c1c", primary: "#9e1b32", primaryDark: "#6d1222", secondary: "#007298", secondaryDark: "#004d66", tertiary: "#e77204", positive: "#45842a", attention: "#f1c319", special: "#652f6c", accent: "#e8002a", accentSoft: "#ffccd5", muted: "#828282", line: "#cfcfcf", quiet: "#e7e7e7" },
      sequence: ["#9e1b32", "#007298", "#e77204", "#45842a", "#652f6c", "#f1c319"]
    }
  });

  const PATTERN_BY_ID = new Map(PATTERNS.map((item) => [item.id, item]));
  const TEXTURE_BY_ID = new Map(TEXTURES.map((item) => [item.id, item]));
  const COMPOSITION_BY_ID = new Map(COMPOSITIONS.map((item) => [item.id, item]));
  const COMPOSITION_BY_PATTERN = new Map(COMPOSITIONS.map((item) => [item.patternId, item]));
  const FONT_BY_ID = new Map(FONT_STACKS.map((item) => [item.id, item]));

  function getD3() {
    const d3 = root.d3;
    if (!d3 || typeof d3.select !== "function" || typeof d3.line !== "function" || typeof d3.arc !== "function") {
      throw new Error("D3 Logo Design requires the global D3 v7 bundle before renderLogo is called.");
    }
    if (d3.version && String(d3.version).split(".")[0] !== "7") {
      throw new Error(`D3 Logo Design requires D3 v7; found ${d3.version}.`);
    }
    return d3;
  }

  function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
  }

  function finiteNumber(value, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  }

  function sanitizeId(value) {
    const clean = String(value == null ? "logo" : value)
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .replace(/-+/g, "-");
    return clean || "logo";
  }

  function hashString(value) {
    let hash = 2166136261;
    const text = String(value);
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(36);
  }

  function makeIdFactory(prefix) {
    const seen = new Map();
    return function uid(label) {
      const slug = sanitizeId(label);
      const count = (seen.get(slug) || 0) + 1;
      seen.set(slug, count);
      return `${prefix}-${slug}${count > 1 ? `-${count}` : ""}`;
    };
  }

  function fragmentUrl(id) {
    return `url(#${id})`;
  }

  function resolveFont(value) {
    const requested = value == null ? "geometric" : String(value);
    if (FONT_BY_ID.has(requested)) return FONT_BY_ID.get(requested);
    const byValue = FONT_STACKS.find((item) => item.value === requested || item.label === requested);
    if (byValue) return byValue;
    if (requested.trim() && requested.length <= 180 && !/[{};]/.test(requested)) {
      return { id: "custom", label: "Custom licensed font", value: requested };
    }
    throw new RangeError(`Invalid custom font stack: ${requested}`);
  }

  function isValidCanonicalId(value) {
    return typeof value === "string" && value.length <= 64 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value);
  }

  function normalizeConfig(input) {
    const source = input && typeof input === "object" ? input : {};
    const requestedComposition = source.compositionId == null ? null : String(source.compositionId);
    const requestedPattern = source.patternId == null
      ? (source.pattern == null ? null : String(source.pattern))
      : String(source.patternId);
    const requestedTexture = source.textureId == null
      ? (source.texture == null ? null : String(source.texture))
      : String(source.textureId);

    let composition;
    let compositionId;
    if (requestedComposition) {
      composition = COMPOSITION_BY_ID.get(requestedComposition);
      if (composition) {
        if (requestedPattern && requestedPattern !== composition.patternId) {
          throw new RangeError(`Composition ${requestedComposition} requires pattern ${composition.patternId}.`);
        }
        compositionId = composition.id;
      } else {
        if (!isValidCanonicalId(requestedComposition)) {
          throw new RangeError(`Invalid custom composition ID: ${requestedComposition}`);
        }
        if (!requestedPattern || !PATTERN_BY_ID.has(requestedPattern)) {
          throw new RangeError(`Custom composition ${requestedComposition} requires a registered patternId.`);
        }
        composition = COMPOSITION_BY_PATTERN.get(requestedPattern);
        compositionId = requestedComposition;
      }
    } else if (requestedPattern) {
      composition = COMPOSITION_BY_PATTERN.get(requestedPattern);
      if (!composition) throw new RangeError(`Unknown pattern ID: ${requestedPattern}`);
      compositionId = composition.id;
    } else {
      composition = COMPOSITIONS[0];
      compositionId = composition.id;
    }

    const patternId = requestedPattern || composition.patternId;
    const textureId = requestedTexture || composition.textureId;
    const expectedExampleId = patternId.replace(/^d3-logo-/, "");
    const exampleId = source.exampleId == null ? composition.exampleId : String(source.exampleId);
    const colorset = source.colorset == null ? composition.colorset : String(source.colorset);
    if (!PATTERN_BY_ID.has(patternId)) throw new RangeError(`Unknown pattern ID: ${patternId}`);
    if (!TEXTURE_BY_ID.has(textureId)) throw new RangeError(`Unknown texture ID: ${textureId}`);
    if (!isValidCanonicalId(exampleId) || exampleId !== expectedExampleId) {
      throw new RangeError(`Example ID ${exampleId} must match the local technique slug ${expectedExampleId}.`);
    }
    if (!Object.prototype.hasOwnProperty.call(COLORSETS, colorset)) {
      throw new RangeError(`Unknown colorset: ${colorset}`);
    }

    const font = resolveFont(source.font == null ? (source.fontFamily == null ? composition.font : source.fontFamily) : source.font);
    const brand = String(source.brand == null ? composition.brand : source.brand);
    const tagline = String(source.tagline == null ? composition.tagline : source.tagline);
    const density = clamp(finiteNumber(source.density, composition.density), 0.45, 2.0);
    const curvature = clamp(finiteNumber(source.curvature, composition.curvature), 0, 1);
    const scale = clamp(finiteNumber(source.scale, composition.scale), 0.6, 1.35);
    const rotation = clamp(finiteNumber(source.rotation, composition.rotation), -180, 180);
    const textureStrength = clamp(finiteNumber(source.textureStrength, composition.textureStrength), 0, 1);
    const seed = Math.trunc(finiteNumber(source.seed, composition.seed));

    return Object.freeze({
      compositionId,
      exampleId,
      patternId,
      textureId,
      brand,
      tagline,
      colorset,
      font: font.id,
      fontFamily: font.value,
      density,
      curvature,
      scale,
      rotation,
      textureStrength,
      seed,
      viewBox: VIEW_BOX,
      accessibilityLabel: String(source.accessibilityLabel == null ? `${brand}${tagline ? ` — ${tagline}` : ""}` : source.accessibilityLabel),
      instanceId: source.instanceId == null ? "" : String(source.instanceId),
      outputWidth: finiteNumber(source.outputWidth, 0),
      smallSize: source.smallSize === true || source.swatch === true
    });
  }

  function effectiveWidth(svgNode, config) {
    if (config.outputWidth > 0) return config.outputWidth;
    if (typeof svgNode.getBoundingClientRect === "function") {
      const measured = finiteNumber(svgNode.getBoundingClientRect().width, 0);
      if (measured > 0) return measured;
    }
    const widthAttribute = finiteNumber(svgNode.getAttribute("width"), 0);
    return widthAttribute > 0 ? widthAttribute : 480;
  }

  function markContainsText(markNode, ctx) {
    if (markNode.querySelector("text, [data-text-proxy]")) return true;
    return Array.from(markNode.querySelectorAll("use")).some((node) => resolvedUseTarget(node, ctx.svgNode)?.localName === "text");
  }

  function rotatedScaleLimit(box, rotation, safeBounds) {
    const pivotX = 240;
    const pivotY = 145;
    const radians = rotation * Math.PI / 180;
    const cosine = Math.cos(radians);
    const sine = Math.sin(radians);
    const corners = [
      [box.x, box.y],
      [box.x + box.width, box.y],
      [box.x + box.width, box.y + box.height],
      [box.x, box.y + box.height]
    ];
    let limit = Number.POSITIVE_INFINITY;
    for (const [x, y] of corners) {
      const dx = x - pivotX;
      const dy = y - pivotY;
      const rotatedX = dx * cosine - dy * sine;
      const rotatedY = dx * sine + dy * cosine;
      if (rotatedX < 0) limit = Math.min(limit, (pivotX - safeBounds.left) / -rotatedX);
      if (rotatedX > 0) limit = Math.min(limit, (safeBounds.right - pivotX) / rotatedX);
      if (rotatedY < 0) limit = Math.min(limit, (pivotY - safeBounds.top) / -rotatedY);
      if (rotatedY > 0) limit = Math.min(limit, (safeBounds.bottom - pivotY) / rotatedY);
    }
    return Number.isFinite(limit) && limit > 0 ? limit : 1;
  }

  function applySafeMarkTransform(markGroup, ctx) {
    const markNode = markGroup.node();
    const requestedScale = ctx.config.scale;
    const requestedRotation = ctx.config.rotation;
    const carriesText = markContainsText(markNode, ctx);
    const reservesBrand = !ctx.brandHandled;
    const reservesTagline = !ctx.taglineHandled && Boolean(ctx.config.tagline);
    const safeBounds = {
      left: 18,
      right: 462,
      top: 14,
      bottom: reservesBrand ? 238 : (reservesTagline ? 282 : 306)
    };
    let effectiveScale = requestedScale;
    try {
      markGroup.attr("transform", null);
      const box = markNode.getBBox();
      if ([box.x, box.y, box.width, box.height].every(Number.isFinite) && box.width > 0 && box.height > 0) {
        effectiveScale = Math.min(requestedScale, rotatedScaleLimit(box, requestedRotation, safeBounds) * 0.98);
      }
    } catch (error) {
      effectiveScale = requestedScale;
    }
    effectiveScale = clamp(effectiveScale, 0.25, requestedScale);
    markGroup
      .attr("data-requested-scale", requestedScale)
      .attr("data-effective-scale", effectiveScale.toFixed(4))
      .attr("data-requested-rotation", requestedRotation)
      .attr("data-effective-rotation", requestedRotation)
      .attr("data-carries-text", carriesText ? "true" : "false")
      .attr("data-reserves-brand", reservesBrand ? "true" : "false")
      .attr("data-reserves-tagline", reservesTagline ? "true" : "false")
      .attr("data-safe-bounds", `${safeBounds.left},${safeBounds.top},${safeBounds.right},${safeBounds.bottom}`)
      .attr("transform", `translate(240,145) rotate(${requestedRotation}) scale(${effectiveScale}) translate(-240,-145)`);
    ctx.svg
      .attr("data-effective-scale", effectiveScale.toFixed(4))
      .attr("data-effective-rotation", requestedRotation);
    return effectiveScale;
  }

  function stablePrefix(svgNode, config) {
    const ownerDocument = svgNode.ownerDocument;
    let documentIndex = 0;
    if (ownerDocument && typeof ownerDocument.querySelectorAll === "function") {
      const nodes = Array.from(ownerDocument.querySelectorAll("svg"));
      const found = nodes.indexOf(svgNode);
      if (found >= 0) documentIndex = found;
    }
    const existingInstance = svgNode.getAttribute("data-logo-instance") || "";
    const nodeIdentity = config.instanceId || svgNode.getAttribute("id") || existingInstance || `${config.compositionId}-${documentIndex}`;
    const instance = `${sanitizeId(config.compositionId)}-${hashString(nodeIdentity)}`;
    svgNode.setAttribute("data-logo-instance", instance);
    return `d3ld-${instance}`;
  }

  function seededRandom(d3, seed, salt) {
    const mixed = ((seed >>> 0) ^ parseInt(hashString(salt), 36)) >>> 0;
    return d3.randomLcg(mixed);
  }

  function texturePattern(defs, ctx, size) {
    const texture = TEXTURE_BY_ID.get(ctx.config.textureId);
    return defs.append("pattern")
      .attr("id", ctx.texturePatternId)
      .attr("data-texture-id", texture.id)
      .attr("data-geometry-signature", texture.geometrySignature)
      .attr("patternUnits", "userSpaceOnUse")
      .attr("width", size)
      .attr("height", size)
      .attr("viewBox", `0 0 ${size} ${size}`);
  }

  function textureBase(pattern, ctx, size, fill) {
    pattern.append("rect")
      .attr("width", size)
      .attr("height", size)
      .attr("fill", fill || ctx.palette.roles.primary);
  }

  const TEXTURE_RENDERERS = {
    "d3-logo-micro-grid": function renderMicroGrid(defs, ctx) {
      const size = 20 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      pattern.append("path")
        .attr("d", `M${size / 2},0V${size}M0,${size / 2}H${size}M${size},0H0V${size}`)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.6, 1.25 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-diagonal-hatch": function renderDiagonalHatch(defs, ctx) {
      const size = 18 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      pattern.append("path")
        .attr("d", `M${-size / 3},${size}L${size},${-size / 3}M0,${size * 1.33}L${size * 1.33},0`)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.8, 1.7 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-crosshatch": function renderCrosshatch(defs, ctx) {
      const size = 21 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      pattern.selectAll("path")
        .data([
          `M${-size / 3},${size}L${size},${-size / 3}M0,${size * 1.33}L${size * 1.33},0`,
          `M0,${-size / 3}L${size * 1.33},${size}M${-size / 3},0L${size},${size * 1.33}`
        ])
        .join("path")
        .attr("d", (d) => d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.55, 1.15 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength * 0.82);
      return pattern;
    },

    "d3-logo-halftone-dots": function renderHalftoneDots(defs, ctx) {
      const size = 24 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      if (ctx.smallSize) {
        pattern.attr("data-flat-fallback", "true");
        pattern.select("rect").attr("fill", ctx.palette.roles.primary);
        return pattern;
      }
      const random = seededRandom(ctx.d3, ctx.config.seed, "halftone");
      const cells = [
        [size * 0.25, size * 0.25], [size * 0.75, size * 0.25],
        [size * 0.25, size * 0.75], [size * 0.75, size * 0.75]
      ].map((point, index) => ({ x: point[0], y: point[1], r: size * (0.08 + random() * 0.11 + index * 0.012) }));
      pattern.selectAll("circle")
        .data(cells)
        .join("circle")
        .attr("cx", (d) => d.x)
        .attr("cy", (d) => d.y)
        .attr("r", (d) => d.r)
        .attr("fill", ctx.palette.roles.primary)
        .attr("opacity", 0.45 + ctx.config.textureStrength * 0.55);
      return pattern;
    },

    "d3-logo-seeded-stipple": function renderSeededStipple(defs, ctx) {
      const size = 34 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const random = seededRandom(ctx.d3, ctx.config.seed, "stipple");
      const count = Math.max(8, Math.round(15 * ctx.config.density));
      const points = ctx.d3.range(count).map(() => ({
        x: random() * size,
        y: random() * size,
        r: 0.55 + random() * 1.45
      }));
      pattern.selectAll("circle")
        .data(points)
        .join("circle")
        .attr("cx", (d) => d.x)
        .attr("cy", (d) => d.y)
        .attr("r", (d) => d.r)
        .attr("fill", ctx.palette.roles.ink)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-topographic-lines": function renderTopographicLines(defs, ctx) {
      const size = 52 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const line = ctx.d3.line().curve(ctx.d3.curveBasis);
      const amplitude = size * (0.08 + ctx.config.curvature * 0.12);
      const paths = ctx.d3.range(5).map((row) => ctx.d3.range(7).map((column) => [
        column * size / 6,
        (row + 0.6) * size / 5 + Math.sin(column * 1.3 + row) * amplitude
      ]));
      pattern.selectAll("path")
        .data(paths)
        .join("path")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.55, 1.1 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-voronoi-mosaic": function renderVoronoiMosaic(defs, ctx) {
      const size = 46 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      const random = seededRandom(ctx.d3, ctx.config.seed, "texture-voronoi");
      const sites = ctx.d3.range(9).map(() => [random() * size, random() * size]);
      const voronoi = ctx.d3.Delaunay.from(sites).voronoi([0, 0, size, size]);
      const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
      pattern.selectAll("path")
        .data(Array.from(voronoi.cellPolygons()))
        .join("path")
        .attr("d", line)
        .attr("fill", (d, index) => index === 0 ? ctx.textureFillFallback : ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.background)
        .attr("stroke-width", 0.9)
        .attr("opacity", (d, index) => index === 0 ? 1 : 0.55 + ctx.config.textureStrength * 0.45);
      return pattern;
    },

    "d3-logo-guilloche-waves": function renderGuillocheWaves(defs, ctx) {
      const size = 58 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const line = ctx.d3.line().curve(ctx.d3.curveBasis);
      const waves = ctx.d3.range(7).map((row) => ctx.d3.range(17).map((column) => {
        const x = column * size / 16;
        const y = size * (row + 0.5) / 7 + Math.sin(column * 0.85 + row * 0.72) * size * 0.075 * ctx.config.curvature;
        return [x, y];
      }));
      pattern.selectAll("path")
        .data(waves)
        .join("path")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.85)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-woven-checker": function renderWovenChecker(defs, ctx) {
      const size = 32 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const band = size / 4;
      pattern.selectAll("rect.vertical")
        .data([0, 2])
        .join("rect")
        .attr("class", "vertical")
        .attr("x", (d) => d * band)
        .attr("width", band)
        .attr("height", size)
        .attr("fill", ctx.palette.sequence[1 % ctx.palette.sequence.length])
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      pattern.selectAll("rect.horizontal")
        .data([0, 2])
        .join("rect")
        .attr("class", "horizontal")
        .attr("y", (d) => d * band)
        .attr("width", size)
        .attr("height", band)
        .attr("fill", ctx.palette.roles.ink)
        .attr("opacity", 0.35 + ctx.config.textureStrength * 0.55);
      pattern.selectAll("rect.over")
        .data([[0, 0], [2, 2]])
        .join("rect")
        .attr("class", "over")
        .attr("x", (d) => d[0] * band)
        .attr("y", (d) => d[1] * band)
        .attr("width", band)
        .attr("height", band)
        .attr("fill", ctx.palette.roles.primary);
      return pattern;
    },

    "d3-logo-directional-fibers": function renderDirectionalFibers(defs, ctx) {
      const size = 42 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const random = seededRandom(ctx.d3, ctx.config.seed, "fibers");
      const count = Math.max(9, Math.round(17 * ctx.config.density));
      const fibers = ctx.d3.range(count).map(() => {
        const x = random() * size;
        const y = random() * size;
        const length = size * (0.2 + random() * 0.42);
        return { x1: x, y1: y, x2: x + length, y2: y + length * (0.14 + ctx.config.curvature * 0.28) };
      });
      pattern.selectAll("line")
        .data(fibers)
        .join("line")
        .attr("x1", (d) => d.x1)
        .attr("y1", (d) => d.y1)
        .attr("x2", (d) => d.x2)
        .attr("y2", (d) => d.y2)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 1)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    }
  };

  function createTexture(defs, ctx) {
    if (ctx.config.textureStrength === 0) {
      const flat = texturePattern(defs, ctx, 16);
      flat.attr("data-flat-fallback", "texture-strength-zero");
      textureBase(flat, ctx, 16, ctx.palette.roles.primary);
      return flat;
    }
    const renderer = TEXTURE_RENDERERS[ctx.config.textureId];
    if (!renderer) throw new RangeError(`No texture renderer for ${ctx.config.textureId}.`);
    return renderer(defs, ctx);
  }

  function brandInitials(brand) {
    const words = String(brand).trim().split(/\s+/u).filter(Boolean);
    if (!words.length) return "?";
    if (words.length > 1) return words.slice(0, 2).map((word) => Array.from(word)[0]).join("").toLocaleUpperCase();
    return Array.from(words[0]).slice(0, 2).join("").toLocaleUpperCase();
  }

  function fittedFontSize(text, preferred, maxWidth, minimum = 8) {
    const length = Math.max(1, Array.from(String(text)).length);
    return Math.max(minimum, Math.min(preferred, maxWidth / (length * 0.59)));
  }

  function fitTextToWidth(selection, maxWidth, minimumSize = 6) {
    const node = selection.node();
    if (!node || !(maxWidth > 0) || typeof node.getComputedTextLength !== "function") return selection;
    const currentSize = finiteNumber(node.getAttribute("font-size"), 16);
    let measuredWidth = 0;
    try {
      measuredWidth = node.getComputedTextLength();
    } catch (error) {
      measuredWidth = 0;
    }
    if (!(measuredWidth > maxWidth)) {
      node.setAttribute("data-text-fit", "natural");
      return selection;
    }
    const fittedSize = Math.max(minimumSize, currentSize * maxWidth / measuredWidth);
    node.setAttribute("font-size", fittedSize.toFixed(3));
    node.setAttribute("data-text-fit", "font-size");
    try {
      measuredWidth = node.getComputedTextLength();
    } catch (error) {
      measuredWidth = 0;
    }
    if (measuredWidth > maxWidth + 0.25) {
      node.setAttribute("textLength", maxWidth);
      node.setAttribute("lengthAdjust", "spacingAndGlyphs");
      node.setAttribute("data-text-fit", "length-adjust");
    }
    return selection;
  }

  function balancedTextLines(value) {
    const text = String(value).trim();
    const words = text.split(/\s+/u).filter(Boolean);
    if (words.length > 1) {
      let splitIndex = 1;
      let bestDifference = Number.POSITIVE_INFINITY;
      for (let index = 1; index < words.length; index += 1) {
        const first = words.slice(0, index).join(" ");
        const second = words.slice(index).join(" ");
        const difference = Math.abs(Array.from(first).length - Array.from(second).length);
        if (difference < bestDifference) {
          bestDifference = difference;
          splitIndex = index;
        }
      }
      return [words.slice(0, splitIndex).join(" "), words.slice(splitIndex).join(" ")];
    }
    const characters = Array.from(text);
    const midpoint = Math.ceil(characters.length / 2);
    return [characters.slice(0, midpoint).join(""), characters.slice(midpoint).join("")].filter(Boolean);
  }

  function fitOrWrapText(selection, value, maxWidth, minimumSize, lineHeight) {
    const node = selection.node();
    if (!node || typeof node.getComputedTextLength !== "function") return selection;
    const currentSize = finiteNumber(node.getAttribute("font-size"), 16);
    let measuredWidth = 0;
    try {
      measuredWidth = node.getComputedTextLength();
    } catch (error) {
      measuredWidth = 0;
    }
    const requiredSize = measuredWidth > 0 ? currentSize * maxWidth / measuredWidth : currentSize;
    if (requiredSize >= minimumSize) return fitTextToWidth(selection, maxWidth, minimumSize);

    const lines = balancedTextLines(value);
    if (lines.length < 2) return fitTextToWidth(selection, maxWidth, minimumSize);
    const x = finiteNumber(node.getAttribute("x"), 240);
    const centerY = finiteNumber(node.getAttribute("y"), 160);
    const originalHasSpaces = /\s/u.test(String(value));
    selection
      .text(null)
      .attr("aria-label", String(value))
      .attr("data-text-fit", "wrapped-2-lines")
      .attr("data-text-line-count", lines.length);
    lines.forEach((line, index) => {
      const renderedLine = originalHasSpaces && index < lines.length - 1 ? `${line} ` : line;
      const lineSelection = selection.append("tspan")
        .attr("x", x)
        .attr("y", centerY + (index - (lines.length - 1) / 2) * lineHeight)
        .attr("data-text-line", index + 1)
        .text(renderedLine);
      fitTextToWidth(lineSelection, maxWidth, minimumSize);
    });
    return selection;
  }

  function addText(group, ctx, options) {
    const className = options.className || "";
    const inferredRole = options.role || (
      /tagline/.test(className) ? "tagline" :
      /initial|monogram|ligature/.test(className) ? "initials" :
      /value/.test(className) ? "label" :
      /brand|wordmark|window|axis-glyph|wave-glyph|stack-copy|depth-copy/.test(className) ? "brand" :
      "decorative"
    );
    const selection = group.append("text")
      .attr("class", options.className || null)
      .attr("data-text-role", inferredRole)
      .attr("x", options.x == null ? 240 : options.x)
      .attr("y", options.y == null ? 160 : options.y)
      .attr("text-anchor", options.anchor || "middle")
      .attr("dominant-baseline", options.baseline || "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", options.size == null ? 32 : options.size)
      .attr("font-weight", options.weight == null ? 700 : options.weight)
      .attr("letter-spacing", options.tracking == null ? 0 : options.tracking)
      .attr("fill", options.fill || ctx.palette.roles.ink)
      .text(options.text == null ? "" : options.text);
    if (options.maxWidth != null) {
      const minimumSize = options.minimumSize == null ? 6 : options.minimumSize;
      if (options.maxLines > 1) {
        fitOrWrapText(selection, options.text, options.maxWidth, minimumSize, options.lineHeight || minimumSize * 1.25);
      } else {
        fitTextToWidth(selection, options.maxWidth, minimumSize);
      }
    }
    return selection;
  }

  function resolvedUseTarget(node, svgNode) {
    if (String(node.localName).toLowerCase() !== "use") return null;
    const href = node.getAttribute("href") || node.getAttribute("xlink:href") || "";
    return href.startsWith("#") ? svgNode.querySelector(href) : null;
  }

  function inferRenderedTextRole(node, ctx) {
    const explicit = node.getAttribute("data-text-role");
    if (explicit) return explicit;
    const target = resolvedUseTarget(node, ctx.svgNode);
    const className = `${node.getAttribute("class") || ""} ${target?.getAttribute("class") || ""}`;
    const text = `${node.textContent || ""}${target?.textContent || ""}`.trim();
    if (/tagline/.test(className) || text === ctx.config.tagline) return "tagline";
    if (/initial|monogram|ligature/.test(className) || text === brandInitials(ctx.config.brand)) return "initials";
    if (/polar-value|label/.test(className)) return "label";
    if (/rosette-glyph/.test(className)) return "decorative";
    if (/axis-glyph|wave-glyph|stack-copy|shifted-slice|stroke-layer|stroke-fill|depth-copy|brand|wordmark|window/.test(className)) return "brand";
    if (text === ctx.config.brand) return "brand";
    if (text.includes(ctx.config.brand) && ctx.config.tagline && text.includes(ctx.config.tagline)) return "brand-tagline";
    return "decorative";
  }

  function annotateTextLayers(compositionGroup, ctx) {
    const root = compositionGroup.node();
    const candidates = Array.from(root.querySelectorAll("text, use, [data-text-proxy]"))
      .filter((node) => {
        if (node.matches("[data-text-proxy], text")) return true;
        return resolvedUseTarget(node, ctx.svgNode)?.localName === "text";
      })
      .filter((node, index, values) => !values.some((parent, parentIndex) => parentIndex !== index && parent.contains(node) && parent.hasAttribute("data-text-proxy")));
    for (const node of candidates) {
      const role = inferRenderedTextRole(node, ctx);
      const source = node.getAttribute("data-text-proxy") || (
        String(node.localName).toLowerCase() === "use" ? "use-stack" :
        node.querySelector?.("textPath") ? "text-path" :
        node.matches("text") ? "glyph-run" : "proxy"
      );
      const layerSuffix = node.getAttribute("data-text-layer-suffix");
      const layerId = `${ctx.config.exampleId}--${sanitizeId(role)}${layerSuffix ? `-${sanitizeId(layerSuffix)}` : ""}`;
      node.setAttribute("data-text-role", role);
      node.setAttribute("data-text-layer-id", layerId);
      node.setAttribute("data-text-source", source);
      if (!node.hasAttribute("data-text-policy")) node.setAttribute("data-text-policy", "clear");
    }

    const layerCounts = new Map();
    const drawables = root.querySelectorAll("path, rect, circle, ellipse, line, polyline, polygon, use, text");
    for (const node of drawables) {
      if (node.closest("[data-text-layer-id]")) continue;
      const classToken = (node.getAttribute("class") || "").trim().split(/\s+/u).filter(Boolean)[0];
      const role = node.getAttribute("data-layer-role") || classToken || String(node.localName).toLowerCase();
      const safeRole = sanitizeId(role);
      const ordinal = (layerCounts.get(safeRole) || 0) + 1;
      layerCounts.set(safeRole, ordinal);
      node.setAttribute("data-layer-role", role);
      node.setAttribute("data-layer-id", `${ctx.config.exampleId}--${safeRole}-${ordinal}`);
    }
  }

  function addBrandLockup(group, ctx, y) {
    addText(group, ctx, {
      className: "brand-lockup",
      text: ctx.config.brand,
      x: 240,
      y: y == null ? 246 : y,
      size: fittedFontSize(ctx.config.brand, 32, 330),
      weight: 750,
      tracking: 1.2,
      fill: ctx.palette.roles.ink,
      maxWidth: 330,
      minimumSize: 8
    });
    ctx.brandHandled = true;
  }

  function addTagline(group, ctx, y) {
    if (!ctx.config.tagline) {
      ctx.taglineHandled = true;
      return;
    }
    addText(group, ctx, {
      className: "tagline-lockup",
      text: ctx.config.tagline,
      x: 240,
      y: y == null ? 282 : y,
      size: fittedFontSize(ctx.config.tagline, 13, 330),
      weight: 500,
      tracking: 1.35,
      fill: ctx.palette.sequence[1 % ctx.palette.sequence.length],
      maxWidth: 330,
      minimumSize: 9,
      maxLines: 2,
      lineHeight: 12
    });
    ctx.taglineHandled = true;
  }

  function originalAnimalPoints(curvature) {
    const lift = (curvature - 0.5) * 12;
    return [
      [112, 158], [143, 143 - lift * 0.25], [176, 121 - lift], [224, 116 - lift],
      [267, 123 - lift * 0.65], [296, 113 - lift * 0.4], [304, 96 - lift], [316, 119],
      [343, 137], [324, 153], [298, 157], [280, 177], [291, 207], [270, 207],
      [250, 178], [210, 176], [194, 207], [173, 207], [179, 173], [147, 167]
    ];
  }

  function originalAnimalPath(ctx) {
    return ctx.d3.line()
      .curve(ctx.d3.curveCatmullRomClosed.alpha(0.35 + ctx.config.curvature * 0.5))
      (originalAnimalPoints(ctx.config.curvature));
  }

  function renderTypeOrbit(group, ctx) {
    if (ctx.smallSize) {
      group.attr("data-small-size-lockup", "compact-horizontal");
      group.append("circle")
        .attr("class", "orbit-compact-ring")
        .attr("cx", 108)
        .attr("cy", 145)
        .attr("r", 78)
        .attr("fill", ctx.textureFill)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 5);
      group.append("circle")
        .attr("class", "orbit-compact-core")
        .attr("cx", 108)
        .attr("cy", 145)
        .attr("r", 61)
        .attr("fill", ctx.palette.roles.primary);
      addText(group, ctx, {
        className: "orbit-compact-initials",
        text: brandInitials(ctx.config.brand),
        x: 108,
        y: 145,
        size: 64,
        weight: 850,
        fill: ctx.palette.roles.surface
      });
      addText(group, ctx, {
        className: "orbit-compact-wordmark",
        text: ctx.config.brand,
        x: 208,
        y: 145,
        anchor: "start",
        size: fittedFontSize(ctx.config.brand, 42, 236),
        weight: 800,
        fill: ctx.palette.roles.ink
      });
      group.attr("data-small-size-tagline", "hidden");
      ctx.brandHandled = true;
      ctx.taglineHandled = true;
      return;
    }
    const pathId = ctx.uid("orbit-text-path");
    const radius = 74 + ctx.config.curvature * 24;
    const startX = 240 - radius;
    ctx.defs.append("path")
      .attr("id", pathId)
      .attr("d", `M${startX},145a${radius},${radius} 0 1,1 ${radius * 2},0a${radius},${radius} 0 1,1 ${-radius * 2},0`);
    group.append("circle")
      .attr("class", "orbit-core")
      .attr("cx", 240)
      .attr("cy", 145)
      .attr("r", 52)
      .attr("fill", ctx.textureFill)
      .attr("stroke", ctx.palette.roles.ink)
      .attr("stroke-width", 3);
    group.append("circle")
      .attr("class", "orbit-guide")
      .attr("cx", 240)
      .attr("cy", 145)
      .attr("r", radius)
      .attr("fill", "none")
      .attr("stroke", ctx.palette.sequence[1 % ctx.palette.sequence.length])
      .attr("stroke-width", 1.5);
    const text = group.append("text")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 18, radius * 3.9))
      .attr("font-weight", 700)
      .attr("letter-spacing", 2.2)
      .attr("fill", ctx.palette.roles.ink);
    text.append("textPath")
      .attr("href", `#${pathId}`)
      .attr("startOffset", "50%")
      .attr("text-anchor", "middle")
      .text(`${ctx.config.brand} · ${ctx.config.tagline || ctx.config.brand} ·`);
    addText(group, ctx, { className: "orbit-initials", text: brandInitials(ctx.config.brand), x: 240, y: 145, size: 34, weight: 800, fill: ctx.palette.roles.surface });
    ctx.brandHandled = true;
    ctx.taglineHandled = true;
  }

  function renderBezierWordpath(group, ctx) {
    const pathId = ctx.uid("bezier-wordpath");
    const lift = 45 + ctx.config.curvature * 75;
    const pathData = `M58,184 C150,${184 - lift} 308,${184 + lift * 0.45} 422,132`;
    ctx.defs.append("path").attr("id", pathId).attr("d", pathData);
    group.append("path")
      .attr("class", "bezier-baseline")
      .attr("d", pathData)
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 11)
      .attr("stroke-linecap", "round");
    const text = group.append("text")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 42, 335))
      .attr("font-weight", 800)
      .attr("letter-spacing", 1.4)
      .attr("fill", ctx.palette.roles.ink);
    text.append("textPath")
      .attr("href", `#${pathId}`)
      .attr("startOffset", "50%")
      .attr("text-anchor", "middle")
      .attr("dy", -10)
      .text(ctx.config.brand);
    group.selectAll("circle.bezier-terminal")
      .data([[58, 184], [422, 132]])
      .join("circle")
      .attr("class", "bezier-terminal")
      .attr("cx", (d) => d[0])
      .attr("cy", (d) => d[1])
      .attr("r", 6)
      .attr("fill", ctx.palette.sequence[1]);
    ctx.brandHandled = true;
  }

  function renderVariableAxisWordmark(group, ctx) {
    group.attr("data-axis-mode", "fallback");
    const glyphs = Array.from(ctx.config.brand);
    const size = fittedFontSize(ctx.config.brand, 66, 360);
    const weightScale = ctx.d3.scaleLinear().domain([0, Math.max(1, glyphs.length - 1)]).range([540, 860]);
    const strongColors = [
      ctx.palette.roles.inkDark,
      ctx.palette.roles.primary,
      ctx.palette.roles.primaryDark,
      ctx.palette.roles.secondaryDark || ctx.palette.roles.ink,
      ctx.palette.roles.special || ctx.palette.roles.ink
    ];
    const glyphData = glyphs.map((glyph, index) => ({
      glyph,
      index,
      baseSize: size * (0.92 + index % 3 * 0.05)
    }));
    const glyphSelection = group.selectAll("text.axis-glyph")
      .data(glyphData)
      .join("text")
      .attr("class", "axis-glyph")
      .attr("data-text-layer-suffix", (d) => `glyph-${d.index + 1}`)
      .attr("x", 0)
      .attr("y", (d) => 151 + Math.sin(d.index * 0.8) * ctx.config.curvature * 7)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", (d) => d.baseSize)
      .attr("font-weight", (d) => Math.round(weightScale(d.index)))
      .attr("letter-spacing", 0)
      .attr("fill", (d) => strongColors[d.index % strongColors.length])
      .text((d) => d.glyph);

    const measureGlyphs = () => glyphSelection.nodes().map((node, index) => {
      const renderedSize = finiteNumber(node.getAttribute("font-size"), glyphData[index].baseSize);
      if (/\s/u.test(glyphData[index].glyph)) return renderedSize * 0.36;
      try {
        const measured = Number(node.getComputedTextLength());
        if (Number.isFinite(measured) && measured > 0) return measured;
      } catch (error) {
        // Detached renderers use the deterministic width fallback below.
      }
      return renderedSize * 0.59;
    });
    const gap = clamp(7.2 - glyphs.length * 0.08 + (ctx.config.density - 1) * 0.3, 5, 7);
    let widths = measureGlyphs();
    const availableGlyphWidth = Math.max(48, 330 - gap * Math.max(0, glyphs.length - 1));
    const measuredGlyphWidth = widths.reduce((sum, width) => sum + width, 0);
    let commonScale = Math.min(1, availableGlyphWidth / Math.max(1, measuredGlyphWidth));
    glyphSelection.attr("font-size", (d) => d.baseSize * commonScale);
    widths = measureGlyphs();
    let totalWidth = widths.reduce((sum, width) => sum + width, 0) + gap * Math.max(0, glyphs.length - 1);
    if (totalWidth > 330) {
      const correction = availableGlyphWidth / Math.max(1, widths.reduce((sum, width) => sum + width, 0));
      commonScale *= correction;
      glyphSelection.attr("font-size", (d) => d.baseSize * commonScale);
      widths = measureGlyphs();
      totalWidth = widths.reduce((sum, width) => sum + width, 0) + gap * Math.max(0, glyphs.length - 1);
    }
    let cursor = 240 - totalWidth / 2;
    glyphSelection.attr("x", (d, index) => {
      const center = cursor + widths[index] / 2;
      cursor += widths[index] + gap;
      return center;
    });
    group.attr("data-axis-scale", commonScale.toFixed(4)).attr("data-axis-gap", gap.toFixed(2));
    group.append("rect")
      .attr("class", "axis-rule")
      .attr("x", 240 - totalWidth / 2)
      .attr("y", 194)
      .attr("width", Math.max(72, totalWidth))
      .attr("height", 7)
      .attr("fill", ctx.textureFill);
    ctx.brandHandled = true;
  }

  function renderLigatureBridge(group, ctx) {
    const initials = Array.from(brandInitials(ctx.config.brand));
    const left = initials[0] || "A";
    const right = initials[1] || left;
    addText(group, ctx, { className: "ligature-left", text: left, x: 164, y: 143, size: 92, weight: 800, fill: ctx.palette.roles.ink });
    addText(group, ctx, { className: "ligature-right", text: right, x: 316, y: 143, size: 92, weight: 800, fill: ctx.palette.roles.ink });
    const bend = 34 + ctx.config.curvature * 56;
    group.append("path")
      .attr("class", "ligature-connector")
      .attr("d", `M196,155 C220,${155 - bend} 260,${155 + bend} 284,133`)
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 12 + ctx.config.density * 4)
      .attr("stroke-linecap", "round");
    group.selectAll("circle.ligature-anchor")
      .data([[196, 155], [284, 133]])
      .join("circle")
      .attr("class", "ligature-anchor")
      .attr("cx", (d) => d[0])
      .attr("cy", (d) => d[1])
      .attr("r", 5)
      .attr("fill", ctx.palette.roles.accent);
  }

  function renderStencilCuts(group, ctx) {
    const maskId = ctx.uid("stencil-mask");
    const mask = ctx.defs.append("mask")
      .attr("id", maskId)
      .attr("maskUnits", "userSpaceOnUse")
      .attr("x", 44)
      .attr("y", 82)
      .attr("width", 392)
      .attr("height", 134);
    mask.append("text")
      .attr("x", 240)
      .attr("y", 164)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 78, 370))
      .attr("font-weight", 900)
      .attr("letter-spacing", 1)
      .attr("fill", ctx.palette.roles.surface)
      .text(ctx.config.brand);
    const cutCount = Math.max(4, Math.round(6 * ctx.config.density));
    mask.selectAll("rect.stencil-cut")
      .data(ctx.d3.range(cutCount))
      .join("rect")
      .attr("class", "stencil-cut")
      .attr("x", (d) => 82 + d * 310 / Math.max(1, cutCount - 1))
      .attr("y", 92)
      .attr("width", 7 + ctx.config.curvature * 8)
      .attr("height", 136)
      .attr("fill", ctx.palette.allowed[0])
      .attr("transform", (d) => `rotate(${-18 + ctx.config.rotation * 0.12} ${82 + d * 310 / Math.max(1, cutCount - 1)} 160)`);
    group.append("rect")
      .attr("class", "stencil-wordmark")
      .attr("data-text-proxy", "mask-proxy")
      .attr("data-text-role", "brand")
      .attr("x", 44)
      .attr("y", 82)
      .attr("width", 392)
      .attr("height", 134)
      .attr("fill", ctx.textureFill)
      .attr("mask", fragmentUrl(maskId));
    ctx.brandHandled = true;
  }

  function renderLetterWindow(group, ctx) {
    const clipId = ctx.uid("letter-window-clip");
    const size = fittedFontSize(ctx.config.brand, 112, 374);
    const clip = ctx.defs.append("clipPath")
      .attr("id", clipId)
      .attr("clipPathUnits", "userSpaceOnUse");
    clip.append("text")
      .attr("x", 240)
      .attr("y", 151)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", size)
      .attr("font-weight", 900)
      .attr("letter-spacing", -1)
      .text(ctx.config.brand);
    group.append("rect")
      .attr("class", "letter-window-surface")
      .attr("data-text-proxy", "clip-proxy")
      .attr("data-text-role", "brand")
      .attr("x", 42)
      .attr("y", 74)
      .attr("width", 396)
      .attr("height", 158)
      .attr("fill", ctx.textureFill)
      .attr("clip-path", fragmentUrl(clipId));
    addText(group, ctx, { className: "letter-window-outline", text: ctx.config.brand, x: 240, y: 151, size, weight: 900, fill: "none" })
      .attr("stroke", ctx.palette.roles.ink)
      .attr("stroke-width", 1.5);
    ctx.brandHandled = true;
  }

  function renderMirroredMonogram(group, ctx) {
    const initial = Array.from(brandInitials(ctx.config.brand))[0] || "A";
    const mark = group.append("g").attr("class", "mirrored-axis-mark").attr("transform", "translate(240,145)");
    mark.append("line")
      .attr("x1", 0).attr("y1", -82).attr("x2", 0).attr("y2", 82)
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2);
    mark.append("text")
      .attr("class", "mirror-initial")
      .attr("x", -3).attr("y", 0).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 800)
      .attr("fill", ctx.textureFill).text(initial);
    mark.append("text")
      .attr("class", "mirror-initial")
      .attr("x", -3).attr("y", 0).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 800)
      .attr("fill", ctx.palette.roles.primaryDark)
      .attr("transform", `scale(-1,1) translate(${-18 * ctx.config.curvature},0)`).text(initial);
    mark.append("circle").attr("class", "mirror-joint").attr("cx", 0).attr("cy", 0).attr("r", 7).attr("fill", ctx.palette.roles.accent);
  }

  function renderGlyphRosette(group, ctx) {
    const glyph = Array.from(brandInitials(ctx.config.brand))[0] || "A";
    const centerY = 132;
    const count = clamp(Math.round(8 + ctx.config.density * 4.5), 10, 16);
    const radius = 78 + clamp((ctx.config.density - 1) * 5, 0, 5);
    const arcLength = Math.PI * 2 * radius / count;
    const glyphSize = clamp(arcLength * 0.55, 16, 22);
    const strongColors = [
      ctx.palette.roles.inkDark,
      ctx.palette.roles.primary,
      ctx.palette.roles.primaryDark,
      ctx.palette.roles.secondaryDark || ctx.palette.roles.ink,
      ctx.palette.roles.special || ctx.palette.roles.ink
    ];
    group.selectAll("text.rosette-glyph")
      .data(ctx.d3.range(count))
      .join("text")
      .attr("class", "rosette-glyph")
      .attr("data-text-layer-suffix", (d) => `glyph-${d + 1}`)
      .attr("x", 240)
      .attr("y", centerY - radius)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", (d) => glyphSize * (d % 2 ? 0.9 : 1))
      .attr("font-weight", 850)
      .attr("fill", (d) => strongColors[d % strongColors.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 1.8)
      .attr("paint-order", "stroke fill")
      .attr("transform", (d) => `rotate(${d * 360 / count} 240 ${centerY})`)
      .text(glyph);
    group.append("circle")
      .attr("class", "rosette-core")
      .attr("cx", 240).attr("cy", centerY).attr("r", 36)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    addText(group, ctx, { className: "rosette-initials", text: brandInitials(ctx.config.brand), x: 240, y: centerY, size: 24, weight: 850, fill: ctx.palette.roles.surface });
  }

  function renderBaselineWave(group, ctx) {
    const glyphs = Array.from(ctx.config.brand);
    const left = 62;
    const right = 418;
    const amplitude = 18 + ctx.config.curvature * 38;
    const frequency = 1.25 + ctx.config.density * 0.55;
    const xFor = (index) => glyphs.length < 2 ? 240 : left + index * (right - left) / (glyphs.length - 1);
    const yFor = (index) => 146 + Math.sin(index / Math.max(1, glyphs.length - 1) * Math.PI * 2 * frequency) * amplitude;
    const areaData = ctx.d3.range(41).map((index) => {
      const x = left + index * (right - left) / 40;
      const y = 146 + Math.sin(index / 40 * Math.PI * 2 * frequency) * amplitude;
      return [x, y];
    });
    group.append("path")
      .attr("class", "wave-ribbon")
      .attr("d", ctx.d3.area().x((d) => d[0]).y0((d) => d[1] + 14).y1((d) => d[1] + 25).curve(ctx.d3.curveBasis)(areaData))
      .attr("fill", ctx.textureFill);
    group.selectAll("text.wave-glyph")
      .data(glyphs)
      .join("text")
      .attr("class", "wave-glyph")
      .attr("x", (d, index) => xFor(index))
      .attr("y", (d, index) => yFor(index))
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 44, 350))
      .attr("font-weight", 800)
      .attr("fill", ctx.palette.roles.ink)
      .attr("transform", (d, index) => {
        const next = Math.min(glyphs.length - 1, index + 1);
        const angle = Math.atan2(yFor(next) - yFor(index), Math.max(1, xFor(next) - xFor(index))) * 180 / Math.PI;
        return `rotate(${angle} ${xFor(index)} ${yFor(index)})`;
      })
      .text((d) => d);
    ctx.brandHandled = true;
  }

  function renderStackOffset(group, ctx) {
    const copies = clamp(Math.round(3 + ctx.config.density * 2.4), 4, 7);
    const center = (copies - 1) / 2;
    const offsetX = 3.6 + ctx.config.curvature * 1.6;
    const offsetY = 4.2 + ctx.config.curvature * 1.8;
    const effectiveRotation = ctx.config.rotation;
    const angle = Math.abs(effectiveRotation) * Math.PI / 180;
    const glyphWidthFactor = Math.max(1, Array.from(ctx.config.brand).length * 0.59);
    const availableWidth = Math.max(120, 2 * (180 / ctx.config.scale - center * offsetX));
    const availableHeight = Math.max(70, 2 * (78 / ctx.config.scale - center * offsetY));
    const widthBound = availableWidth / (glyphWidthFactor * Math.cos(angle) + Math.sin(angle));
    const heightBound = availableHeight / (glyphWidthFactor * Math.sin(angle) + Math.cos(angle));
    const size = clamp(Math.min(68, widthBound, heightBound), 14, 68);
    const stack = group.append("g")
      .attr("class", "stack-safe-area")
      .attr("data-effective-rotation", effectiveRotation);
    stack.selectAll("text.stack-copy")
      .data(ctx.d3.range(copies).reverse())
      .join("text")
      .attr("class", "stack-copy")
      .attr("x", (d) => 240 + (d - center) * offsetX)
      .attr("y", (d) => 150 + (d - center) * offsetY)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", size)
      .attr("font-weight", 900)
      .attr("letter-spacing", 0.6)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[d % ctx.palette.sequence.length])
      .text(ctx.config.brand);
    ctx.brandHandled = true;
  }

  function renderSliceShift(group, ctx) {
    const textId = ctx.uid("slice-source-text");
    const size = fittedFontSize(ctx.config.brand, 82, 365);
    ctx.defs.append("text")
      .attr("id", textId)
      .attr("x", 240).attr("y", 153)
      .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", size).attr("font-weight", 900)
      .text(ctx.config.brand);
    const slices = Math.max(4, Math.round(5 + ctx.config.density * 2));
    const top = 96;
    const height = 118 / slices;
    ctx.d3.range(slices).forEach((index) => {
      const clipId = ctx.uid(`slice-clip-${index}`);
      ctx.defs.append("clipPath")
        .attr("id", clipId)
        .append("rect")
        .attr("x", 42).attr("y", top + index * height).attr("width", 396).attr("height", height + 1)
        .attr("transform", `skewX(${-10 + ctx.config.curvature * 20})`);
      group.append("use")
        .attr("class", "shifted-slice")
        .attr("href", `#${textId}`)
        .attr("clip-path", fragmentUrl(clipId))
        .attr("transform", `translate(${(index % 2 ? 1 : -1) * (8 + ctx.config.curvature * 16)},0)`)
        .attr("fill", index === Math.floor(slices / 2) ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    });
    ctx.brandHandled = true;
  }

  function renderMultiStrokeWordmark(group, ctx) {
    const textId = ctx.uid("multi-stroke-source");
    const size = fittedFontSize(ctx.config.brand, 74, 350);
    ctx.defs.append("text")
      .attr("id", textId)
      .attr("x", 240).attr("y", 151)
      .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", size).attr("font-weight", 850)
      .text(ctx.config.brand);
    const layers = [
      { width: 11, dash: "2 9", color: ctx.palette.roles.line },
      { width: 7, dash: "14 5", color: ctx.palette.roles.primaryDark },
      { width: 3, dash: "1 0", color: ctx.palette.roles.ink }
    ];
    group.selectAll("use.stroke-layer")
      .data(layers)
      .join("use")
      .attr("class", "stroke-layer")
      .attr("href", `#${textId}`)
      .attr("fill", "none")
      .attr("stroke", (d) => d.color)
      .attr("stroke-width", (d) => d.width)
      .attr("stroke-dasharray", (d) => d.dash)
      .attr("stroke-linejoin", "round");
    group.append("use").attr("class", "stroke-fill").attr("href", `#${textId}`).attr("fill", ctx.textureFill);
    ctx.brandHandled = true;
  }

  function renderExtrudedWordmark(group, ctx) {
    const steps = Math.max(5, Math.round(7 + ctx.config.density * 6));
    const size = fittedFontSize(ctx.config.brand, 69, 340);
    const angle = (-28 + ctx.config.curvature * 16) * Math.PI / 180;
    group.selectAll("text.depth-copy")
      .data(ctx.d3.range(steps).reverse())
      .join("text")
      .attr("class", "depth-copy")
      .attr("x", (d) => 240 + Math.cos(angle) * d * 3.2)
      .attr("y", (d) => 151 + Math.sin(angle) * d * 3.2)
      .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", size).attr("font-weight", 900)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[(d + 1) % ctx.palette.sequence.length])
      .attr("stroke", (d) => d === 0 ? ctx.palette.roles.ink : "none")
      .attr("stroke-width", 1.4)
      .text(ctx.config.brand);
    ctx.brandHandled = true;
  }

  function renderLetterWeave(group, ctx) {
    const initials = Array.from(brandInitials(ctx.config.brand).padEnd(2, "A"));
    const bendA = ((initials[0].charCodeAt(0) % 13) - 6) * 2;
    const bendB = ((initials[1].charCodeAt(0) % 13) - 6) * 2;
    group.attr("data-weave-initials", initials.slice(0, 2).join(""));
    const maskId = ctx.uid("weave-crossing-mask");
    const mask = ctx.defs.append("mask")
      .attr("id", maskId)
      .attr("maskUnits", "userSpaceOnUse")
      .attr("x", 100).attr("y", 54).attr("width", 280).attr("height", 190);
    mask.append("rect").attr("x", 100).attr("y", 54).attr("width", 280).attr("height", 190).attr("fill", ctx.palette.roles.surface);
    mask.selectAll("circle")
      .data([[215, 140], [278, 156]])
      .join("circle")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 13 + ctx.config.curvature * 7)
      .attr("fill", ctx.palette.allowed[0]);
    const line = ctx.d3.line().curve(ctx.d3.curveBasis);
    const pathA = line([[128, 204], [162 + bendA, 76], [238, 192 - bendB], [310 - bendA, 78], [350, 201]]);
    const pathB = line([[126, 88], [195, 204 - bendA], [240 + bendB, 94], [286, 204 + bendA], [354, 92]]);
    group.append("path")
      .attr("class", "weave-under")
      .attr("d", pathB).attr("fill", "none").attr("stroke", ctx.palette.roles.primaryDark)
      .attr("stroke-width", 23).attr("stroke-linecap", "square");
    group.append("path")
      .attr("class", "weave-over")
      .attr("d", pathA).attr("fill", "none").attr("stroke", ctx.textureFill)
      .attr("stroke-width", 23).attr("stroke-linecap", "square").attr("mask", fragmentUrl(maskId));
    group.selectAll("circle.weave-terminal")
      .data([[128, 204], [350, 201], [126, 88], [354, 92]])
      .join("circle").attr("class", "weave-terminal")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 6).attr("fill", ctx.palette.roles.accent);
  }

  function renderResponsiveLockup(group, ctx) {
    const mode = ctx.effectiveWidth < 180 ? "compact" : (ctx.effectiveWidth < 360 ? "stacked" : "wide");
    const taglineFill = ctx.palette.roles.secondaryDark || ctx.palette.roles.ink;
    group.attr("data-lockup-mode", mode);
    const symbol = group.append("g").attr("class", `responsive-symbol responsive-symbol-${mode}`);
    const cells = [[0, 0], [1, 0], [0, 1], [1, 1]];
    const origin = mode === "wide" ? [104, 112] : [208, mode === "stacked" ? 68 : 86];
    symbol.selectAll("rect")
      .data(cells)
      .join("rect")
      .attr("x", (d) => origin[0] + d[0] * 36)
      .attr("y", (d) => origin[1] + d[1] * 36)
      .attr("width", 32).attr("height", 32)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    if (mode === "wide") {
      addText(group, ctx, { className: "responsive-brand", text: ctx.config.brand, x: 278, y: 137, size: fittedFontSize(ctx.config.brand, 47, 230), weight: 850, fill: ctx.palette.roles.ink });
      addText(group, ctx, { className: "responsive-tagline", text: ctx.config.tagline, x: 278, y: 176, size: fittedFontSize(ctx.config.tagline, 14, 220), weight: 650, tracking: 0.7, fill: taglineFill });
    } else if (mode === "stacked") {
      addText(group, ctx, { className: "responsive-brand", text: ctx.config.brand, x: 240, y: 196, size: fittedFontSize(ctx.config.brand, 42, 280), weight: 850, fill: ctx.palette.roles.ink });
      addText(group, ctx, { className: "responsive-tagline", text: ctx.config.tagline, x: 240, y: 228, size: fittedFontSize(ctx.config.tagline, 13, 270), weight: 650, tracking: 0.7, fill: taglineFill });
    } else {
      addText(group, ctx, { className: "responsive-initials", text: brandInitials(ctx.config.brand), x: 240, y: 124, size: 24, weight: 900, fill: ctx.palette.roles.surface });
      addText(group, ctx, { className: "responsive-brand", text: ctx.config.brand, x: 240, y: 208, size: fittedFontSize(ctx.config.brand, 30, 250), weight: 850, fill: ctx.palette.roles.ink });
    }
    ctx.brandHandled = true;
    ctx.taglineHandled = true;
  }

  function renderSpiralTrace(group, ctx) {
    const samples = Math.max(90, Math.round(120 * ctx.config.density));
    const turns = 2.4 + ctx.config.curvature * 2.6;
    const points = ctx.d3.range(samples).map((index) => {
      const t = index / (samples - 1);
      return {
        angle: t * Math.PI * 2 * turns,
        radius: 8 + t * (84 + ctx.config.curvature * 22)
      };
    });
    const spiral = ctx.d3.lineRadial()
      .angle((d) => d.angle)
      .radius((d) => d.radius)
      .curve(ctx.d3.curveCatmullRom.alpha(0.55));
    const mark = group.append("g").attr("class", "spiral-trace-mark").attr("transform", "translate(240,143)");
    mark.append("path")
      .attr("d", spiral(points))
      .attr("fill", "none")
      .attr("stroke", ctx.palette.roles.ink)
      .attr("stroke-width", 13)
      .attr("stroke-linecap", "round");
    mark.append("path")
      .attr("d", spiral(points))
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 8)
      .attr("stroke-linecap", "round");
    const finalPoint = points[points.length - 1];
    const terminal = ctx.d3.pointRadial(finalPoint.angle, finalPoint.radius);
    mark.append("circle")
      .attr("class", "spiral-terminal")
      .attr("cx", terminal[0]).attr("cy", terminal[1]).attr("r", 7)
      .attr("fill", ctx.palette.roles.accent);
  }

  function renderOrbitNetwork(group, ctx) {
    const count = Math.max(7, Math.round(9 + ctx.config.density * 5));
    const random = seededRandom(ctx.d3, ctx.config.seed, "orbit-network");
    const nodes = [{ id: "core", x: 240, y: 143, fx: 240, fy: 143, r: 25 }]
      .concat(ctx.d3.range(count).map((index) => ({
        id: `node-${index}`,
        x: 240 + (random() - 0.5) * 160,
        y: 143 + (random() - 0.5) * 160,
        r: 7 + random() * 7
      })));
    const links = ctx.d3.range(count).map((index) => ({ source: "core", target: `node-${index}` }));
    for (let index = 0; index < count; index += 3) {
      links.push({ source: `node-${index}`, target: `node-${(index + 2) % count}` });
    }
    const simulation = ctx.d3.forceSimulation(nodes)
      .randomSource(ctx.d3.randomLcg(((ctx.config.seed >>> 0) ^ 0x51f15e) >>> 0))
      .force("charge", ctx.d3.forceManyBody().strength(-32))
      .force("radial", ctx.d3.forceRadial((d, index) => index === 0 ? 0 : 70 + index % 3 * 22, 240, 143).strength(0.72))
      .force("link", ctx.d3.forceLink(links).id((d) => d.id).distance((d, index) => 58 + index % 4 * 9).strength(0.2))
      .force("collide", ctx.d3.forceCollide((d) => d.r + 4).iterations(2))
      .stop();
    for (let tick = 0; tick < 120; tick += 1) simulation.tick();
    group.append("g")
      .attr("class", "orbit-links")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("x1", (d) => d.source.x).attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x).attr("y2", (d) => d.target.y)
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2.2);
    group.append("g")
      .attr("class", "orbit-nodes")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => d.r)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
    addText(group, ctx, { className: "orbit-network-initials", text: brandInitials(ctx.config.brand), x: 240, y: 143, size: 14, weight: 850, fill: ctx.palette.roles.surface });
  }

  function renderGridActivation(group, ctx) {
    const columns = Math.max(8, Math.round(9 + ctx.config.density * 5));
    const rows = Math.max(5, Math.round(6 + ctx.config.density * 3));
    const cell = Math.min(28, 300 / columns);
    const gap = 4;
    const width = columns * cell;
    const height = rows * cell;
    const left = 240 - width / 2;
    const top = 143 - height / 2;
    const random = seededRandom(ctx.d3, ctx.config.seed, "grid-activation");
    const cells = [];
    for (let row = 0; row < rows; row += 1) {
      for (let column = 0; column < columns; column += 1) {
        const diagonal = Math.abs(column / Math.max(1, columns - 1) - row / Math.max(1, rows - 1));
        const ring = Math.abs(Math.hypot(column - columns / 2, row - rows / 2) - Math.min(columns, rows) * 0.3);
        cells.push({ row, column, active: diagonal < 0.16 || ring < 0.7 || random() < 0.13 * ctx.config.density });
      }
    }
    group.append("g").attr("class", "activation-grid")
      .selectAll("rect")
      .data(cells)
      .join("rect")
      .attr("x", (d) => left + d.column * cell + gap / 2)
      .attr("y", (d) => top + d.row * cell + gap / 2)
      .attr("width", cell - gap).attr("height", cell - gap)
      .attr("fill", (d, index) => d.active ? (index % 7 === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]) : ctx.palette.roles.quiet)
      .attr("data-active", (d) => d.active ? "true" : "false");
  }

  function renderContourFingerprint(group, ctx) {
    const gridWidth = 46;
    const gridHeight = 30;
    const random = seededRandom(ctx.d3, ctx.config.seed, "contour-field");
    const values = [];
    for (let y = 0; y < gridHeight; y += 1) {
      for (let x = 0; x < gridWidth; x += 1) {
        const dx = (x - gridWidth / 2) / gridWidth;
        const dy = (y - gridHeight / 2) / gridHeight;
        const radial = Math.exp(-(dx * dx * 5 + dy * dy * 8));
        const ridges = Math.sin(x * 0.42 + Math.cos(y * 0.31) * 2.2) * 0.13;
        values.push(radial + ridges + (random() - 0.5) * 0.035);
      }
    }
    const thresholdCount = Math.max(8, Math.round(10 + ctx.config.density * 8));
    const thresholds = ctx.d3.range(thresholdCount).map((index) => 0.08 + index * 0.76 / thresholdCount);
    const contours = ctx.d3.contours().size([gridWidth, gridHeight]).smooth(true).thresholds(thresholds)(values);
    const clipId = ctx.uid("contour-medallion-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("ellipse")
      .attr("cx", 240).attr("cy", 143).attr("rx", 122).attr("ry", 93);
    group.append("ellipse")
      .attr("class", "contour-field-base")
      .attr("cx", 240).attr("cy", 143).attr("rx", 122).attr("ry", 93)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    const contourGroup = group.append("g")
      .attr("class", "scalar-field-contours")
      .attr("clip-path", fragmentUrl(clipId))
      .attr("transform", `translate(102,53) scale(${276 / gridWidth},${180 / gridHeight})`);
    contourGroup.selectAll("path")
      .data(contours)
      .join("path")
      .attr("d", ctx.d3.geoPath())
      .attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", 0.48)
      .attr("vector-effect", "non-scaling-stroke");
  }

  function renderVoronoiShards(group, ctx) {
    const random = seededRandom(ctx.d3, ctx.config.seed, "voronoi-shards");
    const count = Math.max(14, Math.round(18 + ctx.config.density * 12));
    const sites = ctx.d3.range(count).map(() => [128 + random() * 224, 42 + random() * 202]);
    const voronoi = ctx.d3.Delaunay.from(sites).voronoi([120, 35, 360, 251]);
    const clipId = ctx.uid("voronoi-shard-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("path")
      .attr("d", `M240,39 C315,39 361,85 361,143 C361,205 310,247 240,247 C170,247 119,205 119,143 C119,85 165,39 240,39Z`);
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("g")
      .attr("class", "voronoi-shard-cells")
      .attr("clip-path", fragmentUrl(clipId))
      .selectAll("path")
      .data(Array.from(voronoi.cellPolygons()))
      .join("path")
      .attr("d", line)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 2.2 + ctx.config.curvature * 1.4);
    group.append("path")
      .attr("class", "voronoi-shard-outline")
      .attr("d", `M240,39 C315,39 361,85 361,143 C361,205 310,247 240,247 C170,247 119,205 119,143 C119,85 165,39 240,39Z`)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderAnimalFacets(group, ctx) {
    const animalPath = originalAnimalPath(ctx);
    const polygon = originalAnimalPoints(ctx.config.curvature);
    const clipId = ctx.uid("animal-facet-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("path").attr("d", animalPath);
    const random = seededRandom(ctx.d3, ctx.config.seed, "animal-facets");
    const target = Math.max(22, Math.round(25 + ctx.config.density * 18));
    const points = polygon.slice();
    let attempts = 0;
    while (points.length < target && attempts < target * 30) {
      const point = [112 + random() * 232, 94 + random() * 116];
      if (ctx.d3.polygonContains(polygon, point)) points.push(point);
      attempts += 1;
    }
    const delaunay = ctx.d3.Delaunay.from(points);
    const triangles = Array.from(delaunay.trianglePolygons());
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("g")
      .attr("class", "animal-delaunay-facets")
      .attr("clip-path", fragmentUrl(clipId))
      .selectAll("path")
      .data(triangles)
      .join("path")
      .attr("d", line)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 1.7);
    group.append("path")
      .attr("class", "original-animal-outline")
      .attr("data-original-procedural", "true")
      .attr("d", animalPath).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3.5).attr("stroke-linejoin", "round");
  }

  function renderAnimalSurfaceMask(group, ctx) {
    const animalPath = originalAnimalPath(ctx);
    const clipId = ctx.uid("animal-surface-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("path").attr("d", animalPath);
    const surface = group.append("g")
      .attr("class", "animal-surface-bands")
      .attr("clip-path", fragmentUrl(clipId));
    surface.append("rect").attr("x", 104).attr("y", 88).attr("width", 248).attr("height", 128).attr("fill", ctx.textureFill);
    const bandCount = Math.max(6, Math.round(7 + ctx.config.density * 5));
    const line = ctx.d3.line().curve(ctx.d3.curveBasis);
    const bands = ctx.d3.range(bandCount).map((index) => ctx.d3.range(9).map((column) => [
      104 + column * 31,
      103 + index * 104 / Math.max(1, bandCount - 1) + Math.sin(column * 0.9 + index) * (5 + ctx.config.curvature * 10)
    ]));
    surface.selectAll("path")
      .data(bands)
      .join("path")
      .attr("d", line).attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length])
      .attr("stroke-width", 10).attr("stroke-linecap", "round");
    group.append("path")
      .attr("class", "original-animal-outline")
      .attr("data-original-procedural", "true")
      .attr("d", animalPath).attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3.5);
  }

  function renderNegativeSpaceReveal(group, ctx) {
    const maskId = ctx.uid("negative-space-mask");
    const initial = Array.from(brandInitials(ctx.config.brand))[0] || "A";
    const mask = ctx.defs.append("mask")
      .attr("id", maskId).attr("maskUnits", "userSpaceOnUse")
      .attr("x", 105).attr("y", 40).attr("width", 270).attr("height", 210);
    mask.selectAll("circle")
      .data([[190, 135, 76], [290, 135, 76], [240, 182, 66]])
      .join("circle")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", (d) => d[2])
      .attr("fill", ctx.palette.roles.surface);
    mask.append("text")
      .attr("x", 240).attr("y", 147).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 900)
      .attr("fill", ctx.palette.allowed[0]).text(initial);
    group.append("g")
      .attr("class", "negative-space-primitives")
      .attr("data-text-proxy", "negative-space")
      .attr("data-text-role", "initials")
      .attr("mask", fragmentUrl(maskId))
      .selectAll("circle")
      .data([[190, 135, 76], [290, 135, 76], [240, 182, 66]])
      .join("circle")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", (d) => d[2])
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    group.append("text")
      .attr("class", "negative-space-outline")
      .attr("data-text-role", "initials")
      .attr("x", 240).attr("y", 147).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 900)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2).text(initial);
  }

  function renderFoldedRibbon(group, ctx) {
    const points = [[86, 187], [153, 92], [224, 187], [294, 92], [394, 178]];
    const line = ctx.d3.line().curve(ctx.d3.curveCatmullRom.alpha(0.25 + ctx.config.curvature * 0.65));
    const ribbon = line(points);
    group.append("path")
      .attr("class", "ribbon-clearance")
      .attr("d", ribbon).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 48).attr("stroke-linecap", "square").attr("stroke-linejoin", "miter");
    group.append("path")
      .attr("class", "ribbon-body")
      .attr("d", ribbon).attr("fill", "none")
      .attr("stroke", ctx.textureFill).attr("stroke-width", 34).attr("stroke-linecap", "square").attr("stroke-linejoin", "miter");
    const overpass = ctx.d3.line().curve(ctx.d3.curveLinear)([[205, 160], [224, 187], [247, 156]]);
    group.append("path")
      .attr("class", "ribbon-overpass-gap")
      .attr("d", overpass).attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 46).attr("stroke-linecap", "square");
    group.append("path")
      .attr("class", "ribbon-overpass")
      .attr("d", overpass).attr("fill", "none").attr("stroke", ctx.palette.roles.primaryDark).attr("stroke-width", 34).attr("stroke-linecap", "square");
    group.selectAll("polygon.ribbon-fold")
      .data([[[139, 103], [153, 92], [169, 111]], [[278, 111], [294, 92], [309, 110]]])
      .join("polygon")
      .attr("class", "ribbon-fold")
      .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
      .attr("fill", ctx.palette.roles.ink);
  }

  function renderBooleanLens(group, ctx) {
    const clipId = ctx.uid("boolean-lens-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("circle").attr("cx", 202).attr("cy", 143).attr("r", 82);
    group.append("circle").attr("class", "boolean-shape-a").attr("cx", 202).attr("cy", 143).attr("r", 82).attr("fill", ctx.palette.roles.primary);
    group.append("circle").attr("class", "boolean-shape-b").attr("cx", 278).attr("cy", 143).attr("r", 82).attr("fill", ctx.palette.sequence[1 % ctx.palette.sequence.length]);
    group.append("circle")
      .attr("class", "boolean-intersection")
      .attr("cx", 278).attr("cy", 143).attr("r", 82)
      .attr("clip-path", fragmentUrl(clipId)).attr("fill", ctx.textureFill);
    group.append("path")
      .attr("class", "boolean-axis")
      .attr("d", "M240,61V225")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
    addText(group, ctx, { className: "boolean-initials", text: brandInitials(ctx.config.brand), x: 240, y: 143, size: 28, weight: 900, fill: ctx.palette.roles.surface });
  }

  function renderRadiantPulse(group, ctx) {
    const count = Math.max(18, Math.round(22 + ctx.config.density * 14));
    const random = seededRandom(ctx.d3, ctx.config.seed, "radiant-pulse");
    const rays = ctx.d3.range(count).map((index) => {
      const angle = index * Math.PI * 2 / count;
      const inner = 47;
      const outer = 72 + random() * 48 + Math.sin(index * 1.7) * 10 * ctx.config.curvature;
      return { angle, inner, outer, width: 1.5 + random() * 3.2 };
    });
    group.append("g").attr("class", "radiant-rays")
      .selectAll("line")
      .data(rays)
      .join("line")
      .attr("x1", (d) => 240 + Math.cos(d.angle) * d.inner)
      .attr("y1", (d) => 143 + Math.sin(d.angle) * d.inner)
      .attr("x2", (d) => 240 + Math.cos(d.angle) * d.outer)
      .attr("y2", (d) => 143 + Math.sin(d.angle) * d.outer)
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d) => d.width).attr("stroke-linecap", "round");
    group.append("circle").attr("class", "radiant-core").attr("cx", 240).attr("cy", 143).attr("r", 43)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    const initials = brandInitials(ctx.config.brand);
    const labelRadius = clamp(22 + ctx.config.density * 2, 23, 27);
    group.append("circle")
      .attr("class", "radiant-label-disc")
      .attr("cx", 240).attr("cy", 143).attr("r", labelRadius)
      .attr("fill", ctx.palette.roles.inkDark)
      .attr("stroke", ctx.palette.roles.surface).attr("stroke-width", 2);
    addText(group, ctx, { className: "radiant-initials", text: initials, x: 240, y: 143, size: fittedFontSize(initials, 27, labelRadius * 1.55), weight: 900, fill: ctx.palette.roles.surface });
  }

  function renderParametricWave(group, ctx) {
    const samples = Math.max(180, Math.round(220 * ctx.config.density));
    const phase = (ctx.config.seed % 360) * Math.PI / 180;
    const frequencyX = 3;
    const frequencyY = 2 + Math.round(ctx.config.curvature * 2);
    const points = ctx.d3.range(samples).map((index) => {
      const t = index / samples * Math.PI * 2;
      return [240 + Math.sin(frequencyX * t + phase) * 116, 143 + Math.sin(frequencyY * t) * 78];
    });
    const line = ctx.d3.line().curve(ctx.d3.curveCatmullRomClosed.alpha(0.5));
    group.append("path")
      .attr("class", "harmonic-curve-shadow")
      .attr("d", line(points)).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 17).attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "harmonic-curve")
      .attr("d", line(points)).attr("fill", "none")
      .attr("stroke", ctx.textureFill).attr("stroke-width", 10).attr("stroke-linejoin", "round");
    group.append("circle").attr("cx", 240).attr("cy", 143).attr("r", 10).attr("fill", ctx.palette.roles.accent);
  }

  function renderKaleidoscopeWedges(group, ctx) {
    const motifId = ctx.uid("kaleidoscope-motif");
    ctx.defs.append("path")
      .attr("id", motifId)
      .attr("d", `M0,-30 C${18 + ctx.config.curvature * 25},-52 ${42 + ctx.config.curvature * 16},-86 0,-116 C-9,-84 -13,-58 0,-30Z`);
    const sectors = Math.max(8, Math.round(10 + ctx.config.density * 6));
    const mark = group.append("g").attr("class", "kaleidoscope-sector-field").attr("transform", "translate(240,143)");
    mark.selectAll("use")
      .data(ctx.d3.range(sectors))
      .join("use")
      .attr("href", `#${motifId}`)
      .attr("transform", (d) => `rotate(${d * 360 / sectors}) scale(${d % 2 ? -1 : 1},1)`)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[d % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.4);
    mark.append("circle").attr("r", 29).attr("fill", ctx.palette.roles.background).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    addText(mark, ctx, { className: "kaleidoscope-initials", text: brandInitials(ctx.config.brand), x: 0, y: 0, size: 18, weight: 900, fill: ctx.palette.roles.ink });
  }

  function renderPolarHalo(group, ctx) {
    const count = Math.max(9, Math.round(10 + ctx.config.density * 6));
    const random = seededRandom(ctx.d3, ctx.config.seed, "polar-halo");
    const gap = 0.035 + (1 - ctx.config.curvature) * 0.04;
    const values = ctx.d3.range(count).map((index) => ({ index, value: 0.35 + random() * 0.65 }));
    const arc = ctx.d3.arc()
      .innerRadius((d) => 64 + d.index % 3 * 8)
      .outerRadius((d) => 76 + d.index % 3 * 8 + d.value * 22)
      .startAngle((d) => d.index * Math.PI * 2 / count + gap)
      .endAngle((d) => (d.index + 1) * Math.PI * 2 / count - gap);
    const mark = group.append("g").attr("class", "polar-data-arcs").attr("transform", "translate(240,143)");
    mark.selectAll("path")
      .data(values)
      .join("path")
      .attr("d", arc)
      .attr("fill", (d) => d.index === 0 ? ctx.textureFill : ctx.palette.sequence[d.index % ctx.palette.sequence.length]);
    mark.append("circle").attr("r", 52).attr("fill", ctx.palette.roles.surface).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    addText(mark, ctx, { className: "polar-initials", text: brandInitials(ctx.config.brand), x: 0, y: -7, size: 28, weight: 900, fill: ctx.palette.roles.ink });
    addText(mark, ctx, { className: "polar-value", text: String(ctx.config.seed), x: 0, y: 23, size: 12, weight: 750, tracking: 0.6, fill: ctx.palette.roles.inkDark });
  }

  function renderApertureIris(group, ctx) {
    const blades = Math.max(7, Math.round(7 + ctx.config.density * 3));
    const outer = 107;
    const inner = 30 + (1 - ctx.config.curvature) * 23;
    const bladePath = `M0,${-outer} C${outer * 0.66},${-outer * 0.84} ${outer},${-outer * 0.18} ${outer * 0.7},${outer * 0.2} L${inner * 0.55},${inner * 0.82} C${inner * 0.1},${inner * 0.45} ${-inner * 0.22},${-inner * 0.28} 0,${-inner}Z`;
    const mark = group.append("g").attr("class", "aperture-blades").attr("transform", "translate(240,151)");
    mark.selectAll("path")
      .data(ctx.d3.range(blades))
      .join("path")
      .attr("d", bladePath)
      .attr("transform", (d) => `rotate(${d * 360 / blades + ctx.config.curvature * 18})`)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[d % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.7);
    mark.append("circle")
      .attr("class", "iris-opening")
      .attr("r", inner).attr("fill", ctx.palette.roles.background)
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    mark.append("circle").attr("r", inner * 0.32).attr("fill", ctx.palette.roles.accent);
  }

  const PATTERN_RENDERERS = Object.freeze({
    "d3-logo-type-orbit": renderTypeOrbit,
    "d3-logo-bezier-wordpath": renderBezierWordpath,
    "d3-logo-variable-axis-wordmark": renderVariableAxisWordmark,
    "d3-logo-ligature-bridge": renderLigatureBridge,
    "d3-logo-stencil-cuts": renderStencilCuts,
    "d3-logo-letter-window": renderLetterWindow,
    "d3-logo-mirrored-monogram": renderMirroredMonogram,
    "d3-logo-glyph-rosette": renderGlyphRosette,
    "d3-logo-baseline-wave": renderBaselineWave,
    "d3-logo-stack-offset": renderStackOffset,
    "d3-logo-slice-shift": renderSliceShift,
    "d3-logo-multi-stroke-wordmark": renderMultiStrokeWordmark,
    "d3-logo-extruded-wordmark": renderExtrudedWordmark,
    "d3-logo-letter-weave": renderLetterWeave,
    "d3-logo-responsive-lockup": renderResponsiveLockup,
    "d3-logo-spiral-trace": renderSpiralTrace,
    "d3-logo-orbit-network": renderOrbitNetwork,
    "d3-logo-grid-activation": renderGridActivation,
    "d3-logo-contour-fingerprint": renderContourFingerprint,
    "d3-logo-voronoi-shards": renderVoronoiShards,
    "d3-logo-animal-facets": renderAnimalFacets,
    "d3-logo-animal-surface-mask": renderAnimalSurfaceMask,
    "d3-logo-negative-space-reveal": renderNegativeSpaceReveal,
    "d3-logo-folded-ribbon": renderFoldedRibbon,
    "d3-logo-boolean-lens": renderBooleanLens,
    "d3-logo-radiant-pulse": renderRadiantPulse,
    "d3-logo-parametric-wave": renderParametricWave,
    "d3-logo-kaleidoscope-wedges": renderKaleidoscopeWedges,
    "d3-logo-polar-halo": renderPolarHalo,
    "d3-logo-aperture-iris": renderApertureIris
  });

  function assertPaletteSafe(svgNode, palette) {
    const allowed = new Set(palette.allowed);
    const paintAttributes = ["fill", "stroke", "color", "stop-color", "flood-color"];
    for (const element of svgNode.querySelectorAll("*")) {
      for (const attribute of paintAttributes) {
        if (!element.hasAttribute(attribute)) continue;
        const raw = element.getAttribute(attribute).trim();
        const normalized = raw.toLowerCase();
        const isLocalPaintServer = /^url\(#[a-z0-9_.:-]+\)$/.test(normalized);
        if (normalized !== "none" && normalized !== "currentcolor" && !isLocalPaintServer && !allowed.has(normalized)) {
          throw new Error(`Palette violation in ${attribute}: ${raw}`);
        }
      }
    }
    if (svgNode.querySelector("linearGradient, radialGradient, meshgradient")) {
      throw new Error("Color-gradient elements are not permitted by the logo palette contract.");
    }
  }

  function renderLogo(target, input, options) {
    const d3 = getD3();
    const svgNode = target && typeof target.node === "function" ? target.node() : target;
    if (!svgNode || String(svgNode.localName).toLowerCase() !== "svg" || svgNode.namespaceURI !== SVG_NS) {
      throw new TypeError("renderLogo expects an SVG element or a D3 selection containing one SVG element.");
    }

    const renderOptions = options && typeof options === "object" ? options : {};
    const sourceConfig = input && typeof input === "object" ? input : {};
    const config = normalizeConfig({
      ...sourceConfig,
      smallSize: sourceConfig.smallSize === true || sourceConfig.swatch === true || renderOptions.smallSize === true || renderOptions.swatch === true,
      outputWidth: renderOptions.outputWidth == null ? sourceConfig.outputWidth : renderOptions.outputWidth
    });
    const palette = COLORSETS[config.colorset];
    const pattern = PATTERN_BY_ID.get(config.patternId);
    const texture = TEXTURE_BY_ID.get(config.textureId);
    const renderer = PATTERN_RENDERERS[config.patternId];
    if (!renderer) throw new RangeError(`No pattern renderer for ${config.patternId}.`);

    const width = effectiveWidth(svgNode, config);
    const smallSize = config.smallSize || width < 128;
    const prefix = stablePrefix(svgNode, config);
    const uid = makeIdFactory(prefix);
    const titleId = uid("title");
    const descId = uid("desc");
    const texturePatternId = uid("texture-fill");
    const svg = d3.select(svgNode);

    svg.selectAll("*").remove();
    svg
      .attr("viewBox", VIEW_BOX)
      .attr("width", 480)
      .attr("height", 320)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("role", "img")
      .attr("focusable", "false")
      .attr("aria-labelledby", `${titleId} ${descId}`)
      .attr("data-composition-id", config.compositionId)
      .attr("data-example-id", config.exampleId)
      .attr("data-pattern-id", config.patternId)
      .attr("data-texture-id", config.textureId)
      .attr("data-colorset", config.colorset)
      .attr("data-geometry-signature", pattern.geometrySignature)
      .attr("data-intentional-text-occlusions", JSON.stringify(pattern.intentionalOcclusions || []))
      .attr("data-intentional-text-omissions", JSON.stringify(pattern.intentionalOmissions || []))
      .attr("data-font", config.font)
      .attr("data-density", config.density)
      .attr("data-curvature", config.curvature)
      .attr("data-scale", config.scale)
      .attr("data-rotation", config.rotation)
      .attr("data-texture-strength", config.textureStrength)
      .attr("data-seed", config.seed)
      .attr("data-effective-width", width)
      .attr("data-small-size", smallSize ? "true" : "false")
      .attr("data-texture-flat-fallback", config.textureStrength === 0 || (smallSize && config.textureId === "d3-logo-halftone-dots") ? "true" : "false");

    svg.append("title").attr("id", titleId).text(`${config.brand} — ${pattern.label}`);
    svg.append("desc").attr("id", descId).text(
      `${config.accessibilityLabel}. ${pattern.label} using ${texture.label} in ${config.colorset}.`
    );

    const defs = svg.append("defs");
    svg.append("rect")
      .attr("class", "logo-background")
      .attr("x", 0).attr("y", 0).attr("width", 480).attr("height", 320)
      .attr("fill", palette.roles.background);

    const context = {
      d3,
      svg,
      svgNode,
      defs,
      uid,
      config,
      palette,
      pattern,
      texture,
      effectiveWidth: width,
      smallSize,
      texturePatternId,
      textureFillFallback: palette.roles.primary,
      textureFill: config.textureStrength === 0 || (smallSize && config.textureId === "d3-logo-halftone-dots")
        ? palette.roles.primary
        : fragmentUrl(texturePatternId),
      brandHandled: false,
      taglineHandled: false
    };
    createTexture(defs, context);

    const compositionGroup = svg.append("g")
      .attr("class", "logo-composition")
      .attr("data-composition-id", config.compositionId)
      .attr("data-example-id", config.exampleId)
      .attr("data-pattern-id", config.patternId)
      .attr("data-texture-id", config.textureId)
      .attr("data-colorset", config.colorset)
      .attr("data-geometry-signature", pattern.geometrySignature);
    const markGroup = compositionGroup.append("g")
      .attr("class", `logo-mark logo-mark-${sanitizeId(config.patternId.replace(/^d3-logo-/, ""))}`)
      .attr("data-mechanism", pattern.geometrySignature)
      .attr("transform", `translate(240,145) rotate(${config.rotation}) scale(${config.scale}) translate(-240,-145)`);

    renderer(markGroup, context);
    applySafeMarkTransform(markGroup, context);
    if (!context.brandHandled) addBrandLockup(compositionGroup, context, 270);
    if (!context.taglineHandled) addTagline(compositionGroup, context, 302);
    annotateTextLayers(compositionGroup, context);
    assertPaletteSafe(svgNode, palette);
    return svgNode;
  }

  const API = Object.freeze({
    version: "1.0.0",
    d3Version: "7",
    VIEW_BOX,
    PATTERNS,
    TEXTURES,
    COMPOSITIONS,
    FONT_STACKS,
    FONTS,
    COLORSETS,
    PALETTES: COLORSETS,
    normalizeConfig,
    renderLogo
  });

  root.D3LogoDesign = API;
})(typeof window !== "undefined" ? window : globalThis);
