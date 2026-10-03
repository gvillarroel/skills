# Changing velocity and integrated distance

Create an 8-second HyperFrames explanation of an ideal vehicle on a straight road,
960 by 540 pixels, 12 fps. Speed starts at 2 m/s. At 2 seconds, the speed control
increases it linearly to 6 m/s over 2 seconds; it stays 6 m/s for the rest. Distance
starts at zero and must integrate that full speed history, including the ramp.
The interactive preview may explore constant speeds from 0 to 6 m/s. Keep the
model and its illustrative assumptions outside the filmed stage.

Show a dominant vehicle/road mechanism with a speed encoding and its coordinated
distance-history representation. Do not replace the mechanism with numbers in
boxes. Keep scales fixed and large enough for the legal preview inputs. For this
case I explicitly request colorset2: red identifies speed, blue identifies distance,
and those identities must be consistent across linked representations. Add only
direct labels, units and necessary axes; no title cards, decorative headline,
prose captions or closing slogan. Use one shared seekable state. The controls must
work outside the filmed frame and restore the scripted event.

Deliver exactly `out/video.mp4`, `out/project/index.html`,
`out/project/preview.html`, `out/project/manifest.json`, `out/project/brief.json`,
`out/audit.json`, `out/media.json` and the rendered-movie contact sheet
`out/contact.jpg`. Check actual browser state and input propagation, reverse seeks,
units, final values, motion and full MP4 decode; repair findings.

`skills/hyperframes-explainer/` is read-only. Keep generated files and caches in
this workspace. Normal local Node.js, Chrome/Chromium, FFmpeg and uv are available;
network installation of local project packages is permitted. Do not read sibling
skills, repository docs, acceptance fixtures or external files. No hosted service
or account is required.

