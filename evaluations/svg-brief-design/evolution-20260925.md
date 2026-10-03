# SVG Brief Design: evolution result

The requested Harbor/GEPA evolution is complete. The tested mutations did not
demonstrate an improvement over the existing guide, so that guide remains
installed and experimental. No new candidate was promoted.

Both campaigns used exact `openai-codex/gpt-6-luna` through Pi 0.84.2 with
medium reasoning and SSE, Harbor 0.18.0, and GEPA 0.1.2. They produced **84
native development trials across 12 tasks and nine reflection proposals**.
All 84 generated SVGs passed technical validity; all execution, model, input,
provenance, and bundle-integrity audits passed. There were no provider failures
or semantic retries in these campaigns.

| Campaign | Tasks | Native trials | Proposals | Original guide mean | Best new complete-set mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| General design guidance | 6 | 54 | 6 | 0.520698 | 0.513628 | Keep original |
| Constructive geometry rules | 6 additional | 30 | 3 | 0.634608 | 0.595336 | Keep original |

Compare versions within each row only. The rows contain different tasks.
Six proposals failed their matched minibatch filters; only three new proposals
received complete-set measurements. No metric was changed after seeing results.
The reward remains verifier 1.1.0: 60% shape and 40% style similarity, not
semantic accuracy or the probability that a human would approve the drawing.

The additional campaign tested a concrete construction procedure rather than
another wording-only change: shared geometric anchors, coherent coordinate
frames, shape relationships, and checks of connections and openings. Its
complete-set candidate regressed on five of six cases. Manual comparison also
showed that improved label legibility can coincide with lower similarity;
the visual proxy is not a substitute for a semantic or visual quality review.

The short natural-language briefs were not expanded to reveal reference
geometry. The additional six briefs contain 25–30 words before their common
SVG delivery contract. Reference artwork remained outside the agent's skill
payload, and reflection received no reference images, path coordinates, or
generated SVG source.

The canonical bundle is still exactly `SKILL.md`, `references/svg-mechanics.md`,
and `agents/openai.yaml`. It contains no purchased assets, encoded artwork,
stored geometry, asset download links, or specimen reconstruction recipes.
The canonical SKILL.md SHA-256 remains
`740953f66380e648093af346231429ddf755d0fd564f910241157ea3beb57d04`.
The repository-local installation matches the source byte for byte.

The private validation and holdout gates remain unopened because the selected
bundle was unchanged in both campaigns. No independent generalization or
unforced routing pass is claimed. The earlier prototype's results and provider
failures remain preserved separately; they were not replaced by these runs.

Recorded usage totals 341,917 native-trial tokens and 32,690 reflection tokens.
The task-free transport probe is separate. USD cost is unavailable.

Detailed methodology and exact local evidence paths:

- [General-guidance campaign](gepa-20260925.md) and [machine-readable summary](gepa-20260925.json).
- [Construction-mechanism follow-up](mechanics-20260925.md) and [machine-readable summary](mechanics-20260925.json).
- [Original skill study](study-20260925.md).
- [Final repository, payload, and installation checks](validation-20260925.json):
  pattern IDs, skill validation, independence, payload, all 14 harness tests,
  Python compilation, quick skill validation, targeted local-install check,
  guidance-only audit, and scoped diff check all passed.

All native artifacts, rejected proposals, model events, rendered comparison
sheets, configuration seals, and audits remain under the ignored local
`evaluations/runs/` roots named in those reports. They are not shipped in the
skill or published.
