# Semantic audio cues

Use the bundled aligner when a figure's guide or highlight must follow specific
spoken references. Preserve existing native voiceovers during a visual-only
revision. Downloaded audio, reviewed native timings or a local ASR transcript
may supply the word evidence. Do not claim estimated script positions were
measured, and do not invent word timestamps if the interface exposes none.

The script consumes three JSON files:

- Transcript: `{"segments":[{"words":[{"word":"60","start":7.37,"end":7.95}]}]}`
  with global audio seconds. Keep the actual source model/evidence alongside it.
- Timing: `{"scenes":[{"id":"split","start":0,"end":20.7,"duration":20.7}]}`.
- Cue spec: `{"scenes":[{"id":"split","cues":[{"target":"split-train",
  "phrase":"sesenta"},{"target":"split-validation","phrase":"veinte",
  "occurrence":1},{"target":"split-test","phrase":"veinte","occurrence":2}]}]}`.

Run:

```text
uv run --script <skill-root>/scripts/narration_cues.py --transcript words.json --timing timing.json --spec cue-spec.json --output cues.json
```

The aligner normalizes punctuation, accents and a small Spanish number alias
set. `alternatives` accepts reviewed ASR spellings; `occurrence` is one-based
within the scene. Unmatched phrases, out-of-order cues and invalid intervals
fail instead of silently substituting an estimated time. The output preserves
target IDs and adds scene-local `at`, `end`, global `audioStart`, `audioEnd`,
`travelSeconds` (default 0.28) and approximate-ASR evidence. Keep its source
files so a new voice or scene order can be re-aligned in one command.

Give this cue file to the visual producer. Resolve IDs from actual label/mark
geometry after fonts load, reserve space beside each object, and start travel
before `at` to arrive on the spoken word. Keep the guide off labels and
important strokes at its largest size. Repeated 20% values require separate
targets and occurrences. Shorten travel rather than letting the point lag
through the next reference. A camera transition may require a documented small
opening delay; do not apply that delay to already visible percentages.

Render the full measured speech budget. Static frame reuse is safe only when
the complete visual state is unchanged, including guide target, position and
radius. Inspect an encoded excerpt with the actual audio. Verify unchanged
native scene/voice timing after replacing the visual clip, then export normally.

For a visual-only revision, prefer the selected video's native **Replace video
→ Upload** control when available. It preserves the object and approved voice.
Use distinct revision filenames and verify the inserted filename, scene count,
native scene announcement and total duration before continuing. Replacement can
change scene length. If a wrong clip is inserted, replace it with the correct
clip and recheck the recovered duration. Pass each file path explicitly to UI
helpers; do not let a helper reuse a stale pending-file reference across calls.
When the extension uploader requires broader file access, use the normal native
file picker if available. Derive fresh controls and observe the actual dialog.
