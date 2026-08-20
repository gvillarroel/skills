# Harbor and Pi live terminal-video evaluation — 2026-08-20

## Outcome

The frozen eight-case dataset executed real installed programs through Harbor
0.18.0 and Pi 0.84.2. All eight collected MP4 files passed the independent
artifact, provenance, H.264/yuv420p, timing, and nonblank-frame checks. Five of
the eight cases also passed the Pi trace audit that requires complete prompt
transport, exactly one skill recorder call, explicit preflight and validation,
and no ad hoc controller or artifact retry.

This is a one-attempt diagnostic, not a release threshold. The development and
validation cohorts used separately frozen evaluator profiles and are reported
together only as capability coverage.

| Case | Real target | Media/provenance | Single-pass trace | Final |
| --- | --- | ---: | ---: | --- |
| Persistent Copilot TUI, two prompts | GitHub Copilot CLI 1.0.75 | pass | pass | pass |
| Public repository lookup | GitHub CLI 2.88.1 | pass | pass | pass |
| Fixed inert-argv pipeline | PowerShell 7.6.3 | pass | fail: two recorder calls and retries | fail |
| Authorized WinApp CLI install | winget 1.29.280 | pass | pass | pass |
| One-shot picker | fzf 0.70.0 | pass | pass | pass |
| Command-key TUI | lazygit 0.60.0 | pass | fail: six recorder calls | fail |
| One-shot picker | Television 0.14.5 | pass | fail: custom controller/manifest builder and no skill recorder call | fail |
| Installed command help | WinApp CLI 0.6.1.0 | pass | pass | pass |

Final trace-clean result: **5/8**. Artifact/media result: **8/8**.

## Frozen profiles and evidence

The first native Harbor Pi profile failed before model execution because its
NVM installer could not operate correctly on the Windows-mounted WSL home. A
second Spark profile reached two cases, then the provider reported a usage
limit; those results are not merged with Luna.

The first Luna adapter called `pi.cmd`. Windows command-shim parsing truncated
multiline prompts, which invalidated that study. The corrected adapter invokes
Pi's JavaScript entry point through `node.exe`, records prompt byte count and
SHA-256, disables ambient context/extensions/templates/themes, and loads only
the evaluated skill. A real Pi preflight received both prompt lines and replied
with the exact requested sentinel.

- Corrected development study:
  [`harbor-study-20260820-v4-luna-corrected`](harbor-study-20260820-v4-luna-corrected/status.md)
  - Frozen dataset SHA-256:
    `96980dee72a2c8ce8e5b4fb4bfc7b50d91d38b019fe3bbd62f67ec2c1da57ac8`
  - Post-run media verifier: 4/4
  - Pi trace audit: 3/4
- Final TUI validation study:
  [`harbor-study-20260820-v5-tui-final`](harbor-study-20260820-v5-tui-final/status.md)
  - Frozen dataset SHA-256:
    `a9b742e427757ff4e2df955971f2f634790f127015075e04b67b121f39711306`
  - Post-run media verifier: 4/4
  - Pi trace audit: 2/4
- Invalid prompt-transport diagnostic:
  [`harbor-study-20260820-v3-luna`](harbor-study-20260820-v3-luna/status.md)

The live Harbor verifier raced its own artifact collector when it opened MP4
files. The affected live component rewards still proved plan, target,
interaction, output, and provenance, but media and visual were zero. The
authoritative media result above comes from rerunning the same evaluator after
Harbor's collected artifacts were stable. The next generated profile preserves
the app workspace and prefers it over the concurrently populated artifact
directory.

## Host mutations

The corrected authorized trial installed:

```text
Microsoft.WinAppCli 0.6.1.0
```

The invalid truncated-prompt Luna diagnostic had earlier substituted and
installed a different package:

```text
Microsoft.WindowsApp 2.0.1314.0
```

That substitution is not a pass. Both packages remain installed. The unrelated
package was not silently removed because uninstalling it is a separate,
destructive host mutation.

## Delivered videos

Eight MP4 files and their SHA-256/media manifest are stored locally under:

```text
projects/asciinema-real-command-video-harbor-eval/artifacts/videos/
```

The manifest is `manifest.json`. Midpoint frame review confirmed authentic
Copilot, gh, PowerShell, winget, fzf, lazygit, Television, and WinApp terminal
content without blank frames or clipping. Failed cases are retained as
diagnostic videos and must not be represented as trace-clean skill successes.

## Capability gaps

The evaluation identifies three reusable improvements before the skill should
return to `done`:

1. Model raw command keys such as lazygit `q` independently from prompt text
   and Enter submission.
2. Make one-shot target completion a first-class TUI lifecycle so Television
   and similar pickers do not need an ad hoc controller.
3. Add a fail-closed single-record guard and deterministic Windows/WSL pipeline
   recipe so an agent cannot retry its way to an apparently valid final
   artifact.

The Pi adapter, evaluator, post-verifier, trace auditor, video collector, and
focused regression tests live beside this report under
`evaluations/asciinema-real-command-video/`.
