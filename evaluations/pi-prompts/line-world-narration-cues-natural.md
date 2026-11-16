Use skills/line-world-google-vids as a read-only resource. Read ../prompt.md first.
I'm revising only the visuals of a Spanish narrated film; the voice is already
approved. In scene allocation, global audio seconds100–120 (duration20), ASR
reports these words: "sesenta" at106.4–107.0, "veinte" at107.3–107.7, "y" at
107.7–107.9, "veinte" at107.9–108.8. The corresponding figure has targets
allocation-main, allocation-check and allocation-test, in that order. In scene
monitor, global seconds120–130 (duration10), words "error" occur at122–122.4
and "real" at122.4–122.8; that phrase refers to target observed-error.

Prepare cues.json for the visual producer, with scene-local cue times and the
global audio evidence, keeping the two equal twenty values distinct. Include
handoff.md explaining how to preserve the approved voice, connect the cues to
objects, revise timing cheaply if audio changes, and check that the finished
film follows those references without covering its labels. Treat ASR as
approximate. Do not open or modify a live account for this offline preparation.
Required exact outputs: cues.json and handoff.md. Keep generated files outside
the read-only skill, and do not read sibling skills or acceptance examples.
