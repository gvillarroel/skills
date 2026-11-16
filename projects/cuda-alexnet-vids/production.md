Current visual review (0.26.0): [cuda-alexnet-polished.mp4](artifacts/videos/cuda-alexnet-polished.mp4). See the [collection review](../line-world-quality-review/review.md) for exact delivery identity and current validation. This is a local visual revision with the approved Google Vids AAC voice preserved; earlier native export records below remain historical evidence.

# CUDA and AlexNet: native Google Vids production

This project uses the six-skill Line World Video 0.14.2 plugin. The Spanish
script is requested source material; production notes and scripts are English.
The native project is separate from the approved ML overfitting film:
https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit

Use white surfaces, primary-red #9e1b32 focus, a dark-gray secondary comparison,
full-frame partitions and one persistent world. Visible titles are disabled.
Keep the same native Nyla voice. Derive final scene lengths and focus arrivals
from actual native speech; draft clipSeconds are estimates, not measurements.

## Historical evidence

- [NVIDIA corporate timeline](https://www.nvidia.com/en-us/about-nvidia/corporate-timeline/)
  identifies the CUDA unveiling in 2006.
- [Original CUDA beta announcement](https://forums.developer.nvidia.com/t/release-notes-and-readme-please-read-after-installing-cuda/213)
  is dated February 15, 2007. Distinguish announcement from public tools.
- [CUDA architecture overview](https://developer.download.nvidia.com/compute/cuda/docs/CUDA_Architecture_Overview.pdf)
  explains general-purpose GPU computing and CPU/GPU responsibilities.
- [ImageNet 2009 research](https://www.image-net.org/static_files/papers/ImageNet_VSS2009.pdf)
  and [dataset history](https://www.image-net.org/about.php) establish the data
  project and its large-scale labeled collection.
- [Original AlexNet paper](https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf)
  supports authorship, architecture, training resources and test results.

The official 2012 challenge results page timed out during research. Use the
original paper's Table 2, not an unverified reconstructed leaderboard.
Its 15.3% top-5 test error belongs to the seven-network competition ensemble;
it is not a single-network result. The runner-up is 26.2%, a 10.9 percentage
point gap. The approximately 1.2M training images / 1000 classes describe the
challenge subset, not all ImageNet. Five convolutional plus three fully
connected layers count weighted layers, omitting intermediate operations.
Two GTX 580 3GB GPUs and five-to-six days describe training a model, not the
whole ensemble's total resource cost. CPU/GPU work and image marks are
schematic; the film invents no measured speedup or classified image examples.

## Completed delivery

The separate ten-scene native project uses the exact verified Spanish scripts
and native Nyla narration. All-scene voice generation was executed through the
actual supported interface. Prepared videos were inserted individually into
their verified matching scenes, preserving ten voice tracks and one video
object per scene. Private sharing remains unchanged.

The original Google Vids MP4 is `artifacts/videos/cuda-alexnet-google-vids-final.mp4`:
1920 by 1080, nominal 30 fps, 6099 frames, 203.313923 seconds, H.264/AAC,
with Google encoder metadata. The native export includes an optional subtitle
track marked default. `artifacts/videos/cuda-alexnet-final.mp4` is the clean
delivery: a stream copy retaining the exact video/audio payloads and decoded
voice while omitting that subtitle track. It adds no new encoding generation.

Actual native scene announcements have millisecond resolution; source clips
use exact 30 fps coverage. The adapter compiles 6098 source frames while the
native muxed export contains 6099 frames. Its 47 ms total-duration difference
passes the timing gate and has no blank tail. All 6099 frames fully decode;
no white or black frame is detected. All 53 encoded cue arrivals have the red
guide beside their expected ports. Ten independently matched original-voice
windows have correlation at least 0.9933. ASR word boundaries remain approximate.

Visual audits cover static reading geometry, text/text and stroke/text bounds,
focus envelopes, exact source camera/guide joins and repeated seeking. A manual
review repaired native Mermaid word wrapping and a schematic checkmark before
final upload. Native connector strokes are included when reserving adjacent
focus ports. Dividers span their complete parent frame sections.

The extension's direct uploader required broader file-URL access. Uploads used
the normal Windows Open dialog instead. Keep script-body focus distinct from
canvas focus: edit the visible script glyphs and verify the committed text.
Temporary canvas text was removed before all ten final video insertions.
The voice reference in `artifacts/sources/` contains the approved speech before
visual insertion; final movies are under `artifacts/videos/`.

## Rebuild and edit

The editable ZIP includes the exact six-skill plugin under `resources/plugin/`,
local D3/GSAP/fonts, original Mermaid sources/SVG, scene code, theme, measured
word cues, clips, both final movies, evidence and a silent interactive preview. It requires no
other repository to rebuild. Existing local Chromium and FFmpeg are needed for
browser rendering. ASR is optional when retaining the supplied measured cues;
`transcribe_native.py` accepts a caller-supplied existing Whisper model folder.

```powershell
uv run --script scripts/prepare_project.py
uv run --script resources/plugin/skills/line-world-video/scripts/video_edit.py inspect --project . --file cues --path "scenes[id=imagenet-result].cues[target=winner]"
uv run --script resources/plugin/skills/line-world-video/scripts/video_edit.py plan --project . --patch changes.json
uv run --script resources/plugin/skills/line-world-video/scripts/video_edit.py apply --project . --patch changes.json
uv run --script scripts/prepare_project.py
uv run --script scripts/render_video.py --render --scene imagenet-result
```

Keep visual styles in `theme.json`. Keep local cue arrival/travel in
`artifacts/data/cues.json`; changing narration requires new actual audio and
realignment. `align_production.py` uses retained word evidence plus reviewed ASR
spelling alternatives. It never invents unmatched timestamps. The guide is
primary red, contracts in travel and grows briefly at each arrival.

Serve `artifacts/composition/` locally and open `preview.html` to select scenes,
scrub or play; those controls are outside the rendered film. The local render
cache validates declared files and actual camera/guide endpoints. Native Vids
uploads still require current UI observations and renewed final export.

## Reproducible validation

The extracted bundle can rebuild the local composition, audit its geometry,
verify the retained native movie and prepare new upload media. Native upload
confirmations are observations of this completed project; editing a scene or
voice requires new observations and a fresh native export. The finalization
command below belongs to the original production workspace after its native
batch has been prepared and its scene/media evidence has been reviewed.

```powershell
uv run --script scripts/render_video.py
uv run --script scripts/prepare_uploads.py
uv run --script scripts/verify_export.py --video artifacts/videos/cuda-alexnet-google-vids-final.mp4
uv run --script scripts/finalize_delivery.py
uv run --script scripts/package_project.py
uv run --script scripts/check_source_bundle.py
```

The ten initial clip preparations copied existing correct media with zero
re-encodes; the final preparation reused all ten. The local scene cache also
reuses all ten unchanged outputs. Actual UI confirmations leave zero pending
native actions. Queue receipts, timing, source/native reviews and delivery
stream hashes are under `artifacts/manifests/` and `artifacts/reviews/`.

## Contributor portraits and circular logo revision

Six inspected documentary portraits now appear in their relevant stages:
Ian Buck with CUDA, Fei-Fei Li and Jia Deng with ImageNet, and Alex Krizhevsky,
Ilya Sutskever and Geoffrey Hinton with AlexNet. The verified NVIDIA mark uses
a separate circular support with complete vector artwork. The original film
and baseline evidence remain under `artifacts/baseline-no-portraits/`.

The three author names have separate measured guide destinations, raising the
cue count from 51 to 53 without changing a spoken word or a scene duration.
Six changed clips were copied into the upload batch without re-encoding; four
were reused. All six native Replace video operations preserved the existing
video object placement, original voice and measured scene extent. Fresh native
selections verified all ten media identifiers and one video/voice per scene.

The downloaded portrait revision has SHA-256
`ee2217a91ca060e752ba3eac5b8ce3a6777f9cbe3c1604a0f9549c4b6de5567c`;
the clean stream-copy delivery has SHA-256
`0c7123409cf517d5115aa3859b5275ea726a874dac5d102ab271eb8198d9d7b4`.
All seven actual encoded media crops match the reviewed source render with
pixel correlation above 0.991. Transparent corners pass for all seven PNGs.
The offline D3 graph loads seven image nodes and four relationships and passes
an actual drag interaction without browser errors.

Read [the media minutes](logos-and-portraits.md) for logo acquisition, SVG/PNG
selection, graph embedding and the actual photo rights. The media pack includes
originals, credits, circular files, `graph-nodes.json` and `graph-preview.html`.
`scripts/prepare_media.py` builds the reviewed media request; repeated builds
reuse all seven local assets. `scripts/build_media_handoff.py` adds the graph
preview and creates `artifacts/packages/cuda-alexnet-media.zip`.
`scripts/verify_media.py --video artifacts/videos/cuda-alexnet-google-vids-final.mp4`
verifies the graph, transparency and actual encoded portrait/logo pixels.

## Whole-film visual revision, archived 0.11.0

The 0.11.0 delivery superseded the portrait-only revision above. Its baseline
movie and source snapshots remain in `artifacts/baseline-visual-review/`.
The initial broader review found 28 grouped guide/figure/text collision findings
and four spacing/type advisories. These findings covered travel and camera
movement that the earlier arrival-only checks did not inspect.

The current film uses all meaningful figures, images and labels as obstacles,
combines neighboring scenes in world coordinates during camera travel, and
keeps the guide on that clear route inside the moving viewport. Related Mermaid
lanes now share one text scale. Portrait headroom, convolution/divider clearance,
the schematic qualifier, secondary-gray value emphasis and the opening network
icon are corrected. Neutral image thumbnails reserve red for explained targets.

All ten source clips were rendered and replaced through native Replace video
without regenerating speech. Fresh selections verified the ten scene IDs,
durations, single video objects and original Nyla tracks. The actual downloaded
native SHA-256 is
`8f23dceeabe76abd18e75d532484758faff75a27fccc9f5492d83c756e10a054`.
The clean stream-copy delivery SHA-256 is
`45c15f6e0e8626eada8462515a601553fd0b138ef49191ede55b0e9f74794c0e`.
Both retain 6099 frames and 203.313923 seconds. All 53 encoded guide arrivals
pass; ten voice-reference windows have correlation at least 0.9933177.
All seven media crops pass, with correlation at least 0.98808. Crop locations
now come from the actual browser geometry rather than handwritten coordinates.

Read [the complete visual review](visual-review.md) for inspection scope,
before/after results, exact review commands and the current source-bound
operator notes. The repeated review reused all 248 extracted samples and the
source scan, with zero new captures. This is a source/encoded visual audit and
retained-audio verification, not a new human listening claim.

## Current content and color revision, 0.12.4

Read [continuous content and vivid emphasis](content-and-color.md) for the
current release. Fresh native inspection found and removed an extra five-second
scene with zero objects and no audio. The project now has the expected ten
scenes, with original speech and extents preserved. The stronger shared theme
uses primary-red edges on white faces and explicit solid-red options, while retaining nonwhite data fills,
dark-gray secondary comparisons, portraits and logo pixels. Native inventory,
all-frame encoded content and source-anchor guards complement the prior visual
audits. Current review artifacts are under `artifacts/reviews/content-after/`.
