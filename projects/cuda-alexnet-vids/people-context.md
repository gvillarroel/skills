# Spoken and visible contributor context

Release 0.19.0, November 15, 2026 local production date. The original portrait
selection and attribution are retained. Each shown person now has a full name,
a concise contribution caption, a spoken name/contribution and a name-linked
guide cue. Scene-local timing comes from actual new Google Vids narration.

| Person | Relevant contribution in this film | Reviewed source |
| --- | --- | --- |
| Ian Buck | Brook with the Stanford team; subsequent NVIDIA CUDA software work and leadership | [NVIDIA history](https://developer.nvidia.com/blog/inside-the-programming-evolution-of-gpu-computing/), [NVIDIA CUDA software-group announcement](https://forums.developer.nvidia.com/t/cuda-expert-day-at-supercomputing08/6324) |
| Fei-Fei Li | Initiated and drove ImageNet, with a larger team | [Stanford HAI](https://hai.stanford.edu/people/fei-fei-li) |
| Jia Deng | First author of the 2009 ImageNet paper | [Original paper](https://www.image-net.org/static_files/papers/imagenet_cvpr09.pdf), [Princeton history](https://www.cs.princeton.edu/news/hallways-princeton-fascination-human-mind-unlocked-power-deep-learning) |
| Alex Krizhevsky, Ilya Sutskever, Geoffrey Hinton | Coauthors of AlexNet at the University of Toronto | [Original 2012 paper](https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf) |

The film does not assign unsupported separate responsibilities to the three
coauthors or imply sole authorship for ImageNet/CUDA. Current executive titles
are not substituted for the historical contribution.

Only three scripts and native Nyla voices changed: cuda-platform, imagenet-scale
and alexnet-model. Five visual clips were replaced, including adjacent continuity
dependencies parallel-work and two-gpus. New native frame-aligned budgets are
25.2333, 26.9333 and 28.6667 seconds for the three changed speaking scenes. The
complete authored budget is 218.4 seconds. Native scene announcements total
218.396 seconds and confirm ten scenes with one video and one audio start each.
The actual downloaded export is 218.453333 seconds and 6,553 frames. Complete
decode and all 56 encoded guide arrivals pass; all ten current voice-reference
windows correlate above 0.9909. This verifies the three revised voices and the
seven retained voices against the actual intermediate narration export.
The current portable review is `artifacts/reviews/people-context-review/`: 259
encoded samples, 6,552 source trajectory poses and explicit per-scene visual
decisions. Its six supplementary 23-pixel caption advisories are accepted after
full-resolution inspection; no overlap, guide or content failure remains.

Actual ASR supplies all six name times. Approximate recognized spellings such as
"Ian Bock" and "Faye Faye Lee" are retained as alignment alternatives; the
committed native scripts and visible names keep the correct spelling. An ASR
spelling variant is not treated as a different person or an exact pronunciation
certificate. The source passes caption bounds, label separation and guide-port
checks. All 56 cues include separate person targets, with the guide beside the
complete portrait/name/role block.

Current [Google Vids project](https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit)
and complete [Drive MP4](https://drive.google.com/file/d/1QNXmC2U5cy64_MJnV-UjF-e_KVZYgdZT/view).
Drive playback and download were observed. The final download is 8,210,651 bytes,
SHA-256 `abc21873df3e33cf7d83516d48a80e215cb93452659b96096e48b16268480a6b`.
The cloud proof is `artifacts/screenshots/google-vids-people-context.jpg`.

Evidence lives in `artifacts/revisions/people-context-0190/`, including the
original production backup, actual voice-reference export, word-derived context,
two final inventory chunks, combined checked inventory and cloud observations.
The new voice reference is intermediate synchronization material; it is not the
final visual movie. Final local review lives under `artifacts/reviews/`.

Verify the revised voices against their own native reference:

```text
uv run --script scripts/verify_export.py --video artifacts/videos/cuda-alexnet-google-vids-final.mp4 --voice-reference artifacts/revisions/people-context-0190/native-voice-reference.mp4 --reference-timing artifacts/revisions/people-context-0190/voice-observed.json
```
