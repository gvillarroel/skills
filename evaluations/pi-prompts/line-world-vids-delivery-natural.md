Rehearse a complete Line World Google Vids handoff offline and catch an
incomplete delivery. There is no authorized live account in this evaluation.
Use only the copied `skills/line-world-google-vids/` bundle and normal local
tools. Keep that skill read-only. Do not use the network, browser, sibling
skills, repository documents or acceptance galleries. All observations below
are explicitly synthetic test data, not permission to act on a cloud account.

Create `artifacts/01-method.mp4`: a two-second, 320x180, 30 fps fixture with a
predominantly white composition, a solid gray bar, a small primary-red mark and
an audible 440 Hz tone. Use this same fixture as source clip and simulated native
export. Create the story, measured timing and observation files needed by the
bundle without writing anything into the skill. Stable scene ID is `method`;
its actual filename is `01-method.mp4`. Script is `Explain the method.` The scene
and speech last two seconds, and the voice name is `Fixture voice`.

The supplied synthetic native/cloud observations are:

- Saved native project: `https://docs.google.com/videos/d/test-project/edit`.
- Actual scene-button count: 1. Fresh selected-scene announcement: `Scene 1 of 1, duration 2 seconds Alt text title: 01-method.mp4 Has speaker notes 1 objects on the page 1 audio clip starts in the scene Selected`.
- Its visual pixels were inspected and the matching narration was retained.
- Complete export action: `Google Vids File > Export to Drive` for that project.
- Exported Drive MP4: `https://drive.google.com/file/d/test-export/view`, file ID `test-export`, MIME type `video/mp4`. Use the actual generated fixture size and SHA-256 for this simulated export.
- The same Drive file was played, its visible clock was 0:02, and its Download control was enabled. Speech endings, scene joins and explanatory content throughout were reviewed in this synthetic scenario.

Produce `artifacts/ready.json` and `artifacts/ready.md` using the bundle's
delivery workflow. The report must be complete and the handoff must lead with
the stable cloud movie link and include the editable project URL. Repeat the
unchanged check and show that full media verification was reused.

Then make a separate receipt where playback was not observed. Produce
`artifacts/blocked.json` and `artifacts/blocked.md`; these must report the missing
playback and must not call the delivery complete. Treat an incomplete-status
exit as an expected result, without generating a tool error. Retain the ready
receipt. Also show that changing the script invalidates the old observation
revision; write that result to `artifacts/stale.json`.

Exercise the bundle's pure upload recommendation helper without executing any
UI action. Use this synthetic full AX text:

```text
0 document Example Value: https://docs.google.com/videos/d/test-project/edit
10 button Scene 1 of 1
11 text Scene 1 of 1, duration 2 seconds Alt text title: old.mp4 1 objects on the page Selected
12 button Insert
13 menu item Upload u
```

The target is scene 1, file `C:/fixture/01-method.mp4`, in the same project.
Record the helper's next recommendation for each independent observation in
`artifacts/ui-next.json`, using keys `diffOnly`, `background`, `delayedDialog`,
`nativeDialog`, and `inserted`. Respect these facts respectively: the text is
only a diff; the tab is in the background; Upload was clicked but no dialog or
media is visible yet; a native Open dialog was freshly observed; the selected
scene announcement now names `01-method.mp4` after submission. There is no live
dialog and these recommendations must remain data, not actions.

Finally write `artifacts/checks.json` with `ok`, `mediaCheckReused`,
`blockedForPlayback`, `staleRevisionRejected`, `syntheticOnly`, and the actual
fixture byte size. All five booleans should be true only when verified.
Keep all exact required output paths and summarize the outcome without claiming
a real cloud upload or playback.
