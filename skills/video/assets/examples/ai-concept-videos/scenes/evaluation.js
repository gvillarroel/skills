import { drawEvaluationDefinition } from "./evaluation-definition.js";
import { drawEvaluationHandoff } from "./evaluation-handoff.js";
import { drawEvaluationHook } from "./evaluation-hook.js";
import { drawEvaluationImplication } from "./evaluation-implication.js";
import { drawEvaluationMechanism } from "./evaluation-mechanism.js";

const beatOrder = ["hook", "definition", "mechanism", "implication", "handoff"];
const renderers = {
  hook: drawEvaluationHook,
  definition: drawEvaluationDefinition,
  mechanism: drawEvaluationMechanism,
  implication: drawEvaluationImplication,
  handoff: drawEvaluationHandoff
};

const durations = {
  hook: 12,
  definition: 24,
  mechanism: 30,
  implication: 34,
  handoff: 20
};

function renderBeat(g, beatId, t, ctx) {
  const renderer = renderers[beatId] ?? renderers.hook;
  renderer(g, t, ctx);
}

export function drawEvaluationVisualOnly(g, ctx) {
  const { beat, sceneProgress, easeOut, clamp } = ctx;
  const current = beat.id;
  const duration = durations[current] ?? (beat.end - beat.start);
  const t = clamp(sceneProgress * duration, 0, duration);
  const index = beatOrder.indexOf(current);
  const transition = 0.7;

  if (index > 0 && t < transition) {
    const previous = beatOrder[index - 1];
    const out = 1 - easeOut(t / transition);
    const previousGroup = g.append("g").attr("opacity", out);
    renderBeat(previousGroup, previous, durations[previous] - 1 / 30, {
      ...ctx,
      sceneProgress: 1
    });
  }

  const inOpacity = index > 0 ? easeOut(t / transition) : 1;
  const currentGroup = g.append("g").attr("opacity", inOpacity);
  renderBeat(currentGroup, current, t, ctx);
}
