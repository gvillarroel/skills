# Visual Metaphor Design

Use this reference before coding a concept video beat, redesigning a weak scene, or responding to feedback that an animation feels generic, copied, decorative, or text-dependent.

## Required Pre-Code Artifact

Write a short design note before implementation:

- **Concept claim:** What should the viewer understand from the diagram before narration adds detail?
- **Mechanic:** What changes because of what? Name the input, transformation, output, feedback, constraint, or consequence.
- **Candidate metaphors:** Generate two or three plausible visual metaphors. Reject at least one with a concrete reason.
- **Chosen metaphor:** Explain why it reveals the mechanic better than the rejected alternatives.
- **Visual vocabulary:** Define repeated roles for shapes, colors, motion, scale, layout regions, and state changes.
- **Composition contract:** Define the grid, shared baselines, edge/corner policy, and focal armature before drawing details.
- **Reuse decision:** Name any reused D3/gallery/component pattern and state which semantic role and source anchors it preserves. Do not reuse a prior pattern only because it looked good.
- **Narration split:** List which facts narration will carry so the frame can stay mostly diagrammatic.

Keep the note concise. Its purpose is to prevent coding before the explanatory model is clear.

## Choosing Metaphors

Pick metaphors that expose causality, not merely activity.

- Use a **pipeline** when order and handoff matter.
- Use a **matrix or grid** when capacity, slots, memory, addressability, or accumulation matters.
- Use a **roulette or sampler** when weighted chance and selection matter.
- Use a **queue** when waiting, latency, retries, or throughput matters.
- Use a **ledger or meter** when work becomes measurable cost.
- Use a **gate, filter, or checkpoint** when permission, blocking, redaction, or policy matters.
- Use a **map or route network** when routing, tool choice, dependencies, or paths matter.
- Use a **loop** when repeated observation, retry, or context growth matters.
- Use **layers** when enclosure, runtime boundaries, or responsibility separation matters.

This is not a D3 taxonomy. After selecting the metaphor, read `visual-density-pattern-bank.md` when the video needs richer, more dynamic, lower-text structure; use the D3 skill to choose the exact visualization primitive or gallery example when available; then use `scene-pattern-recipes.md` when an approved video scene pattern should be reused or extracted into a shared helper.

## Visual Vocabulary Rules

- Assign one semantic meaning to each recurring shape within a video. If a square matrix means context, do not later use the same square matrix as a generic decoration.
- Assign one semantic meaning to recurring motion as well as recurring shapes. A sweep, pulse, orbit, cursor, or flow token may repeat only when it keeps the same narrative role; otherwise choose scene-specific movement from the local diagram.
- Reuse color by role, not by preference. A color can mean source, selected item, blocked path, accumulated work, or model family, but it should not change meaning without a visible reset.
- Preserve object identity through transformations. A token, packet, trace, or request should keep enough color/order/shape continuity for the viewer to track it.
- Prefer visible cause/effect verbs: enter, split, rank, sample, append, block, retry, cache, evict, meter, branch, merge.
- Build a local grammar before building a scene: nouns are shapes, verbs are motions, adjectives are state changes such as opacity, scale, fill, stroke, or position.
- For Metro Minimal Tonal Motion, start from a modular megacanvas: define multiple functional zones, the camera path between them, and the block or tile transition that preserves continuity. Do not reserve visible title, subtitle, caption, checked-date, or draft bands; keep those outside the frame in source packages, filenames, manifests, or post-production copy.
- For Metro, technical, editorial-grid, terminal, blueprint, or hard-edge styles, make rectangles square/0-radius by default, snap major bounds to a grid, and avoid pills, blobs, soft panels, or rounded portals unless they are source-native.
- For no-padding box critiques, treat the rectangle edge as the content boundary. Do not create inset bars, padded labels, inner chips, or nested panels inside a box. Put labels on the boundary, on an adjacent lane, or in a separate flush rectangle. Use gutters outside boxes for separation.
- For level or hierarchy critiques, assign each semantic level a distinct grayscale value and keep those levels stable across scenes. Use hue for state or role, not as the only hierarchy signal.
- For Metro design feedback, load `metro-minimal-tonal-motion.md` and treat its rejection gate as blocking. A video that passes render-state, contact-sheet, and Metro audit JSON can still fail if it reads as slides with labels instead of a navigable modular object.

## Reuse Gate

Before reusing an earlier scene or generic renderer, answer:

- Does the old visual pattern express the same mechanic, or only the same aesthetic?
- Would a viewer infer the new concept if the labels were removed?
- Is the repeated object keeping the same role across beats?
- Is any repeated background or validation motion keeping the same role, or only keeping pixels changing?
- Does the scene add a new visual verb needed by this concept?
- Is there a better metaphor even if it requires new geometry?
- Does the frame have a named grid, baseline, or armature that major objects attach to?
- Does the edge/corner policy match the requested aesthetic and remain stable through motion?
- Are boxes flush with zero internal padding, and are hierarchy levels distinguishable by grayscale values rather than extra padded interiors?
- Did you select a visual-density pattern family for complex videos, and does that pattern add encoded marks or state rather than more text?

If the answer is weak, design a new metaphor first and only reuse low-level helpers such as palette, typography, timing, matrix layout, token geometry, or capture scripts.

## Review Checklist

During contact-sheet and playback review, flag:

- motion that looks busy but does not change state
- recurring background motion that makes unrelated scenes feel structurally identical
- diagrams that only work because labels explain them
- reused structures with changed meaning
- legends added because the metaphor is unclear
- simultaneous animations that compete instead of coordinating around one mechanic
- scenes that preserve the prior visual language but fail to introduce the concept's own mechanic

Fix these by changing the metaphor, object roles, or motion grammar before adding more text.
