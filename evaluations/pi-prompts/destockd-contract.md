# Contract smoke: live public catalog and exact shot download

Use the supplied destockd-video-search skill as a read-only resource. Work only
inside this isolated workspace. Public network reads and one small video
download are authorized. Do not read external local files or other skills.

Run the helper to save the current Destockd collections to `catalog.json`.
Resolve the actual shot page
`https://www.destockd.com/#/shot/Women%20Astronauts%20Training/shot_050`,
save its refreshed metadata to `selected.json`, and download that exact shot to
`chosen.mp4`, retaining the helper's `chosen.mp4.json` receipt. Do not substitute
a preview or another shot. Report the exact identity, source and measured media
properties if a probe is available. Do not claim that this establishes the
contents of every frame or clears all reuse rights.
