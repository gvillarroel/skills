(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.SurfaceStableFractalDither = api;
})(typeof globalThis === "object" ? globalThis : this, function () {
  "use strict";

  // Recursive Bayer order: the first point survives a level boundary and the
  // other three appear in the X-shaped order used to expand a 2x2 level.
  const BAYER_POINT_SEQUENCE = Object.freeze([
    Object.freeze([0, 0]),
    Object.freeze([0.5, 0.5]),
    Object.freeze([0.5, 0]),
    Object.freeze([0, 0.5])
  ]);

  function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
  }

  function stateForScale(scale, baseSpacing = 16) {
    const safeScale = Math.max(Number(scale) || 1, 1e-6);
    const spacingLog = Math.log2(safeScale);
    const fractalLevel = Math.floor(spacingLog);
    const phase = spacingLog - fractalLevel;
    const subLayerCount = clamp(1 + Math.floor(phase * 4), 1, 4);
    return {
      scale: safeScale,
      fractalLevel,
      phase,
      subLayerCount,
      surfaceCellSize: baseSpacing / (2 ** fractalLevel),
      screenCellSize: (baseSpacing / (2 ** fractalLevel)) * safeScale
    };
  }

  function luminance(red, green, blue) {
    return clamp((0.299 * red + 0.587 * green + 0.114 * blue) / 255, 0, 1);
  }

  function brightnessSampler(imageData, surfaceWidth = imageData.width, surfaceHeight = imageData.height) {
    if (!imageData || !imageData.data || !imageData.width || !imageData.height) {
      throw new Error("brightnessSampler requires browser ImageData-like width, height, and data values.");
    }
    return function sampleBrightness(surfaceX, surfaceY) {
      const x = clamp(Math.floor((surfaceX / surfaceWidth) * imageData.width), 0, imageData.width - 1);
      const y = clamp(Math.floor((surfaceY / surfaceHeight) * imageData.height), 0, imageData.height - 1);
      const offset = (y * imageData.width + x) * 4;
      const alpha = imageData.data[offset + 3] / 255;
      return luminance(imageData.data[offset], imageData.data[offset + 1], imageData.data[offset + 2]) * alpha;
    };
  }

  function dotId(x, y) {
    return `${x.toFixed(6)}:${y.toFixed(6)}`;
  }

  function buildDots(options) {
    const {
      width,
      height,
      scale = 1,
      baseSpacing = 16,
      screenRadius = 2.25,
      brightnessAt = () => 1,
      shading = "halftone",
      originX = 0,
      originY = 0,
      padding = baseSpacing
    } = options || {};
    if (!(width > 0 && height > 0)) throw new Error("buildDots requires positive width and height.");
    if (!['halftone', 'bayer-count'].includes(shading)) throw new Error("shading must be halftone or bayer-count.");

    const state = stateForScale(scale, baseSpacing);
    const cell = state.surfaceCellSize;
    const startColumn = Math.floor((-padding - originX) / cell);
    const endColumn = Math.ceil((width + padding - originX) / cell);
    const startRow = Math.floor((-padding - originY) / cell);
    const endRow = Math.ceil((height + padding - originY) / cell);
    const dots = [];

    for (let row = startRow; row <= endRow; row += 1) {
      for (let column = startColumn; column <= endColumn; column += 1) {
        for (let order = 0; order < state.subLayerCount; order += 1) {
          const offset = BAYER_POINT_SEQUENCE[order];
          const x = originX + (column + offset[0]) * cell;
          const y = originY + (row + offset[1]) * cell;
          if (x < -padding || x > width + padding || y < -padding || y > height + padding) continue;
          const brightness = clamp(Number(brightnessAt(x, y)) || 0, 0, 1);
          const threshold = (order + 0.5) / 4;
          if (shading === "bayer-count" && brightness < threshold) continue;
          const radiusMultiplier = shading === "halftone" ? Math.sqrt(brightness) : 1;
          if (radiusMultiplier <= 0) continue;
          dots.push({
            id: dotId(x, y),
            x,
            y,
            radius: (screenRadius / state.scale) * radiusMultiplier,
            screenRadius: screenRadius * radiusMultiplier,
            brightness,
            order,
            layer: order + 1,
            fractalLevel: state.fractalLevel,
            parentCell: `${column}:${row}`
          });
        }
      }
    }
    return { ...state, dots };
  }

  function validateNestedBoundary(options = {}) {
    const baseSpacing = options.baseSpacing || 16;
    const width = options.width || baseSpacing * 4;
    const height = options.height || baseSpacing * 4;
    const before = buildDots({ width, height, baseSpacing, scale: 1.999999, brightnessAt: () => 1, shading: "bayer-count", padding: 0 });
    const after = buildDots({ width, height, baseSpacing, scale: 2, brightnessAt: () => 1, shading: "bayer-count", padding: 0 });
    const beforeIds = new Set(before.dots.map(dot => dot.id));
    const afterIds = new Set(after.dots.map(dot => dot.id));
    return {
      ok: beforeIds.size === afterIds.size && [...beforeIds].every(id => afterIds.has(id)),
      beforeCount: beforeIds.size,
      afterCount: afterIds.size,
      beforeLevel: before.fractalLevel,
      afterLevel: after.fractalLevel
    };
  }

  function validateZoomSequence(options = {}) {
    const baseSpacing = options.baseSpacing || 16;
    const width = options.width || baseSpacing * 4;
    const height = options.height || baseSpacing * 4;
    const scales = options.scales || [1, 1.25, 1.5, 1.75, 1.999999, 2];
    let previous = null;
    const steps = scales.map(scale => {
      const state = buildDots({ width, height, baseSpacing, scale, brightnessAt: () => 1, shading: "bayer-count", padding: 0 });
      const ids = new Set(state.dots.map(dot => dot.id));
      const retained = previous === null || [...previous].every(id => ids.has(id));
      previous = ids;
      return { scale, fractalLevel: state.fractalLevel, subLayerCount: state.subLayerCount, dotCount: ids.size, retained };
    });
    const boundary = validateNestedBoundary({ width, height, baseSpacing });
    return { ok: steps.every(step => step.retained) && boundary.ok, steps, boundary };
  }

  return Object.freeze({
    BAYER_POINT_SEQUENCE,
    brightnessSampler,
    buildDots,
    luminance,
    stateForScale,
    validateNestedBoundary,
    validateZoomSequence
  });
});
