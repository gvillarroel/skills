# Transition Pattern Catalog

Use this catalog when a video needs several different transition types. Pick patterns by semantic job, not by decoration.

## Metro Minimal Tonal Motion Transitions

Use these when the prompt names Metro Minimal Tonal Motion, Masonry, megacanvas, hard square geometry, no padding, grayscale hierarchy, or design feedback that the video is not following the design. Treat the transition as navigation inside one large modular object unless the source explicitly requires a cut to another visual system.

- **Zoom To Subsection**: push into a declared zone, chart, table, node group, or block. End with the target comfortably framed, unclipped, grid-aligned, and still showing enough context to understand where it lives.
- **Zoom Out To System**: pull back from a detail to the full megacanvas. Use when the story needs context, dependencies, or a final synthesis.
- **Pan To Zone**: move horizontally, vertically, or diagonally between named functional zones. Keep the camera stable and axis-aware; the move should reveal a new section, not drift.
- **Expanding Block Cover**: a selected 0-radius module grows until it covers the frame, then shrinks, slides, or unmasks the next section. The block is the content boundary; do not place padded labels inside it.
- **Surface Wipe**: a flat rectangular surface crosses the frame as a clean curtain. Use grayscale or a semantic state red; avoid gradients, soft shadows, or soft-corner masks.
- **Tile Morph**: a module changes size, track, or role while preserving square edges, shared grid lines, and zero internal padding. Good for KPI-to-chart, table-cell-to-matrix, node-to-graph, or summary-block-to-detail.
- **Masked Reframing**: a rectangular aperture opens inside a block and the camera enters the revealed view. The mask must be square-edged and semantically tied to the source block.
- **Masonry Block Motion**: blocks enter, fit, push neighbors, reveal internal marks, expand to detail, or collapse back into the wall. Validate varied block sizes, shared edges, and a clean final wall.

## Pattern Cards

### Persistent Object Flight

- Use when the same work item, token, cursor, packet, or proof must survive the cut.
- Visual mechanic: the object exits the source scene, crosses the boundary, and lands on the first useful target in the next scene.
- Preserve at least two identity cues: shape, color, size, label, rhythm, trail, or arrival behavior.
- Validate that the viewer can point to the same object before and after the cut.
- Do not overuse this pattern. If most cuts already move one object across the screen, choose a scene-level pattern below instead.

### Static Anchor Sweep

- Use when one element should stay still while the rest of the scene changes around it.
- Visual mechanic: hold a frame, axis, logo, card, or focal object fixed while outgoing content moves off-screen and incoming content moves in from another direction.
- Good for preserving a concept while changing its environment.
- Validate that the static anchor truly stays stable in screen space.

### Object Color Cover

- Use when a small object, verdict, or state should flood the entire screen with its color.
- Visual mechanic: expand the object's color into a full-screen cover, optionally hold a short word or symbol, then wipe/fade back to a different scene.
- Square-edge variant: expand the object into an axis-aligned rectangle or stepped shutter that preserves 0-radius corners.
- No-padding variant: the cover rectangle is the content boundary; do not reveal an inset card or padded label inside the cover.
- Good for breaking visual rhythm and making color carry state.
- Validate that the cover color has a semantic reason and the next scene inherits or resolves it.

### Extreme Zoom Reframe

- Use when the next scene should feel like it is inside a detail of the previous scene, or when the transition needs high spectacle.
- Visual mechanic: zoom so far into a card, node, check, gate, or line that it fills the screen; then zoom out to reveal a new composition.
- Keep the zoom target simple and high contrast.
- Validate that the zoom creates a new space, not just a larger version of the same frame.

### Full-Screen Color Card

- Use when the sequence needs a hard reset between visual systems.
- Visual mechanic: fill the entire frame with one semantic color, show one short state word or symbol, then return to a light scene with changed elements.
- Good for proof, failure, approval, blocked, handoff, or mode-change moments.
- Validate that the color card is brief and does not become an unrelated title slide.

### Spatial Portal Reveal

- Use when the next scene is a different conceptual space.
- Visual mechanic: a window, tunnel, aperture, or corridor opens briefly and shows the target space before the cut completes.
- Square-edge variant: use a rectangular aperture, grid cell, split-panel door, or orthogonal corridor; avoid circular portals unless the source style calls for them.
- Good for loop-to-tool, local-to-system, interface-to-runtime, or data-to-diagram changes.
- Validate that the portal shows the destination, not a decorative wipe.

### Color State Wash

- Use when the persistent element changes role or verdict.
- Visual mechanic: a color field starts from the source object and floods only the target region or object that inherits the role.
- Square-edge variant: flood a bounded rectangular region, column, lane, or board cell instead of a soft radial cloud.
- Keep color tied to state. Do not use hue as the only hierarchy signal; hierarchy should still be carried by distinct grayscale levels.
- Validate that color change happens because state changed.

### Camera Parallax Move

- Use when the abstraction level changes or the viewer must see a hidden layer.
- Visual mechanic: push in, pull out, pan, or parallax drift reveals another plane of the same system.
- Keep text readable and avoid rotating unless depth is meaningful.
- Validate that the move reveals new structure, not just motion.

### Interrupt Gate Snap

- Use when a policy, failure, risk, or surprising constraint stops the expected flow.
- Visual mechanic: the motion path snaps into a barrier, red gate, shutter, or verdict line.
- Use sparingly; it should create contrast with smoother neighboring transitions.
- Validate that the interruption explains why the next scene exists.

### Morph Continuity

- Use when one diagram role becomes another.
- Visual mechanic: the outgoing object's bounding box, line, or card reshapes into the incoming object.
- Square-edge variant: preserve rectangular bounds, straight edges, corner radius, and zero internal padding while changing size, fill, internal marks, or grid position.
- Preserve enough geometry for continuity while changing state color or role.
- Validate that the morph has a source and target, not an arbitrary shape change.

### Match Cut Axis

- Use when two scenes share a compositional axis, center point, orbit, or grid cell.
- Visual mechanic: cut when the outgoing and incoming shapes align in screen position or proportion.
- Good for formula-to-diagram, chart-to-node, or panel-to-panel continuity.
- Validate that the eye does not need to hunt after the cut.

### Depth Stack Reveal

- Use when the next scene is behind, under, or inside the current one.
- Visual mechanic: layers slide apart, a foreground panel lifts, or the camera passes through a transparent surface.
- Good for showing harness internals, trace history, or hidden validation layers.
- Validate that foreground and background roles are clear during the move.

### Negative Space Cut

- Use when a calm reset is needed after dense motion.
- Visual mechanic: objects clear a path or collapse toward an empty area where the next focal object appears.
- Good before a final summary, definition, or proof.
- Validate that the pause creates focus, not dead time.

## Sequence Rules

- In a sequence of four or more cuts, use at least three different mechanics unless repetition is the lesson.
- Put the strongest surprise where the story turns, not at every boundary.
- Alternate smooth continuity with contrast. For example: persistent object, portal, interrupt, morph.
- Change only the channels that carry meaning: object, color, camera, space, rhythm, or composition.
- Do not stack every effect on every cut. One primary mechanic plus one supporting cue is usually enough.
- Every pattern choice must name one primary semantic mechanic and one visual continuity cue.
- For hard-edge styles, pick the square-edge variant of portal, morph, color cover, depth reveal, or mask transitions unless a source asset requires soft-corner geometry.
- For no-padding or grayscale-level styles, preserve flush box geometry through the cut and state which grayscale levels carry outgoing, bridge, and incoming hierarchy.
