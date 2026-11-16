Create the illustrative full-frame atlas in `boundary-film`. Verify that its
builder rejects four independent invalid stories: an overlap cancelling an
equal-area gap, a tiny uncovered gap, a panel outside the frame, and a scene
duration that does not leave the required reading time. Start each case from
the same valid original story and call both validate and build with captured
subprocess results, so an expected rejection does not become a tool error.

Prove the compiled timing manifest remains unchanged after each rejection.
Restore and rebuild the valid original project at the end. Write
`boundary-report.json` with `cases` (each containing `name`, `rejected` and
`timingManifestUnchanged`), `validStoryRestored`, and boolean `pass`. Keep skill
resources read-only. No video or browser audit is required for this test.
