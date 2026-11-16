# Measured speech and continuous visuals

## Native scene inventory

Read the current count from the actual scene buttons, then select each scene
and retain its newly emitted announcement. A previously announced "10 of 10"
can be stale while eleven scene buttons are present. Record
`{"sceneButtonCount":11,"scenes":[{"order":1,"announcement":"fresh native text"}]}`
with every current scene, including empty ones. Run:

```text
uv run --script <skill-root>/scripts/vids_inventory.py --story story.json --observed inventory.json --output inventory-check.json
```

The helper parses the observed English UI's order, total, duration, object count,
audio starts and MP4 title. It rejects blank visual scenes, incomplete/stale
inventories, wrong ordered clips and changed extents. It does not inspect an
account or confirm that same-named media pixels were replaced. For another UI
language, retain the observation and adapt its parsing explicitly; do not infer
success from unparsed text. Correct a proven unintended blank scene through the
native reversible scene action, preserve all narration, then inventory again and
verify the actual export. This workflow does not authorize deleting useful content.

Keep an explanatory object visible throughout each scene and native transition.
A guide dot, divider or empty panel alone is insufficient, even if a pure-white
frame detector passes. Inspect the downloaded export rather than relying on
source thumbnails. When the optional Line World producer is available, use its
whole-film content scan; otherwise inspect scene openings and joins and use
ordinary frame extraction. Preserve outgoing context until incoming geometry is
visible. Retain measured voice timing when correcting a visual-only gap.

Use word count only to estimate the draft. Record each inserted voiceover's
actual duration and each scene's actual duration. Preserve the voice naturally;
adjust the visual budget. Keep a modest lead-in and tail when needed. Inspect
silence at joins because insertion of a long video may lengthen a scene that
previously fit the voice exactly.

For a clip with a reusable final hold, put essential visual events before its
`essentialAnimationSeconds`. A scene may trim only after those events. If its
speech is shorter, rerender the visual rather than cutting an explanation in
half. If speech is longer than the available clip, extend the intentional hold
or rerender. Do not speed speech or silently repeat animation to fit.

Keep one stable camera/world model across shots when the content supports it.
End each shot with the full previous state visible; start the next there before
its pan. Test endpoint frames against the declared transition. A designed cut
can differ; record its purpose instead of demanding identical pixels everywhere.
Keep colors, semantic IDs and quantitative scales stable across both states.

Use measured scene lengths to derive contiguous starts and ends. Never
hand-edit cumulative offsets in several places. The helper rounds to frames
and validates that the resulting budget covers speech plus explicit pauses.
After export, compare real duration and audio presence; inspect actual frames
and listen around each boundary. A matching total alone cannot prove sync.

Prefer plain natural-language narration. Read formulas, units and acronyms in
their intended pronunciation and keep essential notation in the figure.
Do not add dramatic audio tags, music or abrupt voice changes by default.

## Millisecond extents and final reading holds

Native auto-fit scenes may end between video frames. The ordinary visible timer
rounds to tenths and accessibility summaries may truncate whole seconds. When
available, select scenes with screen-reader support and read the native scene
announcement including milliseconds. Preserve that evidence and its resolution.
An observed scene containing the full voice is a conservative upper bound on
speech length when isolated audio properties are unavailable; label it as a
bound rather than claiming an exact waveform measurement.

Ceil the visual coverage to the next output frame: `frames = ceil(seconds * fps)`.
Extend only a static final hold, then replace the matching video object and
verify its scene and voice remain intact. Recheck the native duration after the
replacement. Do not floor a 20.440-second extent to a 20.400-second clip. Avoid
adding estimated word-count time as if it were an observed duration.

The compiler consumes the final measured scene budget. Its frame rounding does
not repair source media. Inspect exported frames around every join for missing
objects, white flashes or double audio, including the last few frames of a
scene and the first frames of its successor. Keep listening evidence and
automated transcript evidence distinct.
