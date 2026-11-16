# Native Google Vids workflow

## Contents

- [Native scene workflow](#native-scene-workflow)
- [One-step upload recommendations](#one-step-upload-recommendations)
- [Public references](#public-references)

## Native scene workflow

Verified against the English Vids interface on November 15, 2026. Labels and
feature availability can change; derive targets from current observations.

For fewer repeated reads, use the pure compact-state parser and content-based
pending queue described in the batch workflow. Inspect native All scenes voice
generation when every scene needs a new voice; use individual updates for partial
revisions because bulk generation can replace completed generated tracks.

1. Inventory the available browser/app surfaces. Select the authorized account.
   Open Google Vids through the observed official entry point. A Chrome profile
   picker may need its window raised before coordinates are available.
2. Create a landscape Blank vid for a 16:9 story, or open the requested project.
   Set the file name through Rename and verify Saved to Drive. A file name is
   not an in-film visible title. Do not change sharing permissions by default.
3. Use New scene or the observed equivalent for the planned scene count.
   Observe the selected scene and total count after each batch of deterministic
   actions. Avoid shortcuts while the wrong text field has focus.
4. The Voiceover sidebar exposes Current scene and All scenes, Edit script,
   Change the voice, Preview and Insert voiceover/Update voiceover. Some script
   bodies expose a group rather than an editable accessibility field. Click
   the visible script area, paste plain text and exit editing, then verify the
   script and enabled insertion control in the next observation.
5. In the observed interface, Insert voiceover generates and inserts narration;
   the button changes to Update voiceover after success and the scene expands
   to contain the speech. Keep these postconditions in the journal. Native
   language selection can follow the script's dominant supported language.
   Verify Spanish rather than relying on older English-only help pages.
6. Upload clips through the actual Uploads/Drive and Photos or Insert controls.
   The observed Insert menu has a distinct Upload action for local files;
   the Uploads rail opens a Drive & Photos picker. Prefer the local action for
   project-owned MP4 files. In a native file dialog, keyboard focus of File name
   can avoid an owned-dialog coordinate mismatch; verify the dialog first and
   paste the exact authorized path.
   In a Windows Open dialog, use a resolved Windows path with backslashes.
   Forward-slash paths can produce "The file name is not valid." Verify that
   the picker closes and the media replacement changes the document before
   proceeding. A helper returning from Return is not an upload receipt; stop
   and inspect an error or a picker that remains open. Do not queue replacements
   behind an unresolved native dialog. Respect a browser upload permission
   rejection and report its requested setting; do not change extension access.
   Match stable IDs/file names. Add the clip to the intended existing scene;
   a drop into a timeline gap may create a different scene. Recheck the scene
   count, current media, start offset, duration and playback speed.
   For a visual-only revision, select the existing video and inspect the native
   Replace video control. Its Upload action can replace that object while
   preserving its placement, scene and original voice track. Verify the selected
   scene and replacement pixels, not only a reused filename; then reselect the
   scene to check one video object, its exact duration and its retained narration.
   Prefer this observed path when available over removing/reinserting objects.
   Use Zoom to fit timeline before selecting a distant scene. Go to beginning
   moves the playhead but can leave a different scene selected for insertion.
   Explicitly select the intended scene card and verify its selected state/URL
   and inserted media; never infer insertion destination from playhead alone.
7. If an imported clip extends the scene beyond narration, trim its reading
   hold or set the observed scene duration. Preserve speech endings and the
   essential animation. Use the same voice and restrained transitions.
8. Preview the complete story, then use the observed File export/download
   action. Wait for export readiness, download the complete MP4, and verify
   that the actual file contains video and audio with the intended duration.

Use the current computer-use tool's documented API. Native Windows clicks may
return before the next render/AX update; inspect the resulting screenshot or
fresh state before assuming an insertion failed. Never double-insert a voice
or scene just because the first returned tree was stale. Refresh a changed
window selection after Chrome opens a profile. Never replay saved element
indices or screenshot coordinates from another project.

For each current scene, click Edit script first, then an actual visible text
glyph inside Scripts before selecting all and pasting. The form's bounding box
includes empty space: a form-center click or double-click can still leave the
canvas selected. When necessary, inspect the current screenshot and click a
visible script word. Verify that Select all highlights the script, then paste
and observe the result before Escape. A successful paste changes the Scripts
text and reports a text paste; "Pasted text in a new text box" is a failed edit.
Undo that own paste immediately and correct the focus before continuing.
Confirm the native
"Voiceover outdated" state and the committed script before Update voiceover;
accept its observed Replace existing voiceover dialog when revising that voice.
After generation, freshly select the scene and verify one intended visual object
and one audio start. If an own paste created an unintended text object, undo that
paste before continuing. Never mistake a new canvas text box for a script edit.
Use the current tool's documented key syntax; native-app and browser wrappers
can accept different Control-key spellings. The timeline accessibility summary truncates seconds;
use its precise child timer text, scene/audio properties or visible timer.
Record the measurement resolution and recheck final export drift.

## One-step upload recommendations

Load the small pure `assets/runtime/vids-ui.js` definition into the documented
CUA runtime once. It performs no UI, file or network operations. After a fresh
full AX observation, pass only that state and the pending upload target:

```javascript
const raw = await app.getAXState({emit:false,disableDiffing:true});
nodeRepl.write(LineWorldVidsUI.uploadNext({
  ax: raw, fullState: true, foreground: true, phase: 'select',
  target: {projectUrl: observedProjectUrl, sceneOrder: pendingOrder, file: exactClipPath}
}));
```

Use the API supported by the selected app/tab; `disableDiffing` is specific to
the current tool. Obtain its documentation first. Never assert `fullState` or
`foreground` without observing them. The helper returns one recommendation:

| Result | Next action |
| --- | --- |
| `read-full-state` | Obtain a full current tree; a diff can omit the controls you need |
| `verify-project` | Observe the intended official Vids URL before acting |
| `foreground-tab` | Show/raise the intended browser tab, then verify it again |
| `select-scene` | Use the freshly returned index once; read state again |
| `open-upload` | Inspect current Insert/Replace video > Upload controls |
| `fill-native-filename` | In the observed native Open dialog, focus File name with `Alt_L+n`, paste the exact path, press Return |
| `observe-upload-result` | Wait for another UI observation or inspect a screenshot; do not repeat Upload yet |
| `verify-inserted-scene` | Inspect current pixels, one video, retained voice and exact duration; only then confirm the queued task |
| `stop` | Follow the host's policy handoff; do not switch transport to retry |

After clicking Upload, use phase `await-dialog`; set
`nativeOpenDialogObserved: true` only after freshly observing that dialog.
After submitting a filename, use `await-insertion`. The helper identifies the
media of the selected scene, rather than a filename elsewhere in the timeline.
It returns recommendations, never confirms an upload automatically.

When a browser tab runs in the background, its AX controls can work while a
native file picker remains hidden. Foreground the correct tab before opening
Upload. If a native tab AX click reports missing coordinate geometry, inspect
the current screenshot and use the documented visible control; do not reuse
saved coordinates. The first returned tree after a click may still show the
old tab. Verify the next state before continuing.

An owned Open dialog may expose filename indices that cannot be acted on from
the cached app state. The observed keyboard filename path avoids those indices.
If browser file-chooser automation reports missing file-URL access, use this
normal visible dialog route when allowed; do not change extension permissions.
Respect any host policy stop before considering another route.

## Public references
- [Vids getting started](https://support.google.com/docs/answer/15082958?hl=en)
- [AI voiceovers](https://support.google.com/docs/answer/15070345?hl=en)
- [Spanish voiceover rollout](https://workspaceupdates.googleblog.com/2026/02/vids-avatars-voiceovers-new-languages.html)
- [Voice model and language update](https://workspaceupdates.googleblog.com/2026/04/new-more-expressive-ai-voiceovers-in-Google-Vids-and-16-additional-languages-powered-by-Gemini-3.1-Flash-TTS.html)
