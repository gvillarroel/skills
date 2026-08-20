# Asciinema Real Command Video Validation - 2026-08-20

## Outcome

`asciinema-real-command-video` is complete. It records the requested installed executable inside a real Asciinema PTY, passes exact reviewed prompts as direct argv values, preserves a cast and runtime report, renders a non-looping agg GIF intermediary to H.264 MP4 with ffmpeg, and independently validates executable, prompt, process, cast, and media evidence.

The skill does not simulate terminal output, enable Asciinema input capture, upload recordings, overwrite evidence, or add blanket target permissions.

## Implementation evidence

- One strict JSON session plan controls target identity, working directory, prompt order, terminal geometry, render settings, timeouts, accepted exit codes, and declared scope.
- Duplicate JSON keys, unknown schema fields, missing prompt substitution, likely credentials, missing targets, existing output paths, non-PTY execution, missing Asciinema session identity, input events, marker gaps, prompt/hash mismatches, unexpected exit codes, and invalid MP4 properties fail closed.
- Prompt text is substituted into one argv item and is never interpolated into a shell command. Literal braces used by Python f-strings and JSON remain unchanged.
- The first unexpected target result stops all later steps.
- Official Asciinema 3.2.1 and agg 1.9.0 binaries can be downloaded into a project-local directory with GitHub-published SHA-256 verification.
- Windows `bootstrap-tools`, `record`, and `validate` commands automatically translate paths and re-execute inside the default WSL2 distribution. Native Windows ffmpeg/ffprobe paths are forwarded explicitly.
- Machine markers are stored as OSC title sequences in the cast, so independent validation can recover them without cluttering the rendered video.

## Local regression and real capture

Command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --script skills/asciinema-real-command-video/scripts/test_asciinema_command_video.py
```

Result: 13/13 tests passed. Coverage includes duplicate keys, missing prompt substitution, secret rejection, literal f-string braces, direct-argv metacharacter containment, stop-on-failure behavior, no-overwrite behavior, v2/v3 cast timing, required PTY/cast evidence, input-event rejection, Windows-to-WSL path translation, and official tool pins.

The native Windows public command was then exercised without hand-built WSL commands:

```powershell
uv run --script skills/asciinema-real-command-video/scripts/asciinema_command_video.py record evaluations/pi-prompts/asciinema-real-command-video-real-smoke-plan.json --cast projects/asciinema-real-command-video/artifacts/smoke-bridge-final/session.cast --mp4 projects/asciinema-real-command-video/artifacts/smoke-bridge-final/session.mp4 --manifest projects/asciinema-real-command-video/artifacts/smoke-bridge-final/session.manifest.json --tools-dir projects/asciinema-real-command-video/artifacts/tools --json
```

The real session ran three CPython 3.12.3 processes under Asciinema 3.2.1, rendered with agg 1.9.0 and ffmpeg 8.1.1, and passed the independent validator. The cast SHA-256 was `cc0d33bffd64a07b979ab689f728106e81b29e2707122d85782144b333789c5a`; the MP4 SHA-256 was `45ad91e9ba822d30191574d8d03cd49b4468e2759a1ee5252dd6197c6557f48e`. ffprobe reported H.264 High, yuv420p, 906x540, 24 fps, 68 frames, and 2.833008 seconds. Full-resolution frame review showed target identity plus all three prompt/response boundaries with hidden machine markers and legible text.

## Isolated Spark forward tests

All runs used the runtime payload profile, strict JSON mode, and `openai-codex/gpt-5.3-codex-spark`.

1. `asciinema-real-command-video-20260820-spark-1`: Pi exited 0 and produced the requested recording, but strict evaluation failed the zero-tool-error gate. The agent had to discover Git Bash/Windows/WSL path routing and accumulated failed probes. Classification: skill operational weakness. Fix: automatic Windows-to-WSL bridge and explicit public-entrypoint guidance.
2. `asciinema-real-command-video-20260820-spark-2`: all six artifacts, JSON fields, and skill-integrity gates passed; one event failed because the plan validator mistook legitimate Python f-string braces (`{h}` and `{wc}`) for unsupported placeholders. Classification: skill validation over-constraint. Fix: replace only `{prompt}` and `{run_id}` while preserving every other brace literally.
3. `asciinema-real-command-video-20260820-spark-3`: passed every strict gate in 50.25 seconds. Pi exited 0; six exact non-empty outputs, five asserted JSON fields, model/events, zero tool errors, and unchanged skill payload all passed.

Final isolated evidence:

- Payload SHA-256 before/after: `8463feccd520e5aa696143b1a327aec0cbbbbb19760d093173c6d348f377df2a`.
- Plan SHA-256: `311c1806b902f832c654fc4924895a64fc42f9897c40660199ab4a49938f229c`.
- Cast SHA-256: `f40601cca00bfbc229764132f2dc7532bb89402e66667781c2e873fc12c9462e`.
- MP4 SHA-256: `95d1c6444d80d72cad20ff8e5100ba362d3f0d73e3bbf82349a08da4ca993b35`.
- Video: H.264/yuv420p, 906x540, 24 fps, 69 frames, 2.875 seconds.
- Read surface: prompt, `SKILL.md`, two relevant references, the generated plan, validation JSON, and final manifest. It did not read script source, examples, sibling skills, or repository documentation.
- Full-resolution frame review showed the real CPython identity plus prompt 1, prompt 2, and prompt 3 with their observed outputs and exit codes.

Required artifacts were:

- `source/session-plan.json`
- `artifacts/casts/session.cast`
- `artifacts/videos/session.mp4`
- `artifacts/manifests/session.manifest.json`
- `artifacts/manifests/session.manifest.runtime.json`
- `artifacts/manifests/validation.json`

## Repository gates

The following passed on 2026-08-20:

```powershell
uv run --with pyyaml --script C:\Users\villa\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/asciinema-real-command-video
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
git diff --check
```

`git diff --check` returned success with only existing line-ending conversion warnings for `SKILLS.md` and `skills/mermaid/agents/openai.yaml`.

## Source alignment

The implementation follows the official Asciinema CLI recording model, asciicast v3 format, and agg rendering options, and the GitHub Copilot CLI programmatic `-p` plus explicit `--session-id` interface:

- <https://docs.asciinema.org/manual/cli/quick-start/>
- <https://docs.asciinema.org/manual/asciicast/v3/>
- <https://docs.asciinema.org/manual/agg/usage/>
- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference>
- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference>
