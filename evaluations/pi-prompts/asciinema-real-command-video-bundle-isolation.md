Use the installed `$asciinema-real-command-video` skill to create two authentic
local direct-argv terminal videos in this isolated workspace. This is one
two-video request, so the result must use two sibling video directories and
must not share any plan, cast, runtime, MP4, manifest, ledger, result,
validation, or bundle-index path.

The skill name is not a shell executable. Invoke only its bundled Python
script as documented. Do not run command-help probes, search ancestors, use
unrelated skills, simulate a terminal, construct a custom recorder, edit the
bundled script, or retry a failed recording.

Initialize these exact fresh directories with the bundled `direct-argv`
template:

- `deliverables/first-python-video`
- `deliverables/second-python-video`

Do not edit either initialized `session-plan.json`; the template is already a
valid read-only real `python3` plan for this isolation test. The project-local
recorder and renderer are not pre-provisioned, so bootstrap them once into
`.tools/asciinema` and use that same dependency directory for both videos.

Process the first directory completely before the second. For each directory,
run plan validation, `preflight-video`, exactly one `record-video`, and
`validate-video`. Never invoke the legacy explicit-path `record` command and
never run the two recording lifecycles concurrently.

Each final directory must contain exactly these ten files and no others:

- `.session-plan.recording-attempt.json`
- `bundle.json`
- `preflight.json`
- `record-result.json`
- `session-plan.json`
- `session.cast`
- `session.manifest.json`
- `session.mp4`
- `session.runtime.json`
- `validation.json`

After both directories pass, run the skill's read-only
`audit-video-bundles` command once with both directories in the order listed.
Require it to report `status: passed`, `video_count: 2`, and the two matching
video IDs. Do not replace that command with an ad hoc audit script. Finish by
reporting the two MP4 paths and bundle-index paths. Keep everything local.
