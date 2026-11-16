# Named contributors and relevant contributions, release 0.19.0

Validation date: November 16, 2026 UTC; native production date November 15 local.
Owners: line-world-video and line-world-google-vids. Primary remains validating
for the earlier broad generation limits; this scoped revision passes.

## Problem and correction

The CUDA/AlexNet film showed six reviewed portraits. Three people were not
named in the voice: Ian Buck, Fei-Fei Li and Jia Deng. The three AlexNet coauthors
were named without enough contextual introduction. The image provenance and
bare visible names did not explain the contribution to a new audience.

The updated story says the name and relevant contribution near the first
appearance, shows a concise adjacent full name/contribution caption and binds
the first spoken name to a distinct guide destination. Historical project roles
replace irrelevant current executive titles. Team/coauthor credit is preserved.
The actual paper does not establish separate individual responsibilities for
the three AlexNet authors, so the film credits them collectively at Toronto.

Sources reviewed include NVIDIA's Brook/CUDA history and software-group
announcement, Stanford HAI's Fei-Fei Li biography, Princeton's ImageNet history,
the original 2009 ImageNet paper and the original 2012 AlexNet paper. Links and
the per-person contribution map are in
[the production note](../../projects/cuda-alexnet-vids/people-context.md).

## Reusable plugin changes

`people_context.py` performs a compact preflight from story-owned `people`
bindings and the actual portrait manifest. It rejects missing spoken names,
nearby contribution phrases, short captions, sources or distinct person cues.
Optional local SVG inspection checks actual loaded names/captions, frame bounds,
minimum reading size, clearance from the photograph and label/label separation.
The final gate requires an actual source observation and name cues aligned to
real narration words. It can save the reading screenshot in the same call.
It never operates a cloud account or invents source/audio evidence.

The primary skill, its people/logo reference and shared producer contract carry
the rule. The native Vids adapter requires names/contributions before narration,
and its UI procedure now explicitly enters Edit script and then the Scripts
form, checks Voiceover outdated, handles current-scene replacement and checks
that no accidental canvas text object was introduced.

The utility checks supplied evidence and planned contribution phrases; factual
source review, real speech and encoded viewing remain required. ASR spellings
and word boundaries are approximate. The independent production audio contract
checks contribution phrases in the actual ASR as well as name timings and
reference/final voice correlation.

## Deterministic and isolated validation

```text
uv run --script skills/line-world-video/scripts/test_people_context.py
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

All 12 new deterministic cases pass: complete context, pending observations,
anonymous portrait, name-only speech, unnamed contribution, missing sources and
captions, stale visible role, estimated audio, generic cue substitution,
illegibility/unknown person, incomplete delivery and normalized names.

Seven isolated Pi runs pass strict mode, exact output paths, observed model,
valid JSON, zero tool errors, restricted read surface and unchanged runtime-only
payload. Model exception remains `openai-codex/gpt-6.1-sol`, medium, following
the retained Spark account rejection.

| Case | Run ID under evaluations/runs | Result |
| --- | --- | --- |
| Initial contract | 20261116-line-world-people-contract-sol | Pass |
| Natural preflight/figure 1 | 20261116-line-world-people-natural-sol-1 | Pass |
| Natural preflight/figure 2 | 20261116-line-world-people-natural-sol-2 | Pass |
| Natural preflight/figure 3 | 20261116-line-world-people-natural-sol-3 | Pass |
| Final contract | 20261116-line-world-people-contract-final-sol | Pass |
| Final natural preflight/figure | 20261116-line-world-people-natural-final-sol-1 | Pass |
| Native adapter revision plan | 20261116-line-world-vids-people-sol | Pass |

Prompts are `evaluations/pi-prompts/line-world-people-contract.md`,
`line-world-people-natural.md` and `line-world-vids-people-revision.md`. The normal
runtime figures use fictional people and explicit synthetic timing; they do not
claim measured real speech or native publication. Their current-source replay
passes all four final figures, leaving actual-audio timing pending. The initial
replay incorrectly demanded measured audio from those synthetic fixtures; its
retained rejection correctly identifies missing measured name cues. That was an
evaluator scope error, not a production success or a reason to relabel the fake
timing. See `people-current-forward-replay.json` under local review artifacts.

Initial launch commands stopped at source validation because the expanded
people reference lacked a contents list. The list was added before any model
trial began. In production, the first caption spacing passed the preliminary
photo-clearance check but failed the full focus audit on name/role intersections.
The new inspector includes label/label clearance, the spacing was corrected,
and a retained negative copy of all six real portrait layouts is rejected.
Current source and actual final figures pass. Development evidence is under
`projects/cuda-alexnet-vids/artifacts/revisions/people-context-0190/`.

The actual 312-file archive passes extraction, schema validation, task-local
native Codex installation, exact installed bytes, all six skill registrations
and 187 installed utility tests across 16 suites. General producer source skills
are unchanged; only the dedicated video copies receive the shared handoff.
Canonical/local sync verifies 128 primary files and 22 adapter files.

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| line-world-video-0.19.0.zip | 1,878,115 | 5f0d5cd0c00027d8d1e534d2c1cf96f01f3399426664634d67c1c4053f9f5c39 |
| line-world-video-0.19.0-marketplace.zip | 1,883,511 | 8434bd08e7ebc58d53c74706faac8fff322b259e90974d5ac9fb3d758e1fc6c4 |

Native verification report:
`projects/line-world-video/artifacts/host-checks/openai-0.19.0/verification.json`.

## Actual native film

Three native Nyla voiceovers were revised in the existing project: cuda-platform,
imagenet-scale and alexnet-model. Seven existing voices remain. Five visual clips
were replaced, including their outgoing continuity dependencies parallel-work
and two-gpus. No useful scene or audio was removed. All ten fresh final scene
announcements show one video and one audio start, in order, with no extra scene.
The checked inventory totals 218.396 seconds; authored frame budgets total 218.4.

The real new native voice-reference export was transcribed with the already
available local faster-whisper base model. All six name cues use actual word
timestamps, retaining observed spelling alternatives rather than changing the
correct names. An independent evaluator checks that both the names and the
contribution phrases occur in the actual narration, and that the final movie's
voice windows match the current native reference. All six people pass.

```text
uv run --script projects/cuda-alexnet-vids/scripts/verify_export.py --video projects/cuda-alexnet-vids/artifacts/videos/cuda-alexnet-google-vids-final.mp4 --voice-reference projects/cuda-alexnet-vids/artifacts/revisions/people-context-0190/native-voice-reference.mp4 --reference-timing projects/cuda-alexnet-vids/artifacts/revisions/people-context-0190/voice-observed.json
uv run --script evaluations/contracts/verify-line-world-people-audio.py --story projects/cuda-alexnet-vids/story.json --cues projects/cuda-alexnet-vids/artifacts/data/cues.json --transcript projects/cuda-alexnet-vids/artifacts/data/transcript.json --timing projects/cuda-alexnet-vids/artifacts/revisions/people-context-0190/voice-observed.json --voice-report projects/cuda-alexnet-vids/artifacts/reviews/native-export.json --reference projects/cuda-alexnet-vids/artifacts/revisions/people-context-0190/native-voice-reference.mp4 --output projects/cuda-alexnet-vids/artifacts/reviews/people-actual-audio.json
```

Final native result: 1920x1080, **218.453333 seconds, 6,553 frames**, video/audio
complete decode, zero white/black frames and **56/56 encoded guide arrivals**.
The every-frame content scanner also reports zero insufficient-content frames.
The minimum current-reference voice-window correlation is 0.9909745; this checks
the three intentionally changed voices and the seven retained voices rather
than requiring the new narration to match the old script. All 86 current source
cue/reading item poses, the six portrait caption checks and full render/join
audits pass.

The final native export was opened, played and downloaded from the actual
completed Vids action. Drive showed 3:38, playback progress, and the corrected
Ian Buck frame at 0:43 with name/contribution and the adjacent guide. The download
matches connected Drive metadata: **8,210,651 bytes**, SHA-256
`abc21873df3e33cf7d83516d48a80e215cb93452659b96096e48b16268480a6b`.

- [Complete Drive MP4](https://drive.google.com/file/d/1QNXmC2U5cy64_MJnV-UjF-e_KVZYgdZT/view).
- [Editable native Vids project](https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit).
- Local proof: `projects/cuda-alexnet-vids/artifacts/screenshots/google-vids-people-context.jpg`.
- Current source archive: `projects/cuda-alexnet-vids/artifacts/packages/cuda-alexnet-editable-0.19.0.zip`.

The editable archive retains the exact current runtime, narration reference,
timing/cue evidence, source captions, licensed media and current film. Its
clean extraction is rebuilt and checked with its own bundled people inspector.
The final archive has 4,120 entries (4,119 declared payload files), 130,028,366
bytes and SHA-256 `d6bc5c3bb86f795a07ce6d2612ed50280020dcbcf12b9c8e73c47906d1547105`.
`check_source_bundle.py` passes payload hashes, own-runtime rebuild, source
render audit, six-person observed/audio-cue gate, preview controls and current
portable movie/gallery playback with zero browser errors.
The complete current review has 259 encoded samples, 6,552 source trajectory
poses, zero guide events, zero empty intervals and explicit visual decisions
for all ten scenes. Six 23-pixel contribution-caption advisories are accepted
after full-resolution reading; they are supplementary labels, clear of names,
photos and dividers. A cached repeat reuses all 259 frames and the source audit.
The first source-archive check exposed a legacy 203-second duration assertion
and historical review route after the runtime/people checks had already passed.
The corrected check uses the current review and actual native metadata rather
than a fixed film duration. That earlier check is retained as
`source-first-check.json`; the final archive is rebuilt after qualification.
Earlier archives and the prior film remain preserved. A first aggregate journal
was empty due to a REPL closure binding; durable five-scene chunks and row-count
guards replaced it before final validation. A final export notification was
dismissed before its link was recorded; a fresh observed export supplied the
actual link above. The intermediate synchronization movie is not delivered as
the final visual film.

## Repository gates and limits

Pattern IDs, skill-independence tests, payload check, scoped diff check and
bounded local sync pass. Global skill validation and global sync retain exactly
the four pre-existing unrelated reference-route findings in semantic-model,
ontology and extraction skills. No unrelated files were changed to hide them.
No Pages example/catalog changed and no global plugin activation is claimed.
The primary skill retains its earlier broader generation validation status.
