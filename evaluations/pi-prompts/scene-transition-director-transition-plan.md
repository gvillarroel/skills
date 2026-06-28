Use $scene-transition-director to create a machine-readable transition plan for a 24-second silent technical explainer.

Write exactly one file at `transition-plan.json`.

Source scenes:

1. `s01-intake`, 0-8 seconds. A user request enters a coding assistant as a yellow task card.
2. `s02-tool-use`, 8-16 seconds. The task becomes a blue tool packet that moves through repo, editor, terminal, and tests.
3. `s03-proof`, 16-24 seconds. The tested result becomes a green proof card next to a final definition.

Requirements:

- Use one persistent element named `work packet`.
- Create exactly two transitions.
- Transition 1 must preserve `yellow task card` and explain how it becomes a `blue tool packet`.
- Transition 2 must preserve `blue tool packet` and explain how it becomes a `green proof card`.
- Include compositionShift, colorShift, cameraShift, spaceShift, surprise, outgoingState, bridgeAction, incomingState, and validationChecks for every transition.
- Do not mention GSAP.
- Your JSON must pass this validator command from the isolated workspace:

```powershell
uv run --script skills/scene-transition-director/scripts/validate_transition_plan.py --plan transition-plan.json --expect-transitions 2 --expect-persistent-name "work packet" --expect-chain "s01-intake,s02-tool-use,s03-proof" --require-anchor "yellow task card" --require-anchor "blue tool packet" --require-anchor "green proof card" --forbid gsap
```
