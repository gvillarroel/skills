import {
  drawCapsuleOnPath,
  drawContextPlates,
  drawRailSwitch,
  drawText,
  drawToken,
  easeP,
  p01
} from "./evaluation-shared.js";

const baseTargets = [
  { label: "summary", color: "#007298", target: { x: 982, y: 168 } },
  { label: "rules", color: "#652f6c", target: { x: 1040, y: 274 } },
  { label: "draft", color: "#45842a", target: { x: 1032, y: 382 } },
  { label: "table", color: "#e77204", target: { x: 978, y: 492 } },
  { label: "?", color: "#9e1b32", target: { x: 902, y: 574 } }
];

const vague = [0.3, 0.24, 0.2, 0.15, 0.11];
const structured = [0.11, 0.62, 0.17, 0.07, 0.03];

function branchesFor(progress) {
  return baseTargets.map((branch, index) => ({
    ...branch,
    p: vague[index] + (structured[index] - vague[index]) * progress,
    selected: index === (progress > 0.68 ? 1 : 0)
  }));
}

function drawContextTokens(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const baseP = easeP(t, 0.4, 0.8, ctx);
  ["write", "policy"].forEach((token, index) => {
    drawToken(g, 112 + index * 92, 120, 76, 30, [palette.gray600, palette.blue][index], ctx, {
      label: token,
      labelSize: 13,
      opacity: baseP * easeOut(p01(t, 0.4 + index * 0.16, 0.6, ctx)),
      strokeWidth: 1.1
    });
  });
  const richP = easeP(t, 6.8, 1.2, ctx);
  ["format", "data", "tests", "tone"].forEach((token, index) => {
    drawToken(g, 104 + index * 86, 226, 72, 28, [palette.orange, palette.purple, palette.green, palette.red][index], ctx, {
      label: token,
      labelSize: 12,
      opacity: richP * easeOut(p01(t, 7.0 + index * 0.16, 0.58, ctx)),
      strokeWidth: 1.1,
      fillOpacity: 0.76
    });
  });
}

export function drawEvaluationDefinition(g, t, ctx) {
  const { palette, easeOut, easeInOut, clamp } = ctx;
  const group = g.append("g").attr("opacity", easeP(t, 0, 0.8, ctx));
  drawContextTokens(group, t, ctx);

  const reshapeP = easeInOut(p01(t, 7.2, 6.4, ctx));
  drawContextPlates(group, [
    { x: 308, y: 190 - 46 * reshapeP, w: 58, h: 58, color: palette.orange, fill: palette.orangeHighlight, icon: "format_shapes", drop: 110 },
    { x: 386, y: 190 - 34 * reshapeP, w: 58, h: 58, color: palette.green, fill: palette.greenHighlight, icon: "science", drop: 98 },
    { x: 464, y: 190 - 52 * reshapeP, w: 58, h: 58, color: palette.purple, fill: palette.purpleHighlight, icon: "database", drop: 118 }
  ], ctx, {
    opacity: easeP(t, 7.3, 1.1, ctx),
    reveal: reshapeP
  });

  const origin = { x: 258, y: 430 };
  const switchGroup = group.append("g");
  const branches = branchesFor(reshapeP);
  const paths = drawRailSwitch(switchGroup, origin, branches, ctx, {
    reveal: p01(t, 1.4, 2.0, ctx),
    minWidth: 3.5,
    maxWidth: 28
  });

  const firstSample = p01(t, 3.4, 3.5, ctx);
  if (firstSample > 0.01 && reshapeP < 0.35) {
    drawCapsuleOnPath(group, paths[0].path, easeInOut(firstSample), palette.blue, ctx, {
      opacity: easeP(t, 3.3, 0.6, ctx) * (1 - clamp((reshapeP - 0.1) / 0.25, 0, 1)),
      w: 62,
      h: 26,
      strokeWidth: 3
    });
  }

  const secondSample = p01(t, 14.4, 5.1, ctx);
  if (secondSample > 0.01) {
    drawCapsuleOnPath(group, paths[1].path, easeInOut(secondSample), palette.brandPrimary, ctx, {
      opacity: easeP(t, 14.2, 0.7, ctx),
      w: 66,
      h: 28,
      strokeWidth: 3.4
    });
  }

  const uncertainty = easeP(t, 18.8, 1.3, ctx);
  if (uncertainty > 0.01) {
    const sidePath = paths[3].path;
    drawCapsuleOnPath(group, sidePath, 0.62 + Math.sin(t * 1.8) * 0.04, palette.orange, ctx, {
      opacity: uncertainty * 0.46,
      w: 38,
      h: 17,
      strokeWidth: 2,
      fill: palette.orangeHighlight
    });
    drawText(group, "still possible", 792, 604, ctx, {
      size: 17,
      weight: 850,
      fill: palette.orangeHover,
      opacity: uncertainty
    });
  }
}
