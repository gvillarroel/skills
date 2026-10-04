# PlantUML style publication verification — 2026-10-04

Status: passed against packaging commit `35f07038c6d30a1b08e820e4f5337d55c882b3fe`, delivered by [successful Pages run 37214189948](https://github.com/gvillarroel/skills/actions/runs/37214189948). The unchanged strict public gate exited 0. All 60 HTTP resources exactly equal their committed Git blobs and current working-tree bytes. The first public audit remains preserved as a failed binding attempt. No public SHA comparison was relaxed.

The first source deployment was commit `014fece01384f5e72bf00ce40f7c0d1d3ed80565`, delivered by [successful Pages run 37213408650](https://github.com/gvillarroel/skills/actions/runs/37213408650). The audited [unified gallery](https://gvillarroel.github.io/skills/examples/plantuml-colorset-renderer/) serves Colorset 2 and Colorset 1 through its theme selector.

The strict publication command required the full source SHA with `--published --expected-ref`, read canonical Git blobs as binary Buffers, and compared exact HTTP response bytes. It checked 60 resources: each palette's 27 SVGs, one Ditaa PNG, coverage metadata, and render report. All 60 returned HTTP 200, but only the two coverage files and two PNGs matched the committed blobs. All 54 SVGs and both reports differed by one terminal LF added by the existing Pages builder. The failed audit exited 1.

The byte diagnosis verified that every public response exactly matched its local `dist/pages/` build artifact. For every failing resource, the first difference was EOF, public/build length was exactly one byte longer, and committed bytes plus one LF equaled the actual public/build bytes. Applying the existing `build-pages.py` text normalization to the committed inputs reproduced all 60 build artifacts. This was a deterministic packaging difference; all published paints and geometry remained correct.

Line endings were assessed separately. Before repair, the 54 working-tree SVGs had CRLF sequences that Git normalized to LF; their normalized content exactly matched the committed blobs. Those local CRLF differences were diagnostics only and were never applied to public response comparisons. The bounded repair normalized only the 54 canonical SVGs and two render reports to LF with exactly one terminal LF. For all 56 files, repaired bytes equal the pre-repair committed blob plus that one LF, preserving every label, paint, geometry value, metadata value, and ID. Repaired canonical bytes now exactly match all 60 previously observed public/build artifacts. Frozen runtime scripts, themes, references, and the isolated Pi candidate were unchanged.

The first live browser audit passed 108/108 paint comparisons against committed native SVGs: both palettes, desktop 1440×1000 and mobile 390×844, all 27 SVG fixtures per combination. Combined local/public checks passed 224/224 uniform-scale, PNG natural/display ratio, and compact-frame checks. Native/mounted local paint parity passed 54/54. There were no style findings, loading failures, broken images, theme mismatches, or overflow. The audit retained nine negative controls, three positive controls, and four measurement controls, all passing, including a real 0.02px inset failure and a hollow-symbol success. Minimum measured contrast ratios were 4.58698 for visible text, 4.43944 for grouped shafts/heads, and 3.10431 for ungrouped connector primitives.

Direct live screenshot review covered Activity CS1 mobile, WBS CS2 desktop, Ditaa CS1 mobile, ArchiMate CS2 desktop, Component CS2 desktop, Sequence CS1 desktop, Packet Diagram CS2 mobile, and Timing CS1 mobile. Complete heads and gutters, initial/final markers, component tabs, cylinder curves, compartments, semantic packet boundaries, and timing contours remained visible. Ditaa retained its slanted request, API cylinder, document silhouette, and complete directional heads. A total of 88 detailed live cards were captured across 22 semantic families, both palettes, and both viewports. The first publication evidence contains 240 screenshots. The packaging-only local audit also exited 0; all 148 local screenshots are byte-identical to the directly reviewed corrected-r4 screenshots.

Both corrected render-report validators passed with 28 rendered outputs and 29 checked fixture results per palette. The frozen coverage validator passed 29 fixtures, 28 published items, 27 canonical families, and the release-extra family. The exact pre/post byte verifier passed all 56 repaired resources. No Pi repeat was needed for this asset-whitespace-only repair.

Ignored evidence is retained under `projects/plantuml-style-repair/artifacts/reviews/` and its sibling `screenshots/` directory:

| Evidence file | SHA-256 |
| --- | --- |
| `published-source-014fece-independent-browser-paint-geometry.json` — preserved failed public audit | `0ffc043ad187e7546b3dcd53338242db6e8801d415c4a545b3e59797782e502d` |
| `published-source-014fece-byte-diagnosis.json` — exact EOF-only cause | `ed8d75d770fe1bedb3a56fb784edba28bd285c8d12658196ae818506c40fe5fb` |
| `canonical-packaging-lf-verification.json` — bounded 56-file repair | `d69cc474107a2e8e49afd854231f6dadc73584d691e5d8de500631db2e099c0a` |
| `published-source-014fece-screenshot-sha256.json` — 240 screenshot hashes | `fe500df99099d6d8f293ff0f001c066f92db6a81e4ac45c4d88a222ad9911fc3` |
| `packaged-lf-independent-browser-paint-geometry.json` — clean post-repair local audit | `9cfdf1306aee4f7cc2481b78cdc7f9f29cbbb96900b3ee3a8c7dcb24568b3a51` |
| `published-corrected-35f070-independent-browser-paint-geometry.json` — accepted exact public gate | `1d162d4e7fa25b3062fd5e185f8721447388ead8a1d0dc4f509529938d51a6e4` |
| `published-corrected-35f070-screenshot-sha256.json` — 154 accepted-run screenshot hashes | `856c4e6cbd6dfe70c68b3cf9d74771f6ab6bdb2e9677812c27cb9ed41a0e999f` |
| `published-source-014fece-to-published-corrected-35f070-public-resource-stability.json` — unchanged public bytes | `dd877b08657d7977172aec33e661543142a09106c00f759879cdadefff88dcb9` |

The accepted command was:

```text
node projects/plantuml-style-repair/scripts/audit_native_gallery.ts --phase published-corrected-35f070 --published --expected-ref 35f07038c6d30a1b08e820e4f5337d55c882b3fe --require-clean
```

This accepted run verified HTTP 200 and exact committed-byte equality for 60/60 resources, 108/108 live SVG paint comparisons in both palettes and both viewports, 224/224 local/public geometry and frame checks, 54/54 local raw/mounted paint comparisons, and all 16 controls. It reports zero style, public binding, paint parity, geometry, loading, overflow, or broken-image failures. Every working-tree resource also equals its committed blob: 60 exact matches and zero remaining CRLF-only exceptions. Contrast minima and semantic geometry remain as recorded above.

All 60 accepted public resource byte sequences equal those observed in the first deployment, and all 154 screenshots generated by the accepted run are byte-identical to their corresponding first-public-phase screenshots. The prior direct live visual review therefore remains applicable to the accepted deployment. The SHA-256 digest of the sorted 60-resource committed binding list is `669c37fb9da12bbc9b408b4daadfc762aee163cf2c21f16dca4049d26da4ce8e`. Per-resource committed/public/local hashes and exact equality flags remain in the accepted report; screenshot files and their hashes are retained in its manifest. A subsequent documentation-only closeout deployment can be verified in fresh ignored evidence without another self-referential documentation commit.
