# Reddit walkthrough

This project demonstrates public Reddit navigation and participation controls
using original signed-out browser screenshots. The current captures use
Reddit's native **Display Mode > Light** setting. Earlier dark captures remain
only in ignored local revision evidence and are not used by the current story.
No UI pixels are inverted or recolored.

The Spanish narration explains search, choosing and following a community,
rules, reading a thread, voting, replying, commenting, account requirements
and creating a post. The capture session performed read-only navigation and
opened account dialogs; it did not submit participation or credentials.

## Reproduce or revise locally

The source captures are under `artifacts/screenshots/light/` and the original
narration and provider word boundaries under `artifacts/audio/`. These local
media files are excluded from Git. Capture new real UI states when recreating
this project elsewhere. `capture-session.json` records their source and theme;
`story.json` contains reviewed source-pixel controls and adjacent ports.

```powershell
uv run --script projects/reddit-navigation-video/scripts/build_story.py
uv run --script projects/reddit-navigation-video/scripts/render_tutorial.py --audit-only
uv run --script projects/reddit-navigation-video/scripts/render_tutorial.py
```

The builder reuses narration when text, voice and rate are unchanged. It
measures audio with ffprobe and derives cues from provider word boundaries.
The renderer uses the bundled Line World helper, preserves source screenshots
and encodes one continuous audio track. Every scene is rounded to complete
30 fps frames. The result is a 1920 by 1080 H.264/AAC MP4 of approximately
105 seconds with nine scenes. The voice is `es-CL-CatalinaNeural` through
Microsoft Edge speech/edge-tts. This is a local render, not a native Google
Vids voice or export.

## Change timing

Edit `audioLead` and the scene-local `cues[].at` in `story.json` when the guide
needs to arrive earlier or later. Keep each cue within its scene and in order.
Edit `duration` to extend the reading hold; do not shorten a scene below the
measured narration extent. Rerun only `render_tutorial.py` for these timing
edits. Rerunning `build_story.py` deliberately regenerates timings from the
measured voice and replaces manual story edits.

To change narration, edit `request()` in `scripts/build_story.py` and run the
builder first. Only changed voice requests are regenerated. Review source
controls again if new captures change their positions. `panSeconds` controls
the calm travel time within a scene; keep a stable scale after its entry.

Final output, poster, encoded-frame review and source audit belong under
`artifacts/videos/`, `artifacts/images/` and `artifacts/reviews/`.
