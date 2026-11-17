# Everyday life through 1960s archive clips

This is the user's requested Spanish-language archival video, created with the
Destockd search skill and the Line World visual and timing workflow. The final
delivery is a local 1920 × 1080, 30 fps MP4, 124.50 seconds long. Narration
uses Microsoft Edge speech (`es-CL-CatalinaNeural`, rate `-4%`), with actual word
boundaries and decoded audio durations. This project does not claim a native
Google Vids export or a native HyperFrames render.

The film discusses selected aspects of public life, clothing, communication,
cinema and unequal access to shared spaces. It is a small, situated historical
commentary, primarily about the United States with a European fashion report.
It is not a representative survey of every household, class or country in the
1960s. Spanish narration and entity labels are required source material for the
requested output; project instructions and verification records are in English.

## Historical identity and dates

| Material | Date evidence | Scope |
| --- | --- | --- |
| Hampton street and parade | [NASA's history of the March 17, 1962 celebration](https://www.nasa.gov/centers-and-facilities/langley/nasalangley100-making-space/) corroborates the event named in [the NASA/NARA film](https://archive.org/details/255-fr-1638). | Actual parade streets, cars, shops and spectators; not ordinary commuting footage. The item itself does not supply a date field. |
| Rome fashion report | [Universal Newsreel, volume 37, release 86](https://archive.org/details/un-un-v37-r86-s4), released October 26, 1964. | A staged report on autumn fashions, including an aircraft, daytime and evening clothing. Release date is not an asserted shooting date. |
| Hollywood and the Academy Awards | [Universal Newsreel, volume 38, release 29](https://archive.org/details/un-un-v38-r29), released April 8, 1965. | The 37th Academy Awards, its exterior and its actual auditorium; not an ordinary cinema audience. |
| Chicago offices, phones and television | [1968 Democratic National Convention, Chicago](https://archive.org/details/306-1424-r1_HD_2Mbps). | Campaign/convention workspaces, not a private household. The year is in the archival title; no exact shooting date is asserted. |
| Somerville protest | [Civil Rights Demonstration at Sommerville, Tennessee](https://archive.org/details/60-cr-8), produced 1963; the description places the incident/protest on July 22, 1963. | Actual documented civil-rights protest. Preserve the source title's spelling; use the place name Somerville in narration. |

Search results were not treated as date evidence. Earlier material returned by
the semantic search, such as *The President Accounts* (1939), was excluded.
The unknown-date kitchen reel and a 1965 sports celebration were also excluded
from household/nightlife claims. No supermarket, domestic family or household
television survey was inferred from visually similar footage.

Destockd provides shot-level downloads and links to FedFlix/NARA source records.
The [National Archives' account of the Universal Newsreel collection](https://www.archives.gov/publications/prologue/2013/summer/fads-and-fashions-in-universal-newsreels)
documents that collection's public-domain donation. Keep each shot's actual
receipt and provider rights notice; this is provenance, not a blanket assertion
about every element in every film. Original archive audio is excluded from this
commentary. The voice track is newly generated Spanish narration.

## Source and rendering contract

- `story-source.json` is the editable narrative, layout, phrase and timing input.
- `scripts/acquire_clips.py` selects exact saved film/shot identities. It invokes
  the search skill's real downloader, retains immutable receipts and validates
  existing download hashes. Sixteen candidates were acquired; the scene plan
  chooses which of them actually appear.
- `scripts/prepare_story.py` measures decoded speech and actual word boundaries,
  resolves phrase-triggered cuts, preserves end pauses and writes `story.json`,
  `artifacts/manifests/timing.json` and the combined voice WAV. It caches voices
  by text/provider/voice/rate and actual file digest. It excludes only redundant
  trailing TTS padding after both the last actual word boundary and audible PCM,
  retaining a 220 ms margin; immutable downloaded speech stays intact. This
  prevents the voice's own end silence from duplicating the editing pause.
- Original clips retain their native speed. Prepared panels use conservative
  source-matte crops, aspect-preserving fit, ordinary frame-rate conversion and
  declared end-frame holds for annotation. They do not loop, reverse, synthesize
  or interpolate archive action. Originals and source hashes remain intact.
- `composition/scene.js` uses the copied Line World `focus.js` runtime. Actual
  word cues drive adjacent guide ports. Pure shared-clock SVG states own the
  guide, contextual relations and motion during long reading holds. The authored
  palette uses primary red `#9e1b32`, grays and white; original media color is
  retained separately. There are no added headline or subtitle bands.
  Sections use spacing and alignment, without a decorative central divider.
  The shared `gentle-motion.js` clock floats each complete concept group with
  its labels and connectors. The guide follows the displayed target; route
  obstacles include the full motion envelope.
- `scripts/render_movie.py` composes native video pixels with FFmpeg and overlays
  the same time-indexed SVG through Playwright/resvg. It uses source/output
  digests to reuse prepared panels and finished scenes. Scene changes use one
  1.25-second lateral pan with a guide-free outgoing plate and an independent,
  continuously visible guide. No repeated zoom in/out is used.
  The held television frame has one slow 10% detail cycle: four seconds in,
  three held and four out, anchored to the actual television speech cue. The
  original image returns inside a fixed viewport; its caption and guide stay
  outside the camera. Native FFmpeg and browser preview derive this cycle
  from the same parameters. Overlay frames are requested in batches of 30
  to reduce browser round trips, while still rendering every unique time.
- The local preview server supports HTTP byte ranges. Metadata loading alone
  did not guarantee correct seeking with the initial basic server. The exact
  preview seek now waits for the requested media time and fails on a mismatch.
- The final audio/video assembly uses the plugin's `project_delivery.py`, with
  measured PCM durations and exact per-scene frame budgets.
- Scene color normalization decodes the original render to RGB before BT.709
  conversion. Retagging or a negotiated YUV-only conversion changed the apparent
  red/gray values. The final actual decoded primary red, gray and white samples
  must stay within six channel levels of their authored colors, allowing normal
  H.264 quantization. Range flags and all scene parameters are checked too.
- Outgoing plates select the exact decoded last frame by frame index. Fast
  timestamp seeking rounded past the final sample of one concatenated panel;
  the indexed selection avoids that failure without substituting another shot.

## Editable times

Change `timing.leadSeconds`, `timing.tailSeconds`, `timing.panSeconds`, the voice
rate, or a scene's `primary` source choices in `story-source.json`. Keep the lead
long enough for the arrival pan and guide travel, and retain at least the current
tail when inspecting the final spoken word. Cuts with `untilPhrase` follow the
actual regenerated word boundaries. `offset` is a source-local trim time in
seconds. Do not rewrite timestamps in `composition/scene.js` or speed up speech
to fit a template. Rebuild and inspect affected scene joins after every change.

Edit `motion.float` to change the group displacement and cycle. Current
1080p defaults are 2.5 horizontal units, 6 vertical units, an 11-second cycle
and 1.2-second settling. Edit `motion.detail` for the television's reviewed
normalized focus rectangle, zoom and entry/hold/return durations. Reserve the
whole cycle inside its reading hold. Do not compress it to fit a short scene
or float individual quantities. Run the source and encoded checks again.

```powershell
uv run --script projects/sixties-archival-video/scripts/acquire_clips.py
uv run --script projects/sixties-archival-video/scripts/prepare_story.py
uv run --script projects/sixties-archival-video/scripts/render_movie.py --panels-only
uv run --script projects/sixties-archival-video/scripts/render_movie.py --audit-only
uv run --script projects/sixties-archival-video/scripts/render_movie.py
uv run --script skills/line-world-video/scripts/review_video.py --video projects/sixties-archival-video/artifacts/videos/sixties-lifestyle.mp4 --story projects/sixties-archival-video/artifacts/data/review-story.json --output projects/sixties-archival-video/artifacts/reviews/encoded
uv run --script projects/sixties-archival-video/scripts/build_delivery.py
uv run --script projects/sixties-archival-video/scripts/verify_motion.py
uv run --script projects/sixties-archival-video/scripts/check_playback.py
```

The source audit covers all 3,735 authored guide states, 24 measured spoken cues,
actual SVG reading geometry and repeat seeking. Encoded content, final stream
checks, media playback and operator visual observations are recorded separately
under project artifacts. Passing geometry does not by itself certify speech
quality, historical interpretation or the selected source crops.

Final stream evidence records 14 used source clips, 3,735 decoded frames,
124.50 seconds, 1080p/30 fps and AAC narration. Audio analysis finds no silence
interval of at least 3.5 seconds and keeps the peak below clipping. Fresh Chrome
checks actual playback in all six scenes, six exact source-preview seeks and
HTTP 206 byte-range delivery with zero page errors. The encoded reviewer finds
no insufficient-content frames. Operator observations are frozen in
`observations.json` against the actual final movie hash and must not be reused
to approve a changed movie.

Revision 2 uses Line World plugin 0.27.0 and its shared motion utilities.
Approved AAC payload bytes match revision 1 exactly; the camera has separate
structural parity checks against the actual prepared source image. The mean
channel difference stays near one level at entry, hold and return. All five
concept groups change position while retaining their labels and connections.
The plugin's strict standalone contract and naturalistic forward cases pass
on the documented Sol-medium model exception. See the canonical
[release evidence](../../evaluations/line-world-video/gentle-motion-20261117.md).

Repository pattern IDs, skill independence and payload checks pass. Unrelated
root skill-authoring findings remain outside this release. Publish only the
scoped Line World changes from a clean worktree and require its complete
repository checks to pass. Private Drive delivery receipts and movie bytes
stay in ignored artifacts; no cloud identifier is published with source.
