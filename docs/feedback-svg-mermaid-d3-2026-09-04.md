# Feedback from the Harness / Tools / Context presentation

Date: 2026-09-04. Requested output: a retrospective and actionable feedback for the skills responsible for SVG, Mermaid, and D3.

## Main finding and scope

The dominant avoidable problem was losing an already established contract during a later revision. Meaning, notation, palette, geometry, animation, and delivery were maintained in several places. A small requested change could therefore repair one output while silently invalidating another.

The user repeatedly had to specify both the instructional idea and production details: complete blocks appearing in order, a transparent diagram, an independently movable text card, a final-state review image, and consistent colors after a structural edit. Those decisions needed to become persistent inputs to the build and review process.

This report distinguishes three sources of evidence:

- **Conversation:** explicit requests and corrections in the provided task history. These establish intent and dissatisfaction, but do not independently prove every implementation failure.
- **Saved artifacts:** source, generators, versioned output directories, and prior QA notes in the sibling `blog` repository.
- **Fresh checks:** decoded APNG frames, image pixels, SVG structure, selectors, source/package hashes, and route geometry inspected on 2026-09-04.

The review does not claim a fresh inspection of the live Google Slides deck, remote ZIPs, or current product capabilities. Existing news and paper claims were reviewed for presentation clarity, not independently fact-checked again. Historical QA notes are evidence of what was checked at that time, not a current release certificate.

No presentation assets or skill behavior were changed in this pass. The requested feedback lives in this repository; temporary inspection code, contact sheets, and measurements remain in the blog's [review evidence folder](../../blog/output/skill-feedback-20260904/). Source hashes are recorded in [artifact-audit.json](../../blog/output/skill-feedback-20260904/artifact-audit.json).

## 1. Distinguish avoidable repairs from useful exploration

Several iterations were legitimate design development. The user changed the delivery preference between APNG and MP4, expanded the metaphor, introduced a fourth ecosystem layer, and asked for additional evidence and topics. An earlier artifact should not be graded against a requirement introduced later.

Avoidable rework begins when an explicit choice is ignored, a correction changes unrelated approved properties, or an export no longer represents its source. The following ledger makes that distinction.

| Area | What needed clarification or repair | What worked after the repair | Transferable lesson |
| --- | --- | --- | --- |
| Scope of iteration | The user asked to remove premature material and define slides together. The suggestions deck also needed an explicit boundary from the canonical deck. Actual unauthorized mutation is not established by the reminder alone. | Stable canonical and exploratory destinations, with one reviewed component at a time. | Record the authorized target and the maturity of each proposal. Preserve an approved item while exploring alternatives. |
| Diagram family | Generic Mermaid/flowchart choices did not satisfy the explicit railroad request. The skill-package tree also needed correction from a flowchart to `treeView-beta`. | `railroad-ebnf-beta` for the compositional explanation; Mermaid TreeView for files. | Treat an explicit family as an acceptance condition. Check the installed renderer before inferring that a family is unsupported. |
| Slide versus components | A complete slide/video was insufficient for moving and reusing individual parts. Standalone top titles and separate text fragments also needed revision. | A compact white text card, yellow left rail, separate visual, editable sources, and final review images. | Distinguish the composition from its editable components and exports. One does not substitute for the other. |
| Reveal behavior | The user wanted coherent blocks, ordered left to right, with the return loop revealed last. Visual appearance alone did not communicate this ordering requirement. | `data-stage` / `data-stage-label`, explicit schedules, a single play, and a held final state. | Animate semantic units: a node, its label, and relevant connector. Do not infer the teaching order from arbitrary SVG primitive order. |
| Background and layering | Diagram backgrounds had to be removed; the text card had to remain white. The frozen brain had to remain in front of the hamster at its head. | Separate surfaces and explicit foreground ordering. | Transparency and z-order are component properties. A single global background or flatten operation is insufficient. |
| Review images | Initial thumbnails sometimes omitted the main diagram or data. | Final-state PNGs were generated from completed animations and used for annotation. | Validate and export the semantic end state deliberately. A presentation thumbnail is not automatically a final-state render. |
| Copy and evidence | Merely naming the concept, long text, and absent source boxes needed improvement. | Short contrastive definitions and short, linked source names separated by commas. | Give the speaker a useful distinction, and give the audience evidence in readable native links. Keep the full bibliography in Markdown/notes. |
| Ecosystem | Three layers became four; labels became equal-sized circular icons; services and sources were expanded; layer counts were removed. Some of this was new scope. | Models, harnesses, meta-harnesses, and tools; a later scene reused the positions and illuminated connections. | Separate a taxonomy from connectivity. Keep coordinates stable when the next slide adds relationships. Equal containers still need optical logo sizing. |
| Skills and hooks | The skill scene needed two role-specific paths. The blocking-hook scene initially read as several attempts and had to become one continuous execution. | Hat changes communicate a different instruction context; one agent blocks, backtracks twice, and then crosses an allowed point. | Specify the state machine, actor identity, attempt counter, and stopping condition before animation. |
| Risks and examples | Dense combined scenarios, decorative threat symbols, generic icons, and an abstract replacement did not fit the desired explanation. | Separate processes, familiar service logos, a smaller hamster, a sober external server, and evidence from recognizable incidents. | Choose the medium from the reader's question. A credible image or source figure can be more useful than a new custom diagram. |
| Harness correction | Moving System Prompt to the beginning was followed by an unwanted color change and misaligned hook points. | The palette was restored; hook anchors were derived from current railroad geometry. | Structural edits need dependent-asset invalidation and independent style checks. Preserve the approved visual roles while recomputing layout. |
| Delivery | Animation-only archives omitted static visuals; later requests distinguished diagram text, text cards, sources, and transparent assets. | Per-slide folders, APNG for motion, PNG for static compositions, and a separate text-card image. | Build from an explicit inventory, not an extension filter alone. Record what each file contains and what the destination can edit. |

Historical evidence includes the [block-animation review](../../blog/presentations/harnesses-skills-context/validation/block-animation-review.md), [single-card review](../../blog/presentations/harnesses-skills-context/validation/single-card-layout-review.md), and [copy/source audit](../../blog/presentations/harnesses-skills-context/qa/copy-and-source-boxes-audit.md). The block-animation review describes the earlier order with System Prompt after extensions; the [current Harness source](../../blog/presentations/harnesses-skills-context/slides/01-harness/diagram.mmd) puts it first. That difference itself demonstrates why historical reports need source/version identity.

## 2. Freshly verified defects and remaining fragility

Priorities: **P1** affects meaning, fidelity, editability, or repeatability; **P2** affects polish or audit confidence. These are review priorities, not claims about production security severity.

### P1 — The Skills highlight no longer finds its target

[build-skill-composition-slide-v3-gates.mjs](../../blog/presentations/harnesses-skills-context/scripts/build-skill-composition-slide-v3-gates.mjs), function `highlightedHarnessSvg`, selects a group by the literal transform `translate(40.07421875, 47)`. That transform is absent from the current Harness SVG. The exported `harness-skill-highlight.svg` contains **zero** groups with `class="railroad-terminal skill-focus"`.

The result can render successfully while silently losing the intended focus. The current rendered Skills block uses `translate(44.20703125, 47)` within its parent, illustrating why coordinates cannot serve as identity.

**Suggested repair:** identify the block from its semantic role and label within the Harness rule, assign a stable ID, and require exactly one match. A missing or ambiguous target should fail the build with the target name. Broader selectors should not silently highlight another block.

**Acceptance:** change the length/order of a neighboring label; the same Skills block is highlighted exactly once without editing selector coordinates.

### P1 — Contain-resize introduces opaque black letterboxing

The same generator resizes the harness inset to `800 × 238` with `fit: "contain"` and no explicit padding background. The resulting [harness-skill-highlight-slide.png](../../blog/presentations/harnesses-skills-context/artifacts/slide-03i-skill-composition-v3-gates/harness-skill-highlight-slide.png) has `(0, 0, 0, 255)` at all four corners. Black vertical strips are visible in the [saved slide composition](../../blog/presentations/harnesses-skills-context/artifacts/slide-03i-skill-composition-v3-gates/slide-final.png).

**Suggested repair:** preserve alpha through resize and intermediate composites, and apply an opaque surface only to the component that owns it. For this inset, explicitly transparent padding is appropriate.

**Acceptance:** inspect the padded margins and composite the result over the intended slide background and a contrasting review background. Check opacity, not just whether the file reports an alpha channel. Do not remove all near-white pixels: they can be legitimate node fills or text-card content.

### P1 — Car motion and path construction use different progress definitions

In [build-search-attempts-slide.mjs](../../blog/presentations/harnesses-skills-context/scripts/build-search-attempts-slide.mjs), `pointOnRoute` interpolates by segment index. `meshSvg` reveals the stroke using a fraction of total arc length. Equal progress therefore places the car and the visible trace tip at different locations when segments have unequal lengths.

Sampling 999 progress values on each of the four saved route geometries produced maximum separations of **80.420, 78.609, 71.222, and 73.783 SVG pixels**. These are source-geometry measurements, not measurements of live Google Slides playback. The APNG frame renderer also uses easing while the separately authored SMIL path uses its own timing; final-frame agreement alone cannot establish intermediate equivalence.

**Suggested repair:** use one route parameterization for the follower, stroke tip, current node, and phase transition. Either use cumulative arc length throughout or use a common segment schedule with explicit node dwell times. Derive SVG and raster playback from the same event/timing data.

**Acceptance:** test an uneven polyline containing a backward segment. At sampled timestamps, the actor is on the visible route tip within a declared pixel tolerance, including segment transitions. Record purposeful offsets as offsets, not silent disagreement.

The [D3 review](../../blog/output/skill-feedback-20260904/d3-search-review.md) records the qualitative assessment separately from the measured implementation finding.

### P1 — Slide 31 fixed the dots, but other relationships remain coordinate-bound

The corrected [hook geometry](../../blog/presentations/harnesses-skills-context/artifacts/slide-03j-hooks-anatomy-v1/hook-anchor-geometry.json) has a Harness gate y-coordinate spread of **0.0** and an Agent gate spread of **0.0**. The corrected source APNG and the local public-package APNG have matching SHA-256 hashes. The alignment repair is real and should be retained.

[build-hooks-anatomy-slide.mjs](../../blog/presentations/harnesses-skills-context/scripts/build-hooks-anatomy-slide.mjs) still contains a fixed expansion arrow starting `M 645 405`, fixed label boxes, and a fixed Agent crop `viewBox="0 208 325.890625 120"`. Its geometry walker accumulates `translate` operations; it does not resolve general nested scale/rotate/skew transforms. Those limitations are not evidence that the current dots are wrong, but they can cause the next layout change to break the relationship again.

**Suggested repair:** derive the expansion arrow from the actual Agent block and the lower Agent diagram. Resolve complete coordinate transforms into one scene space, or explicitly reject transform types outside the supported contract. Derive crop bounds from the selected rule and include stroke/marker padding. Fit callouts with clear leaders and collision checks.

**Acceptance:** move System Prompt, lengthen an extension label, add a tool, and change the inset size. Every gate remains on its declared rail segment and the expansion arrow still connects the intended concepts.

### P1 — The combined APNG is a playback composite, not an editable combined animation source

The delivered combined APNG correctly packages the harness, agent, and gates together. However, `hooks-harness-agent-combined.svg` is created by calling the scene at its final time. It has **zero SVG animation elements and zero semantic stage groups**. Its two railroads are SVG documents embedded as base64 `<image>` references. They remain vector content, but are not directly exposed as editable node groups in the parent SVG.

The combined renderer fades in the Harness and Agent as whole images. At time zero, `gateOpacity` already returns `.15`, so ghosted gates appear before their base diagram. This does not reproduce the earlier complete-block railroad construction contract. See the [fresh temporal contact sheet](../../blog/output/skill-feedback-20260904/hooks-combined-frames.jpg).

**Suggested repair:** retain an editable, ID-safe scene graph or an explicit source composition with references; use one clock and named semantic phases. Keep independent components and also offer the synchronized visual that the user can paste as one object. Label a final-only SVG as static. If a combined animated SVG is promised, ship the animation source that actually reproduces the composite.

**Acceptance:** compare standalone scene playback and decoded APNG at the same named phase boundaries. With motion disabled, the result is fully readable. With motion enabled, construction follows the selected block sequence and hooks attach only after their supporting geometry is visible, unless a deliberate overview is requested.

### P2 — Final-frame consistency needs a precise definition

The slide 31 APNG holds its last **21 frames / 1.75 seconds** and is mostly transparent. Its final decoded frame is not exactly identical to the separate final PNG: the difference is localized to a **15 × 13 pixel region**, bounding box `(35, 322, 50, 335)`, in the Harness label area. The difference survives compositing over both light and dark backgrounds. This is a small export consistency issue, not a large visual failure; its exact cause was not established.

**Suggested repair:** when the contract asks for the animation's last frame, export that decoded/composited frame directly. If a separate renderer produces the reference PNG, compare with a documented tolerance and inspect differences rather than claim byte/pixel identity without checking.

**Acceptance:** fully reconstruct APNG frames with their blend/disposal behavior, select the final presentation state, and compare against the supplied final review image at equal dimensions. A complete-slide PNG is a different artifact and must use the correct placement/scale of that frame.

### P2 — Reproducible editing is incomplete in the local public package

The current slide 31 package includes images and SVGs, but neither `build-hooks-anatomy-slide.mjs` nor the editable `copilot-pretool-hook.mjs` example. [sync-corrected-harness-assets.mjs](../../blog/scripts/sync-corrected-harness-assets.mjs) excludes `.js` and `.mjs` along with media formats. That can fit a restricted email package, but the package alone is insufficient to regenerate the combined animation.

**Suggested repair:** distinguish a presentation/import package from a source/rebuild package. Keep code as readable Markdown in the restricted package when requested, and preserve the executable source in the authorized source repository. Include role, revision, renderer version, source hash, palette identity, timing, and output hash in the manifest. Explain constraints honestly; do not disguise files to evade corporate controls.

**Acceptance:** a recipient can identify the current visual, the matching final PNG, the separate text card, and the source required for editing. A rebuild claim requires the actual source/dependencies, not merely an `.svg` extension.

## 3. What the current artifacts do well

The minimal left card and right visual form a useful recurring composition. The short definitions distinguish neighboring concepts: tokens versus context, prediction versus execution, and agent loop versus tool authority. The [copy/source audit](../../blog/presentations/harnesses-skills-context/qa/copy-and-source-boxes-audit.md) records these editorial improvements explicitly.

The hamster, frozen brain, equipment, hats, route, and gates create continuity across otherwise abstract concepts. The stronger scenes change one aspect of an existing visual language instead of requiring the audience to learn a new diagram on each slide. The connection scene's reuse of the ecosystem layout is especially effective.

Semantic railroad stages are a good reusable mechanism. The original five-slide pipeline retains the static SVG, stage annotations, animation, APNG, contact sheet, and metadata. Its single-play/end-hold behavior is demonstrable. The later hook anchor repair also demonstrates the right direction: derive overlays from actual source geometry.

The blocking-hook sequence now communicates **one run**, **two blocked encounters**, and **one allowed crossing**. The sampled frames show continuity and a visible boundary. The supporting notes appropriately state that this depicts a blocking hook and that not all hooks block.

Sources, notes, per-slide manifests, archived versions, and editable Markdown made this retrospective possible. The weakness is the manual relationship between them, rather than the absence of evidence altogether.

## 4. Further criticism of the visual and conceptual results

| Artifact | What works | Further improvement worth testing |
| --- | --- | --- |
| Four-layer ecosystem | Equal circular carriers, meaningful concentric roles, recognizable products, and a later connection-focused scene. | The [full ecosystem slide](../../blog/presentations/harnesses-skills-context/artifacts/slide-03e-harness-layers-ecosystem-v6-antigravity-rovo/slide-final.png) is a useful reference sheet but difficult to narrate from a projector. Short badges do not reliably disambiguate repeated vendor logos across models and harnesses. Retain the requested complete inventory, then emphasize a few labeled examples during playback. Use optical logo bounds, not only equal container diameter. Keep all source links, with readable grouped source lines and an accompanying detailed source sheet. |
| Dense possibility mesh | It conveys a large search space, failure, overshoot, and cumulative cost. The `$3.67 per run` amount is explicitly marked illustrative and satisfies the requested non-round range. | Preserve the requested density and reversals, but make only the active decision and path dominant. The very faint background can disappear under projection. Completed paths compete with the active path in the final scene. Make the acceptance test visible enough that passing near the goal is distinguishable from accepting an output. |
| Skills change salience | Firefighter and police variants preserve the same space while highlighting different corridors. | The final frame retains only the police result, so a final-state still cannot explain the comparison by itself. Consider a final recap retaining a subdued first route and clear role labels, or provide two explicitly named review stills alongside the animation. Do not imply that a skill changes weights or guarantees a route. |
| Hook boundary | The repaired one-run sequence is clearer than resetting the entire attempt. | A gate can block an attempted action; rerouting is a subsequent agent response. The graphic should preserve that distinction. Add a small `blocked` / `allowed` cue so color is not the sole evidence. Some blocked points sit behind the car, so the stop indicator must remain visible. |
| Hook anatomy | Harness above Agent, with pre/post tool locations, links code to lifecycle. | Six callouts and a long code panel create two reading tasks. Show the selected event and relevant code together, then reveal other locations. A short API example should be labeled illustrative; the broad allow fallback and two-pattern command check do not justify a claim of complete policy enforcement. The current selected-event arrow is meaningful only when its code destination is present. |
| Skill package | TreeView plus highlighted Markdown is easy to relate to a real folder. | Repair the missing highlight and black inset padding first. Then clarify that a script inside a skill is a **check that can be run**; compulsory enforcement requires a workflow/harness that invokes it and respects its result. The presentation currently risks collapsing those two claims into “Gates verify.” |
| Frozen model and roulette | The current copy correctly says weights/code are fixed **at inference**, and new information enters as context. It says the next token **can** be sampled. | Preserve these qualifications. Avoid “learns nothing” as a standalone claim. Do not make equal wheel sectors look like measured equal probabilities unless the example is explicitly uniform. If the wheel is token sampling, label tokens; if it selects actions, label it as a higher-level teaching metaphor. |
| Harness railroad | Consistent, concise, and memorable. | Treat it explicitly as a compositional teaching model. The current `[("AGENTS.md" \| "Skills" \| "MCP")]` is an optional choice, visually allowing one alternative, although the intended system can use them together. The model source uses `"parameters" \| "code"`, which reads as alternatives. These are inherited/user-supplied abstractions, not proven renderer faults. Flag the semantic limitation and propose an optional repeated group or a sequence when that matches the speaker's intended meaning; do not silently rewrite the approved source. |
| Evidence wall | Original figures, screenshots, and named incidents support credibility more directly than the rejected abstract D3 replacement. | The [saved evidence wall](../../blog/presentations/harnesses-skills-context/artifacts/slide-15-evidence-wall-v3/slide-15-evidence-wall-preview.png) still has too many competing claims and tiny screenshot text. “Emergent coordination” and the line below it are crowded. One statistic plus one tightly cropped evidence image per reveal would read better. Preserve the distinction between a controlled simulation, a real incident, and an enterprise analogy. “At least one trial” must remain attached to the relevant count. |
| Internal-data exfiltration | Familiar service logos and the sober external server make source, compromised actor, data, and destination recognizable. | In the [aligned four-column version](../../blog/presentations/harnesses-skills-context/artifacts/slide-03k-internal-exfiltration-scenario-v6-aligned-columns/slide-final.png), the outgoing path starts beside one security icon and can appear to exclude the other data sources. Use a clear shared collection point or a selected asset to explain scope. Familiar brands are illustrative identities, not evidence that those products are inherently malicious. |

The [rejected D3 incident diagram](../../blog/presentations/harnesses-skills-context/artifacts/slide-03m-instrumental-intrusion-v2-d3/slide-03m-final.png) was reasonably organized: it separated trust regions and included a stop/escalate branch. Its [selection rationale](../../blog/presentations/harnesses-skills-context/artifacts/slide-03m-instrumental-intrusion-v2-d3/diagram-selection.md) also rejected misleading quantitative forms. The user still preferred documented evidence. A technically defensible diagram can fail the communication task when the audience needs credibility and concrete examples more than another abstraction.

## 5. Where the feedback belongs

The maintained skill sources are under `skills/`. Installed `mermaid-animated-svg` and `d3-animated-svg` copies under `.codex/skills` are different from the current maintained `mermaid` and `d3` bundles. Both installed entrypoints reference a parent `ANIMATED_VISUAL_TOKENS.md` that was absent at that installed location during this review. This is a current installation/resource issue; it is not proof of what the runtime contained during every historical iteration.

Current skill instructions already address several failures. Add operational support or a small reusable regression case where necessary; do not repeatedly add “preserve colors” prose to a skill that already says it.

| Owner | Existing useful guidance | Narrow improvement suggested by this case |
| --- | --- | --- |
| [mermaid](../skills/mermaid/SKILL.md) | Explicit-family fidelity, source preservation, rendered inspection, final animation/static agreement, accessible metadata. | Railroad-specific semantic grouping; exact selector cardinality; style-role invariance after ordering edits; repeated-label handling; a shared anchor export for consumers. Include TreeView parent/child reveal coverage. |
| [d3](../skills/d3/SKILL.md) | Deterministic layouts, explicit output contracts, composition critique, offline SVG, meaningful final state. | A route-follower/trace recipe using one progress model; state-machine fixtures for one run and several blocked actions; paired input/role scenarios; explicit distinctions between synthetic paths and measured probabilities. |
| [procedural-svg-animation](../skills/procedural-svg-animation/SKILL.md) | Shared clock, seeded state, path-following invariants, readable static state, alpha/portability discipline through SVG-native output. | Reuse its “follower never outruns reveal” and shared-clock mechanisms. Add a portable one-shot construction/hold fixture if useful. Do not route a notation-preserving railroad task through a procedural art generator. |
| [compose-synchronized-svg](../skills/compose-synchronized-svg/SKILL.md) | Canonical shared state, semantic relationships, theme preservation, composition/browser review. | Relevant when several semantic panels share state. A simple railroad plus gates needs a small composition contract, not an automatic expansion into a large business dashboard. |
| [animated-svg-to-gif](../skills/animated-svg-to-gif/SKILL.md) and the export workflow | Browser-accurate capture, explicit dimensions/timing, final-state QA. | Make the requested APNG/PNG delivery contract explicit in the actual owning export workflow. Do not silently force APNG work through a GIF-only route. Test blend/disposal, alpha, one play, and the decoded final state. |
| Presentation/orchestration workflow | Persistent briefs, components, revisions, sources, and canonical/suggestions targets. | Own the current asset manifest and dependency invalidation. Render-specific skills should not each duplicate deck identity, email packaging, or release instructions. |
| Installation workflow | Self-contained skill bundles and source ownership. | Verify installed bundle identity and runtime resource resolution. Repair installed copies from their canonical source through the appropriate installation workflow, rather than editing an obsolete copy as if it were canonical. |

The [skill-creator guidance](../../../.codex/skills/.system/skill-creator/SKILL.md) informed this review's distinction between transferable rules and one user's visual preferences. The recommendation is a small amount of clear routing plus reusable mechanics and regression evidence, not an ever-longer universal checklist.

## 6. Proposed acceptance scenarios for the next skill improvement pass

These tests are **proposed, not executed**. Run them against an isolated skill bundle when implementing behavior changes, following the repository's evaluation methodology. Preserve failed examples. Test novel labels and dimensions as well as this deck so the skill does not merely memorize one diagram.

| ID | Realistic revision prompt | Expected observable result |
| --- | --- | --- |
| R01 | “Use this `railroad-ebnf-beta` source, yellow-dominant colorset2, and reveal complete blocks left to right.” | Correct family; stable semantic groups; labels/boxes/connectors appear coherently; return loop appears last; complete final state. |
| R02 | “Move System Prompt to the start. Keep the original colors.” | Only the intended grammar order changes; logical fill/stroke/text roles remain the same in SVG, APNG, still, and inset consumers. Compare style signatures by semantic identity, not position. |
| R03 | “Rename an extension to a longer label and show hooks above and below.” | Unique anchors survive reflow; leaders, callouts, expansion arrow, and crop stay correct; unsupported transforms are resolved or rejected clearly. |
| R04 | “Highlight Skills” with duplicate `Skills` labels in different rules. | The target is scoped to the intended rule; exactly one block is highlighted, or the tool reports ambiguity. An absent match cannot produce a successful blank highlight. |
| R05 | “Fit this wide transparent SVG into a taller placeholder.” | Padding remains transparent; legitimate white card/node fills remain intact; alpha is verified over light and dark surfaces. |
| R06 | “Make one copyable animation from the railroad and hook overlay, keeping editable sources.” | Independent sources plus one synchronized composite; shared clock; source filenames accurately distinguish animated versus final-only SVG. |
| R07 | “One agent is blocked twice, backtracks, and then passes.” | Actor/run identity remains constant; two blocked encounters; one allowed crossing; no progress beyond a blocked point before the allowed event. |
| R08 | “Follow this uneven route, including a reversal, while constructing the line.” | Follower and trace use one parameterization; phase transitions and final positions agree across SVG and raster export. |
| R09 | “Keep all icons, but focus the next slide on three connection scenarios.” | Inventory retained; positions stable across scenes; selected edges match the configured topology; inactive nodes dim without becoming unidentifiable; brand/source mapping stays correct. |
| R10 | “Export the final review image and a package with animated and static slides.” | Every slide has its required visual; APNG finals are decoded correctly; static visuals remain PNG; text-card images are separate; sources stay readable/editable in their designated artifact. |
| R11 | “Show two skills on the same space with different preferences.” | Geometry and seed unchanged; only the declared role/context-dependent salience changes; visible outcomes carry the intended comparison without implying weight updates. |
| R12 | “Make this evidence-heavy slide clearer.” | Facts and figure values remain intact; distinctions among observed incident, experiment, and analogy remain visible; a source figure can be retained instead of being automatically replaced by a custom chart. |

For geometry/animation scenarios, sample named events and nearby boundary times. For typography, inspect at actual placement size, including a 1280 × 720 presentation preview. For projection-sensitive designs, assess label and mark visibility on the intended light background. Avoid an arbitrary universal pixel-size rule; the relevant issue is readability at the actual destination.

Use two independent gates: **mechanical validity** and **communication quality**. File existence, palette membership, graph counts, and a nonblank screenshot do not establish that a viewer can follow the main relationship. Conversely, an attractive screenshot cannot excuse an incorrect sequence, missing block, false quantitative encoding, or inaccessible source.

## 7. A compact persistent contract would prevent most repeated repairs

For future work of this kind, one scene/slide record should carry:

1. **Identity:** stable slide ID, canonical/suggestion target, current revision, and the specific requested change.
2. **Meaning:** one reader question, entities/relations, exact notation, metaphor versus measured evidence, and the outcome to retain.
3. **Visual roles:** approved palette values, semantic color roles, typography, backgrounds, z-order, and intended placement size.
4. **Motion:** named phases, component dependencies, actor/run identity, seed, one master clock, and an explicit end/loop rule.
5. **Delivery:** editable source, component images, synchronized composite when requested, final still, text card, sources, and a manifest tying derivatives to source hashes.

On a later request, update only the affected fields, calculate which derivatives become stale, and verify the resulting changes against that record. The user can still evolve the concept; the record prevents an intentional evolution from accidentally discarding unrelated decisions.

Project-specific preferences to preserve in this deck include English copy, yellow dominance, dark-yellow and light-yellow roles, white text cards with a yellow left border, transparent diagram exports, short linked sources, semantic construction, and one-shot review animation. They should be a named project profile, not compulsory styling for all Mermaid or D3 work. Likewise, the hamster and railroad metaphor are this presentation's language, not defaults for unrelated topics.

## 8. Evidence and verification record

Fresh checks used Pillow to reconstruct APNG frames and inspect alpha/pixel differences, XML parsing for scene structure, source/package hashes, and independent arithmetic on saved route geometry. They did not rebuild the slides or run a model-based skill evaluation.

| Saved animation | Dimensions | Frames / duration | Plays | Identical final tail |
| --- | --- | --- | --- | --- |
| Combined Harness + Agent + hooks | 860 × 850 | 168 / 14 s | 1 | 21 frames / 1.750 s |
| Core Harness block construction | 1920 × 1080 | 90 / 6 s | 1 | 19 frames / 1.267 s |
| Search mesh | 1130 × 850 | 144 / 12 s | 1 | 8 frames / 0.667 s |
| One-run blocking-hook mesh | 1130 × 850 | 168 / 14 s | 1 | 17 frames / 1.417 s |
| Two-role skill mesh | 1130 × 850 | 168 / 14 s | 1 | 18 frames / 1.500 s |

All five files have transparent pixels in the decoded final frame. This establishes partial transparency, not that every intended region is correctly transparent. The inset's opaque black padding is a separate component-level failure.

Review surfaces:

- [Measurement script](../../blog/output/skill-feedback-20260904/audit_artifacts.py) and [measurement report with source hashes](../../blog/output/skill-feedback-20260904/artifact-audit.json).
- [Harness construction frames](../../blog/output/skill-feedback-20260904/harness-blocks-frames.jpg).
- [Combined hooks frames](../../blog/output/skill-feedback-20260904/hooks-combined-frames.jpg).
- [Search path frames](../../blog/output/skill-feedback-20260904/search-mesh-frames.jpg).
- [One-run hook frames](../../blog/output/skill-feedback-20260904/hooks-gate-frames.jpg).
- [Role-dependent skill frames](../../blog/output/skill-feedback-20260904/skills-mesh-frames.jpg).
- [D3 qualitative review](../../blog/output/skill-feedback-20260904/d3-search-review.md). Its numeric score is explicitly a reviewer judgment, not a calibrated automatic benchmark.

The detailed report's cross-repository evidence links assume `skills` and `blog` are sibling checkouts, as on this workstation. The installed skill-creator link assumes the current user home layout. No private knowledge-corpus text was copied into this report.

Repository checks for this documentation pass all passed: `validate-pattern-ids.py`, `validate-skills.py`, `test-skill-independence.py`, and `check-repo-payload.py`, run through `uv run --script scripts/<name>`. The link check resolved all 43 local links across the root entry file, this report, and the documentation index. The changed index passed `git diff --check`. These checks establish documentation/repository consistency; they do not establish that the proposed skill improvements are implemented. Existing unrelated working-tree changes were preserved.

## 9. Suggested improvement order

1. Repair semantic selectors, explicit alpha padding, and route progress consistency. These have direct evidence and narrow fixes.
2. Make the approved theme and geometry identity survive structural edits; invalidate dependent insets, stills, and composite animations together.
3. Consolidate playback around one scene timeline and record the actual rebuild sources for every promised editable animation.
4. Add the corresponding regression scenarios to the owning skills without duplicating orchestration responsibilities.
5. Revisit projection readability, the role-comparison end state, overloaded evidence layouts, and the distinction between guidance and enforced execution.

The desired improvement is fewer repeated production corrections while retaining useful conceptual iteration with the user.
