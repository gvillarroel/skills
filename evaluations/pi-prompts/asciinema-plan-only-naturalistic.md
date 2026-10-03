Prepare a plan for a future non-interactive CPython terminal demo, using the
loaded `asciinema-real-command-video` skill. I only want to review and validate
the plan today. Do not launch Python or any target process, install recording
tools, record a cast, render a video, or contact the network.

Treat `skills/asciinema-real-command-video/` as read-only. Use only this prompt
and the skill's task-relevant guidance. Do not inspect helper source,
acceptance examples, sibling skills, parent directories, or repository docs.
Keep generated files inside this workspace.

Use the existing workspace root as the future command's working directory,
the `python3` executable with its real version query, a 92-by-24 terminal,
GitHub Dark theme, 18-pixel font, 1.4 line height, 24 fps, real-time speed, no
idle-time cap, and a one-second final hold. Limit declared side effects to
read-only local Python commands.

Plan two independent invocations, in this order:

1. Receive this exact text as one argument and print it verbatim:
   `alpha; echo untouched && $(printf inert)`
2. Receive this exact text as one argument and print its SHA-256 in UTF-8:
   `A second, independent argument.`

Use a 30-second timeout, half a second of pause after each command, and require
exit code zero. Preserve the exact text and punctuation without evaluating
them as shell syntax.

Create exactly these deliverables:

- `outputs/planned-demo/session-plan.json`
- `outputs/plan-validation.json`

Use the bundled plan validator and preserve its unmodified JSON output in the
second file. The planned-demo directory must contain only its session plan.
Report the validation result and paths, then stop before preflight or capture.
