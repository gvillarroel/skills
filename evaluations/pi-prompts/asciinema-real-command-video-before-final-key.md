Use the installed `$asciinema-real-command-video` skill to create one authentic
local lazygit terminal recording in this isolated workspace.

The skill name is not a shell executable. Invoke only its bundled Python
script as documented; do not run `asciinema-real-command-video`, command-help
probes, environment-variable discovery, or ancestor searches. The supplied
template and workflow below contain the required interface details.

Create `fixture/repo` as a small Git repository with one committed tracked file
and one unstaged tracked change. Configure a project-local lazygit directory so
startup popups and background network activity are disabled. Copy
`skills/asciinema-real-command-video/assets/templates/lazygit-session-plan.json`
to `source/session-plan.json`. Also copy
`skills/asciinema-real-command-video/assets/templates/lazygit-config.yml` to
`fixture/repo/.git/lazygit-config/config.yml`; do not reconstruct, extend, or
preflight that YAML and do not prelaunch or warm up lazygit. The plan-relative
repository path and requested one-second pause already match this task, so do
not reconstruct its JSON or regex fields. Record the real installed
`lazygit.exe` TUI. After the authentic interface is ready, pause for one second
and send only lazygit's real `q` key. Do not invent Enter, use a custom
controller, simulate the UI, or retry a failed recording.

Run plan validation, explicit preflight, exactly one recording transaction,
and the independent validator. Create these exact outputs:

- `source/session-plan.json`
- `deliverables/session.cast`
- `deliverables/session.mp4`
- `deliverables/session.manifest.json`
- `deliverables/session.manifest.runtime.json`
- `deliverables/validation.json`

The project-local recorder and renderer are not pre-provisioned. Before
preflight, bootstrap them once with the skill's `bootstrap-tools` command into
`.tools/asciinema`; do not search ancestors, prior evaluation runs, environment
variables, or unrelated directories for binaries. Then pass that directory to
preflight, record, and validate. Keep all operations local and read-only except
for the official tool download, isolated fixture, and requested recording
artifacts.
