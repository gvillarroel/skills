# Task

You are in an isolated workspace with only the `html-d3-anime-video-workflow` skill copied under `skills/html-d3-anime-video-workflow`.

Read this prompt first. Then use the skill to create a design-focused production plan for a polished Metro Minimal Tonal Motion video. This is not a video-render task.

## Required References

Before writing outputs, read these two skill references:

- `skills/html-d3-anime-video-workflow/references/metro-minimal-tonal-motion.md`
- `skills/html-d3-anime-video-workflow/references/visual-density-pattern-bank.md`

Do not inspect scripts. Do not list directories. Do not read `assets/examples`.

## Source Brief

Create a 55 second narrated concept video plan for:

**Distributed trace overload recovery**

The source facts that must be preserved:

- Requests enter an API gateway.
- A trace fans out to auth, billing, inventory, and notification services.
- The inventory service saturates first.
- Retries amplify queue pressure.
- Backpressure throttles new traffic.
- A dead-letter route isolates failed work.
- A circuit breaker stops retry storms.
- Recovery happens when queue depth falls and half-open probes pass.

## Visual Style

Use Metro Minimal Tonal Motion:

- colorset1 only
- no rounded borders
- no internal box padding
- hard 4 px grid geometry
- different grayscale levels for hierarchy
- no title, subtitle, caption, checked-date, draft, or scaffold bands
- functional text only as object labels, states, table values, axes, node names, or compact legends
- design as one megacanvas with camera exploration, not disconnected slides

## Required Output

Write:

- `projects/metro-design-redesign-plan/production-plan.md`
- `projects/metro-design-redesign-plan/design-contract.json`
- `projects/metro-design-redesign-plan/metro-design-validation.json`

The Markdown plan must include these exact section headings:

- `# Metro Design Production Plan`
- `## Source Facts`
- `## Megacanvas Composition`
- `## Pattern Selection`
- `## Beat Plan`
- `## Text Budget`
- `## Motion Systems`
- `## Camera Path`
- `## Rejection Gate`

The plan must name at least six visual pattern IDs from the visual density pattern bank, and it must use at least three of them in the beat plan.

The Markdown plan must explicitly include these literal strings in the design or composition discussion because the validator checks them:

- `colorset1`
- `no internal box padding`
- `4 px`
- `corner radius`
- `camera`
- `grayscale`
- `megacanvas`

Before running the validator, check the plan text yourself and fix it if any of those literals are missing.

The JSON contract must contain:

```json
{
  "passed": true,
  "style": "Metro Minimal Tonal Motion",
  "colorset": "colorset1",
  "roundedBorders": false,
  "internalBoxPadding": false,
  "minimumFunctionalZones": 3,
  "minimumSemanticMotionSystems": 3,
  "minimumCameraEvents": 2,
  "titleBandsAllowed": false,
  "patternIdsNamed": [],
  "patternsUsedInBeats": [],
  "muteTestExpectedInference": ""
}
```

Fill `patternIdsNamed` with at least six IDs and `patternsUsedInBeats` with at least three IDs. Keep the copied skill directory read-only; write outputs only under `projects/metro-design-redesign-plan`.

After writing the Markdown plan and JSON contract, run the bundled Metro design validator from this exact skill-relative script path: `skills/html-d3-anime-video-workflow/scripts/validate_metro_design_contract.py`. Do not run `--help`, `find`, `ls`, or any script probe. Write its report to `projects/metro-design-redesign-plan/metro-design-validation.json`. Require these source anchors in the validator: `Inventory`, `Retry`, `Backpressure`, `Dead-letter`, and `Half-Open`.
