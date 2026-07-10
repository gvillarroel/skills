# Evaluation Rubric

Use this reference when critiquing a brief, storyboard, renderer, or final MP4. Score only what the artifact actually proves.

Before running command examples, set `$env:AWSOME_VIDEOS_SKILL` to this skill directory in the current workspace.

## Readiness Gates

A production-ready short technical explainer must pass these gates:

- Hook appears in the first 5 seconds and states a claim, contradiction, or concrete payoff.
- Timed beat table has at least 8 beats for short videos.
- Every beat has script purpose, visual, animation, transition, and audio.
- Voiceover has one concrete line per beat; template placeholders and repeated filler lines are not production narration.
- Visuals are source-bound: each major visual explains a claim, proof, mechanism, contrast, or warning.
- Every finished-video asset exists at its declared project path, carries provenance/rights and a producer validation report, maps to stable beat/scene IDs, and passes the final-crop resolution check.
- Every finished-video scene has anchors, rejected alternatives, text bounds, focal hierarchy, safe zones, four motion phases, reduced-motion intent, an outgoing seam, and first/hold/emphasis/final evidence.
- The renderer binds visible media to manifest output and SHA-256 plus composition-object IDs; `sourceProofVisible=true` or a bare SVG ID is not evidence.
- Source-backed or publishable briefs include concrete source URLs or domains and pass `check_video_brief.py --require-source-links`.
- Motion changes meaningfully every 6-10 seconds in short videos.
- Audio plan includes voiceover role, bed, ducking, and punctuation cues.
- Audio report identifies whether audio is final or synthetic validation audio; publishable work must pass `--require-final-audio` and prove `finalAudioDurationOk: true`.
- Final beat callbacks to the hook or gives a clear practical rule.
- Validation commands and expected results are included; plan-only handoffs should include brief, style fidelity, and readiness commands.
- Final production notes include non-thin structured visual review lines for legibility, beat coverage, visual mechanism, pacing/transition, source binding, audio sync, and caveats.

## Scoring

Score each category from 0 to 3:

| Category | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Hook | No clear hook | Generic intro | Clear claim after delay | Immediate claim plus proof visual |
| Script density | Wanders | Sparse or repetitive | Mostly dense | Every beat defines, proves, contrasts, jokes, or warns |
| Visual mechanism | Decorative | Prose or self-reported state only | Most scenes explain claims | Reviewed frames and renderer IDs prove the core mechanism without narration dependency |
| Source binding | Unsupported | URLs or planned assets only | Some validated local proof | Ready assets with provenance, claim/scene use, visible renderer IDs, and reviewed evidence |
| Transitions | Random | Mostly decorative | Mark sections | Mark idea changes, proof points, reversals, or jokes |
| Audio direction | Missing | Vague music | Bed plus some cues | Bed, ducking, hits, ticks, risers, dropout, and final tail |
| Format fit | Wrong length/style | Partly fit | Good fit | Matches format, pacing, and audience precisely |
| Validation | None | Manual only | Brief or artifact check | Brief, artifact, renderer beat coverage, audio report, contact sheet, and motion/quality checks |

Interpretation:

- 22-24: ready to produce or publish after normal polish.
- 18-21: usable, but fix the weakest category first.
- 14-17: needs a rewrite or storyboard repair.
- 0-13: not yet an Awesome/Fireship-style explainer.

For a deterministic first pass, run:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --brief path/to/brief.md --require-voiceover --json
```

Then score corpus-style fidelity:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief path/to/brief.md --pattern-blueprint path/to/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --json
```

For a finished package, include the video and reports:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --brief path/to/brief.md --video path/to/final.mp4 --renderer-report path/to/render-state.json --quality-report path/to/quality-report.json --motion-report path/to/motion-report.json --capture-manifest path/to/capture-manifest.json --audio-report path/to/audio-report.json --contact-sheet path/to/contact-sheet.jpg --require-voiceover --output path/to/readiness-score.json --json
```

Treat `"ok": true` as a readiness signal, not proof of final taste. Finished work must also pass the hash-bound visual contract, renderer asset/composition coverage, and an authored scene review after viewing full-resolution frames and full-speed playback. Automated nonblank checks do not prove composition or source binding. Final notes must name asset quality, composition, renderer asset binding, legibility, beat coverage, mechanism, pacing/transition, source binding, audio sync, and caveat findings.
For publishable work, also use `--require-final-audio`; otherwise synthetic validation audio can be acceptable for a preview but must be reported as unfinished audio. A final-file report with `finalAudioDurationOk: false` is still unfinished, because the audio source does not cover the requested runtime.
For source-backed publishable work, also use `--require-source-links` in brief validation, style fidelity, readiness scoring, and package validation. Concrete source URLs/domains can satisfy full source binding when the storyboard uses generated diagrams instead of captured source screenshots, but the claims still need to map to those sources.

## Common Failure Modes

- Text-only plan: timed beats exist, but visuals do not prove anything.
- Wireframe delivery: the untouched `AWSOME_SCAFFOLD_WIREFRAME` is presented as a finished renderer.
- Asset theater: URLs or manifest rows exist, but local files are missing, undersized, unlicensed, orphaned, or never visibly loaded.
- Composition theater: scene names exist, but every frame reuses one card layout or lacks a focal armature and reviewed evidence.
- Review theater: `ok` or generated prose claims inspection without frame paths, current input hashes, corrections, or full-speed playback.
- Source placeholder drift: the visual source plan says "official docs" or "primary sources" but provides no concrete URL or domain.
- Decoration drift: animations look active but do not correspond to mechanism changes.
- Audio afterthought: music is named but not assigned to timing roles.
- Placeholder audio drift: the MP4 has an audible validation tone, but no final narration/music/SFX report.
- Short final audio drift: the report says a file was supplied, but `sourceDurationSeconds` is shorter than the video and `finalAudioDurationOk` is false.
- Voiceover placeholder drift: the template starter lines remain, or the same explanatory filler line repeats across beats.
- Overlong setup: background arrives before the first claim or proof.
- Weak final beat: no callback, warning, tradeoff, or practical rule.
- Validation theater: commands are listed, but no expected pass/fail evidence is supplied.

## Critique Format

Lead with findings:

```markdown
## Findings

- Severity: issue, evidence, fix.

## Score

Category table with 0-3 scores.

## Fix Plan

Ordered edits that would move the artifact to ready.
```

When the artifact is an MP4, mention both automated evidence and visual inspection evidence.
