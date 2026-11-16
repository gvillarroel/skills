Create the illustrative full-frame atlas in `boundary-film`. Starting each
case from the same valid original, prove the builder rejects these independent
invalid stories: (1) overlap cancelling an equal-area gap, (2) tiny uncovered
gap, (3) panel outside the frame, (4) insufficient reading time, (5) guideColor
set to accent #e8002a, (6) travelRadius greater than baseRadius, (7) a semantic
category color map while palette is colorset1, (8) unitPerPoint=0.01 producing
more than 64 quantity points per entity.

Call both validate and build with captured subprocess results so expected
rejections do not become tool errors. Prove timing.json is unchanged after
each rejection. Restore and rebuild the valid original. Write
`boundary-report.json` with `cases` (each containing `name`, `rejected` and
`timingManifestUnchanged`), `validStoryRestored`, and boolean `pass`.
Keep resources read-only. No video or browser audit is required.
