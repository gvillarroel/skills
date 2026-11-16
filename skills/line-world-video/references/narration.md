# Explain the subject

Write narration about the subject's mechanisms, decisions, evidence and
consequences. Let the visual carry its layout, decoration and animation. Before
generating speech, ask what the viewer learns from each sentence. Rewrite a
sentence that only explains how the video was drawn or disclaims a harmless
simplification.

| Avoid spending speech on | Explain instead |
| --- | --- |
| The animation represents a mechanism and does not measure speed | What runs in parallel, what each worker computes and how results are used |
| The diagram is a map rather than reality | The relevant entities, their relationship and the consequence of that relationship |
| The scheme simplifies eight weighted layers | What early and later layers learn and how that supports classification |
| The red dot identifies the part being explained | The operation or result at that destination |
| The chart translates the table's rows | The meaningful comparison, magnitude, units and interpretation |

Keep navigation short and attached to substance. In a tour of an original
paper, "Figure 2" or "the right column" can orient the viewer. Follow it with
what that passage establishes. Do not narrate every pan, color or pointer move.
Let each sentence connect to the next through the topic rather than through
screen directions.

Keep limitations that change the interpretation: synthetic versus measured
data, a selected eight-task sample versus an entire benchmark, an ensemble
versus a single model, uncertainty and the absence of a general guarantee.
State the relevant scope once, close to the claim. A useful limitation explains
what the evidence supports. Do not erase it merely because it contains "not"
or "illustrative". Move production notes, crop choices and nonessential
representation details to the editable source/review record.

The absence of a speed measurement does not itself require a spoken warning
when the scene only explains a functional mechanism and makes no speed claim.
Omit that warning in such a scene. State measurement scope when an actual
number, axis or comparison could otherwise be mistaken for measured evidence.

Run the inexpensive candidate scan before speech generation:

```text
uv run --script <skill-root>/scripts/narration_review.py --story story.json --output narration-review.json
```

The scan identifies common English/Spanish production commentary for editorial
review; it cannot judge meaning or certify a good script. Read every scene,
including scenes with no matches. Keep a short reviewed decision for each
candidate: rewrite, remove or retain with a concrete interpretive reason.
For a revision, pass `--baseline previous-story.json` to list changed scripts by
stable ID. That list identifies voices to regenerate; it does not certify
unchanged visuals or joins. Re-measure actual audio and re-align semantic cues
for changed voices before rendering. Preserve unaffected voices and inspect
the new reading holds, late cues and outgoing scene joins.
