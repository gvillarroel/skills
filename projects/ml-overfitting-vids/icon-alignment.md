# Container alignment revision

November 15, 2026, plugin 0.18.0. The preprocessing and deployment objects now
center their loaded internal labels horizontally and vertically. Quantitative
chart geometry and deliberately aligned values retain their coordinates.

Four affected scenes and continuity dependencies were replaced in the existing
[Google Vids project](https://docs.google.com/videos/d/12pQ3UaqihBOtZe_w6VaigVhjQzzgnU4qCnCKa0VmLCs/edit).
The complete [Drive MP4](https://drive.google.com/file/d/1DJ1LxRu8YPwYTHiW5PFLYnt4mWODnSzq/view)
was played and downloaded: 9,417,427 bytes, 1920x1080, 7,977 frames and
265.914921 seconds. All frames decode with no blank/black frames. The original
voice PCM is byte-identical. Source inspection covers 116 cue/reading poses;
the existing guide audit checks all source frames and 80 cue arrivals.

Evidence: `artifacts/revision/items.json`, `native-verification.json` and
`google-vids-icon-centering.jpg`. The prior native movie and changed clips remain
under `artifacts/videos/before-icon-alignment/`.
