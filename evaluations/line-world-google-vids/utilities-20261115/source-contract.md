Use only the loaded line-world-google-vids skill and keep it read-only. This is
an offline source-preservation check. Do not browse or access any live account.
Start by creating input/, output/ and film/media/ with Python Path.mkdir using
parents=True and exist_ok=True; the workspace does not provide those folders.
Do not require nonexistent task directories to pass an initial shell listing.
Generate a two-second 320x180, 30 fps H.264 static white/red source directly at
film/media/inspect.mp4. Create input/story.json for one scene inspect, with that
absolute sourceClip path, script "Inspect the evidence.", voice Nyla, clipSeconds
2, essentialAnimationSeconds 0.5, staticHoldAfterSeconds 0.5, and target 320x180,
30 fps. Create film/ using the batch helper, preserving its existing input file.
Use synthetic observed speech 0.85 seconds and scene extent 0.91 seconds.
Prepare the upload and repeat unchanged. Write output/check.json with
sourceUnchanged=true only if the original byte digest is preserved,
uploadSeparated=true only if the prepared upload path differs from its source,
and warmEncodedClips from the actual second build. Keep the prepared clip,
film/handoff/timing.json and film/.vids/state.json. Do not count local preparation
as completed native UI work.
