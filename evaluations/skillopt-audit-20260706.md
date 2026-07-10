# SkillOpt Audit - 2026-07-06

## Installation

- Installed Microsoft SkillOpt with `uv tool install skillopt --python 3.12`.
- Verified the isolated tool installation exposes `skillopt-train`, `skillopt-eval`, and `skillopt-sleep`.
- Confirmed `skillopt-train --help`, `skillopt-eval --help`, and `skillopt-sleep --help` run successfully.

## Source Check

- Official project: https://github.com/microsoft/SkillOpt
- Official documentation: https://microsoft.github.io/SkillOpt/docs/guideline.html
- Microsoft Research overview: https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters/

Microsoft's installable optimizer is named SkillOpt. `SkillOps` exists as a broader term in research writing, but the available Microsoft tool used here is SkillOpt.

## Local Runs

Harvested recent Codex sessions:

```powershell
skillopt-sleep harvest --project . --source codex --backend mock --lookback-hours 0 --max-sessions 100 --max-tasks 40 --output projects\skillopt-audit\artifacts\tasks\codex-harvest.json --json
```

Result: 3 sessions and 3 tasks were harvested. The harvested tasks were too broad or off-target for safe automatic skill edits.

Dry-ran SkillOpt-Sleep against `mermaid-colorset-styler` and `html-d3-anime-video-workflow` with the mock backend:

```powershell
skillopt-sleep dry-run --project . --source codex --backend mock --lookback-hours 0 --max-sessions 100 --max-tasks 20 --target-skill-path .agents\skills\mermaid-colorset-styler\SKILL.md --json
skillopt-sleep dry-run --project . --source codex --backend mock --lookback-hours 0 --max-sessions 100 --max-tasks 20 --target-skill-path .agents\skills\html-d3-anime-video-workflow\SKILL.md --json
```

Both runs produced no accepted edits, with `baseline: 0`, `candidate: 0`, and `gate_action: reject`.

Dry-ran SkillOpt-Sleep against `html-d3-anime-video-workflow` with the Codex backend:

```powershell
skillopt-sleep dry-run --project . --source codex --backend codex --lookback-hours 0 --max-sessions 20 --max-tasks 1 --target-skill-path .agents\skills\html-d3-anime-video-workflow\SKILL.md --progress --json
```

Result: no accepted edits, with `baseline: 0`, `candidate: 0`, and `gate_action: reject`.

## Forward Validation

The SkillOpt maintenance pass also ran isolated Spark forward tests after updating skill guidance:

- `mermaid-colorset-styler-skillopt-maintenance-20260706-spark-1-json` passed exact output checks, `styled-check.json::missingStyleCount=0`, event checks, and read-surface inspection with no `assets/examples` reads.
- `scene-composition-skillopt-maintenance-20260706-spark-4-json` passed exact output checks, event checks forbidding workspace discovery commands, and read-surface inspection after tightening the skill and zero-padding evaluation prompt.
- `scene-transition-skillopt-maintenance-20260706-spark-4-json` passed exact output checks, event checks forbidding workspace discovery commands, and read-surface inspection after tightening the skill, zero-padding evaluation prompt, and required transition-field guidance.

Earlier transition and composition runs exposed repeated workspace probes such as `rg --files`, `find`, and `ls`. Those failures were kept as design feedback and resolved by making the isolated-run contract explicit in both the skills and the zero-padding `pi` prompts.

## Conclusion

SkillOpt is installed and operational, but the archived sessions available on 2026-07-06 did not provide enough target-specific, scoreable evidence for automatic edits. The safer improvement is to make the repository more SkillOpt-ready:

- Skill runtime instructions now say that SkillOpt proposals require reviewed tasks, exact output paths, and deterministic gates.
- `mermaid-colorset-styler` explicitly rejects candidates that add class assignments, change geometry, leave YAML, or switch away from Mermaid `base`.
- `html-d3-anime-video-workflow` explicitly treats no-edit `baseline: 0` / `candidate: 0` SkillOpt results as insufficient scoring signal, not proof of optimality.
- `scene-composition-director` and `scene-transition-director` now point maintainers to existing validator commands and checked isolated `pi` prompt files, and their isolated-run instructions explicitly block workspace discovery before writing exact requested outputs.
