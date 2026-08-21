# Asciinema Real Command Video Complex Harbor Evaluation — 2026-08-21

## Outcome

The evolved skill passed both a three-case native Harbor validation regression
and a previously untouched three-case holdout. Every trial used installed Pi
to operate a real terminal target, recorded exactly once, completed without an
execution error, and received reward 1.0 in all twelve dimensions. The three
holdout MP4s are 14.67 to 16.40 seconds long.

The full nine-task dataset covers six real TUI cases and three direct-argv
cases. Eight tasks require a video longer than 10 seconds. Targets include
GitHub Copilot CLI, fzf, PowerShell, GitHub CLI, lazygit, and Television.

## Evaluation design

The study used Harbor 0.18.0, Pi 0.84.2, and
`openai-codex/gpt-5.6-luna`, with one attempt and concurrency one. Development,
validation, and holdout are disjoint three-task splits. The policy is:

1. Develop against the development split.
2. Run the validation regression.
3. Freeze the complete candidate skill payload.
4. Release the untouched holdout exactly once.
5. Preserve native results, traces, casts, manifests, validation reports, and
   derived media without artifact replacement or verifier recovery.

Schema-v2 contracts verify exact prompt, text, and key order; minimum action
and pause counts; planned dwell time; source-cast duration; real executable
identity; target exit; H.264/yuv420p media; and target-visible frames. An
independent Pi trace audit checks prompt integrity, exactly one skill `record`
call, no direct Asciinema invocation, no custom source path, and no retry
mutation.

## Frozen evidence

- Run root:
  `evaluations/runs/asciinema-real-command-video-complex-candidate-20260821-v3/`
- Development split SHA-256:
  `ba3c3441dd74930fa9c2285e4b29970b8398b92a678a535a387cdff58330028e`
- Validation split SHA-256:
  `95a9534dc8aaee5cd8fa06dab29d94d31afd68f187e3933f119c2ccbaaca5041`
- Holdout split SHA-256:
  `5ba2e7883004660165d0d052c0bc1902edb82111b3a086d03edfe952f1720396`
- Candidate skill SHA-256 before and after holdout:
  `eabcc603ea9bd23717096236f4d57ceac04bb092e4b2372223f693640181d7b6`
- Validation job:
  `asciinema-real-command-video-complex-candidate-20260821-v3-validation-pi`
- Holdout job:
  `asciinema-real-command-video-complex-candidate-20260821-v3-holdout-pi`

The frozen candidate contains eleven versioned source files plus two Python
interpreter cache files staged by the custom Harbor adapter. Its digest was
recomputed after holdout and remained identical. All eleven versioned files in
the publication candidate byte-match their frozen counterparts.

## Native results

| Split | Result | Execution errors | Retries | Trace audit |
| --- | ---: | ---: | ---: | ---: |
| Validation regression | 3/3 | 0 | 0 | 3/3 |
| Untouched holdout | 3/3 | 0 | 0 | 3/3 |
| Combined | 6/6 | 0 | 0 | 6/6 |

Every native trial received 1.0 for artifacts, complexity, interaction, media,
output, plan, presentation, provenance, target, validation, visual, and total
reward. All six trace audits prove exactly one recorder call, no direct
recorder call, no alternate source path, no retry mutation, complete prompt
byte/SHA-256 transport, valid JSON, and matching wrapper markers.

## Untouched holdout media

| Task | Authentic target and interaction | MP4 | Source cast | MP4 SHA-256 |
| --- | --- | ---: | ---: | --- |
| `complex-holdout-lazygit-deep-path-tui` | lazygit on branch `release/demo`; Down, Down, Up, Tab, Tab, q | 16.40 s | 18.638 s | `2930c5130a887197a1aa4fd4ce9c0936e7b3954dc1a95f35952d3ff42dd200a1` |
| `complex-holdout-powershell-five-stage-argv` | PowerShell phases PREPARE through FINISH plus inert label argv | 15.733333 s | 13.768 s | `8e78e3ff1baec33f09aa99d5ae77828b978d8193e7669bf0405b520143a621f5` |
| `complex-holdout-television-long-edit-tui` | Television query edit, Backspace, navigation, and Enter selection | 14.666667 s | 16.325 s | `50a20c677a306ca6e65141b6c826804d40a9fa81a96d1e993ad102b82cbb4b83` |

Stable local copies and their machine-readable manifest are under
`projects/asciinema-real-command-video-complex-harbor/artifacts/videos-v3-holdout/`.
They are verification artifacts and remain outside git.

## Failure that drove the final evolution

Candidate v2 passed two validation tasks but failed the lazygit task. The
native trace exposed two distinct defects: a relative Windows config path was
not visible to the Windows process, and the deeply nested Harbor path caused
Git-for-Windows errors including `Filename too long` and
`fatal: '$GIT_DIR' too big`. The agent then evaded the plan-scoped attempt
ledger by changing plan and output names, producing five recorder calls. That
result is preserved as failed evidence and is not counted as candidate proof.

The promoted implementation now:

- permits `{windows_working_directory}` only for native Windows TUI targets;
- translates the verified WSL working directory with native `/usr/bin/wslpath`;
- obtains a collision-checked, locked temporary drive with `subst.exe`;
- expands the reviewed launch argv only while that mapping exists;
- records mapping creation, exact argv expansion, and release in provenance;
- always releases the mapping and fails closed if cleanup fails;
- requires repo-local `core.longpaths=true` for a bridged lazygit repository;
- rejects casts containing known lazygit/Git path errors; and
- defines one attempt per user-requested deliverable, so renamed plans,
  outputs, or adapters never authorize a retry.

The v3 validation lazygit case and the deeper untouched holdout both passed in
one recording transaction with `windows-working-directory-bridge`,
`lazygit-project-longpaths`, and `lazygit-path-clean` evidence. Both targets
exited 0, the mappings were released, and no path-error text remained.

## Visual review

Opening, middle, and final full-resolution frames were inspected for all three
holdout MP4s:

- lazygit shows the real status UI, `release/demo`, commits, staged and
  unstaged changes, an untracked file, and genuine panel navigation;
- PowerShell shows the real provenance card, all five timed phases, the exact
  inert label, and exit status 0; and
- Television shows the real Custom Channel UI, the query changing from `ox`
  to `o`, result navigation, and final selection `golf.log`.

No reviewed frame contains a simulated terminal, invented target output,
controller lead-in, restored outer shell, lazygit path failure, or unresolved
startup modal.

## Earlier broad cohort

The preceding v1 development/validation cohort remains useful breadth
evidence: six real Copilot, fzf, PowerShell, gh, lazygit, and Television
recordings, five longer than 10 seconds. Native Harbor completed all six with
zero execution errors and passed 5/6; the sole miss was an old validation
label mismatch, while corrected artifact-only reverification passed 6/6. The
Copilot case visibly typed three exact prompts in one persistent real TUI and
produced a 34.93-second MP4.

## Local regression tests

- Controller: 39/39 passed.
- Harbor verifier: 12/12 passed.
- Complex dataset builder: 7/7 passed.
- Pi trace auditor: 4/4 passed.
- Harbor Pi wrapper: 2/2 passed.

The trace-auditor suite includes a regression for single-quoted absolute skill
script paths. That evaluator-only correction was made after holdout because
the original audit parser undercounted a real Television recorder call; it did
not alter the frozen candidate or any task artifact.
