# Visual Metaphor Design

Use this reference before coding a concept video beat, redesigning a weak scene, or responding to feedback that an animation feels generic, copied, decorative, or text-dependent.

## Required Pre-Code Artifact

Write a short design note before implementation:

- **Concept claim:** What should the viewer understand from the diagram before narration adds detail?
- **Mechanic:** What changes because of what? Name the input, transformation, output, feedback, constraint, or consequence.
- **Candidate metaphors:** Generate two or three plausible visual metaphors. Reject at least one with a concrete reason.
- **Chosen metaphor:** Explain why it reveals the mechanic better than the rejected alternatives.
- **Visual vocabulary:** Define repeated roles for shapes, colors, motion, scale, layout regions, and state changes.
- **Reuse decision:** Name any reused D3/gallery/component pattern and state which semantic role it preserves. Do not reuse a prior pattern only because it looked good.
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

This is not a D3 taxonomy. After selecting the metaphor, use the D3 skill to choose the exact visualization primitive or gallery example.

## Visual Vocabulary Rules

- Assign one semantic meaning to each recurring shape within a video. If a square matrix means context, do not later use the same square matrix as a generic decoration.
- Reuse color by role, not by preference. A color can mean source, selected item, blocked path, accumulated work, or model family, but it should not change meaning without a visible reset.
- Preserve object identity through transformations. A token, packet, trace, or request should keep enough color/order/shape continuity for the viewer to track it.
- Prefer visible cause/effect verbs: enter, split, rank, sample, append, block, retry, cache, evict, meter, branch, merge.
- Build a local grammar before building a scene: nouns are shapes, verbs are motions, adjectives are state changes such as opacity, scale, fill, stroke, or position.

## Reuse Gate

Before reusing an earlier scene or generic renderer, answer:

- Does the old visual pattern express the same mechanic, or only the same aesthetic?
- Would a viewer infer the new concept if the labels were removed?
- Is the repeated object keeping the same role across beats?
- Does the scene add a new visual verb needed by this concept?
- Is there a better metaphor even if it requires new geometry?

If the answer is weak, design a new metaphor first and only reuse low-level helpers such as palette, typography, timing, matrix layout, token geometry, or capture scripts.

## Review Checklist

During contact-sheet and playback review, flag:

- motion that looks busy but does not change state
- diagrams that only work because labels explain them
- reused structures with changed meaning
- legends added because the metaphor is unclear
- simultaneous animations that compete instead of coordinating around one mechanic
- scenes that preserve the prior visual language but fail to introduce the concept's own mechanic

Fix these by changing the metaphor, object roles, or motion grammar before adding more text.
