Prepare a small offline video-source fixture that explains the people in a
process. Use only the copied line-world-video skill and normal local tools.
Keep the skill read-only. Do not use network, live browser sessions, sibling
skills, repository documents, skill unit tests or acceptance galleries. A local
headless browser for your authored HTML is allowed.

The fixture is explicitly fictional: Ada Example built a compiler, and Bo
Sample designed a dataset. Show two geometric portrait placeholders, their full
names and short contribution captions beside a connected compiler/dataset
diagram. They are synthetic placeholders, not photographs of real people.
Use a white 1920x1080 frame with gray structure and primary-red attention. No
visible title. Keep labels clear of faces and other text.

Make a 10-second scene with stable ID method. Its narration names Ada Example
and explains that she built the compiler, then names Bo Sample and explains
that he designed the dataset. Bind each name to a distinct semantic cue and
an adjacent guide position. Use declared synthetic word timing at seconds 3
and 7; do not claim measured real audio. No actual audio/video rendering needed.
Source URLs may use example.org and must be identified as fixture provenance.

Create exact paths `film/story.json`, `film/media.json`, `film/cues.json` and
`film/index.html`. Use the skill's person data contract and actual DOM markers;
expose #stage, renderClip(index,localSeconds), loaded readiness and a deterministic
guide. Use the actual bundled people-context inspector to create
`review/people.json` with source observations and no findings, plus
`review/hero.png`. Then create a negative copy with one person's name removed
from the narration while retaining their portrait and contribution. Capture its
expected nonzero preflight status inside a small driver, so an expected rejection
does not become a tool execution error. Write `review/negative.json` with the
actual missing-spoken-name finding and `review/checks.json` with explicit booleans
and top-level ok after reviewing both results.

Use uv scripts with declared dependencies for additional Python work rather
than probing bare Python packages. Use the reusable helper for inspection and
screenshot capture; avoid writing another custom browser auditor. State honestly
that all identities, contributions and timing are synthetic test data.
