# Google Vids adapter validation — November 15, 2026

Skills: line-world-google-vids and the line-world-video orchestration route.
Model exception: openai-codex/gpt-6.1-sol with medium thinking, continuing the
recorded Line World account exception because Spark was unavailable for this
account. No ambient skills, extensions, context files, templates or themes were
enabled. Runtime-only payloads remained unchanged in every isolated run.

## Deterministic and isolated checks

- `uv run --script skills/line-world-google-vids/scripts/test_vids_plan.py`: 8/8 pass.
- `uv run --script projects/ml-overfitting-vids/scripts/run_skill_evaluations.py`:
  contract 1/1, naturalistic 3/3, generalization 3/3, boundary 1/1 pass.
- After promoting the millisecond/frame-ceiling workflow, an additional final
  naturalistic run passed with the final adapter resource payload.
- The changed primary orchestrator passed its own native-Vids routing run.
- `uv run --script projects/ml-overfitting-vids/scripts/review_skill_evidence.py`:
  independent output and read-surface review passed for all 10 runs. Model,
  JSON events, zero tool errors, exact output paths, frame totals, script/order
  fidelity and unchanged copied payloads were checked. Boundary evidence rejects
  unmeasured timing. Generalization inputs provide actual observations and need
  not keep an additional handoff worksheet unmeasured; the independent reviewer
  was corrected to honor that prompt instead of imposing a hidden requirement.

Commands, exact outputs, run IDs and read surfaces are retained in
`offline-results-20261115.json` and `reviewed-evidence-20261115.json` here.
Full runtime traces remain in ignored evaluations/runs/. The isolated runs test
offline handoff/evidence gates; they do not claim autonomous native UI execution.

## Real editor and downloaded media

The authorized signed-in Google Vids account created a private landscape project.
Twelve exact Spanish scripts were committed and native Nyla voiceovers inserted.
Twelve local D3/HTML clips were uploaded to their selected matching scenes.
Native playback completed the entire film. The ordinary timer rounds to tenths;
screen-reader scene announcements supply millisecond extents. Five reading holds
were ceiled to the next frame and replaced without changing the voiceovers.

The actual File > Download > MP4 action reported that export had completed and
download had started. Computer Use then stopped on Chrome's downloads shortcut
because the runtime could not confidently verify the browser URL. No further UI
control or alternate UI transport was attempted. The completed local download
was read and copied into the authorized workspace. Its native Google encoder
metadata and byte digest are retained with the local export evidence.

`vids_plan.py verify-export` passed full decode, video, audio and measured-duration
checks. The downloaded movie contains 1920 by 1080 H.264 at nominal 30 fps,
stereo AAC and an optional Spanish subtitle track. Duration is 265.914921 seconds,
with 7,977 video frames. The frame plan is 265.866667 seconds/7,976 frames; native
container/audio padding differs by approximately 48 ms and stays inside the
verifier's two-frame/0.1-second tolerance. It is not claimed byte-for-byte equal
to a local render.

All decoded low-resolution frames were examined for missing visual content:
zero blank frames and zero black frames. Full-resolution samples from every
scene and the actual native contact sheet were inspected. Independent
faster-whisper base CPU/int8 recognition matches 580/597 normalized source words
(97.15%), including the final sentence and all twelve segments in order.
Recognition differences include number spelling, English terms and inflection;
this is automated content evidence, not a human-listening assertion. The first
ASR attempt encountered a PyAV metadata argument incompatibility; decoding to
PCM with FFmpeg and supplying a NumPy array resolved it without changing media.

The synthetic grouped regression is actually measured. Its early-stopping and
production-monitoring views are labeled schematic. The final test interval is a
fixed-model cluster bootstrap, not an unconditional promise of future accuracy.

## Plugin and repository gates

Version 0.6.0 contains six skills, including the adapter. Archive extraction
digests and a clean extracted starter smoke passed. Portable schema validation
and native Codex marketplace/add/list operations all returned zero in a task-local
home, discovering all six expected skill names. No global host install is claimed.

Pattern IDs, skill-independence tests and repository payload checks pass. The
global skill validator and global synchronization remain blocked by four existing
reference-route findings outside this work: curate-semantic-model's
schema-validation-review.md, extract-ontologies' premise-reuse.md, and
extract-with-ontology's keyword-witnesses.md/product-crawl.md. The new coverage
inventory entry was added; no finding belongs to the new adapter. Focused
canonical synchronization and validation pass for both changed skill bundles.
No unrelated skill source was edited. No Pages example was added or published.
