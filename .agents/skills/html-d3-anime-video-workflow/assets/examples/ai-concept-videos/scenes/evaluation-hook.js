import {
  drawCapsule,
  drawCapsuleOnPath,
  drawRailSwitch,
  drawText,
  drawToken,
  easeP,
  p01
} from "./evaluation-shared.js";

const branches = [
  { label: "return", p: 0.42, color: "#007298", target: { x: 958, y: 170 }, selected: true },
  { label: "fix", p: 0.24, color: "#652f6c", target: { x: 1010, y: 276 } },
  { label: "test", p: 0.18, color: "#45842a", target: { x: 1026, y: 382 } },
  { label: "try", p: 0.1, color: "#e77204", target: { x: 984, y: 486 } },
  { label: ".", p: 0.06, color: "#9e1b32", target: { x: 910, y: 572 } }
];

function drawOriginPrompt(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const reveal = easeP(t, 0.2, 0.9, ctx);
  const tokens = ["bug", "in", "patch"];
  tokens.forEach((token, index) => {
    drawToken(g, 116 + index * 88, 348, 72, 30, [palette.blue, palette.gray600, palette.orange][index], ctx, {
      label: token,
      opacity: reveal * easeOut(p01(t, 0.4 + index * 0.18, 0.6, ctx)),
      labelSize: 13,
      strokeWidth: 1.1
    });
  });
  drawCapsule(g, 116, 430, 0, palette.brandPrimary, ctx, {
    opacity: easeP(t, 1.2, 0.8, ctx),
    w: 64,
    h: 28
  });
}

export function drawEvaluationHook(g, t, ctx) {
  const { palette, easeOut, clamp } = ctx;
  const group = g.append("g").attr("opacity", easeOut(p01(t, 0, 0.8, ctx)));
  const origin = { x: 270, y: 430 };
  drawOriginPrompt(group, t, ctx);

  const switchReveal = p01(t, 1.4, 2.0, ctx);
  const paths = drawRailSwitch(group, origin, branches, ctx, {
    reveal: switchReveal,
    opacity: 1,
    minWidth: 3.5,
    maxWidth: 25
  });

  const pulseP = easeP(t, 3.2, 1.0, ctx);
  paths.forEach((branch, index) => {
    const dotCount = Math.max(1, Math.round(branch.p * 12));
    for (let dot = 0; dot < dotCount; dot += 1) {
      const p = ((t * (0.08 + branch.p * 0.08) + dot / dotCount + index * 0.11) % 1);
      const opacity = pulseP * (branch.selected ? 0.38 : 0.16) * clamp(1 - Math.abs(p - 0.5) * 1.4, 0, 1);
      drawCapsuleOnPath(group, branch.path, p, branch.color, ctx, {
        opacity,
        w: 22,
        h: 10,
        strokeWidth: 1.2,
        fill: branch.color
      });
    }
  });

  const sampleP = p01(t, 4.6, 4.4, ctx);
  if (sampleP > 0.01) {
    const selectedPath = paths[0].path;
    drawCapsuleOnPath(group, selectedPath, ctx.easeInOut(sampleP), palette.brandPrimary, ctx, {
      opacity: easeP(t, 4.4, 0.7, ctx),
      w: 66,
      h: 28,
      strokeWidth: 3.4
    });
  }

  const settledP = easeP(t, 9.0, 1.2, ctx);
  if (settledP > 0.01) {
    drawText(group, "likely", 828, 92, ctx, {
      size: 20,
      weight: 890,
      fill: palette.gray700,
      opacity: settledP
    });
    drawText(group, "not guaranteed", 956, 92, ctx, {
      size: 20,
      weight: 890,
      fill: palette.brandPrimary,
      opacity: settledP
    });
    group.append("line")
      .attr("x1", 900)
      .attr("y1", 104)
      .attr("x2", 900)
      .attr("y2", 150)
      .attr("stroke", palette.gray300)
      .attr("stroke-width", 2)
      .attr("opacity", settledP * 0.5);
  }
}
