Use $awsome-videos.

Create a production-ready plan-only compressed explainer brief for:

Title: `SQLite Indexes in 100 Seconds`
Promise: `Explain how indexes trade extra structure and write cost for faster lookups.`
Audience: `Intermediate developers who know SQL basics but do not know how database indexes work.`
Runtime target: `1:40`

Required outputs:

- `outputs/sqlite-indexes-blueprint.json`
- `outputs/sqlite-indexes-brief.md`
- `outputs/sqlite-indexes-validation.json`
- `outputs/sqlite-indexes-style.json`
- `outputs/sqlite-indexes-readiness.json`

Requirements for `outputs/sqlite-indexes-brief.md`:

- Follow the awsome-videos production-ready plan output contract, not just a prose summary.
- Choose the `compressed explainer` format.
- Include a title/promise, audience, runtime target, pattern blueprint summary, hook/cold-open line, visual source plan, animation and transition vocabulary, music/SFX plan, script style notes, evaluation checklist, and concrete `check_video_brief.py`, `score_style_fidelity.py`, and `score_video_readiness.py` validation commands.
- Include at least 8 timed beats with columns for time, script purpose, visual, animation, transition, audio, and voiceover.
- Use concrete, non-repeated voiceover lines; do not leave template placeholders.
- Use source-backed visuals with concrete source URLs or domains. Acceptable sources include official SQLite documentation pages such as `https://www.sqlite.org/queryplanner.html`, `https://www.sqlite.org/lang_createindex.html`, and `https://www.sqlite.org/eqp.html`.
- Keep every beat visually concrete: name the actual code, query plan, B-tree/lookup diagram, terminal output, or warning shown in that beat.

Do not list directories or read script source. Use the skill instructions and relevant references, write the brief, then run these commands from the workspace root:

```bash
mkdir -p outputs
uv run --script skills/awsome-videos/scripts/select_video_patterns.py --title "SQLite Indexes in 100 Seconds" --promise "Explain how indexes trade extra structure and write cost for faster lookups." --format "compressed explainer" --runtime "1:40" --output outputs/sqlite-indexes-blueprint.json --json >/dev/null
uv run --script skills/awsome-videos/scripts/check_video_brief.py outputs/sqlite-indexes-brief.md --require-voiceover --require-source-links --json > outputs/sqlite-indexes-validation.json
uv run --script skills/awsome-videos/scripts/score_style_fidelity.py --brief outputs/sqlite-indexes-brief.md --pattern-blueprint outputs/sqlite-indexes-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output outputs/sqlite-indexes-style.json --json
uv run --script skills/awsome-videos/scripts/score_video_readiness.py --brief outputs/sqlite-indexes-brief.md --require-voiceover --require-source-links --output outputs/sqlite-indexes-readiness.json --json
```

The final answer must be under 12 lines and report:

- Whether every required output path exists.
- Whether `sqlite-indexes-validation.json`, `sqlite-indexes-style.json`, and `sqlite-indexes-readiness.json` each have `"ok": true`.
- The brief validator beat row count, source link count, and voiceover line count.
- The style fidelity score and any penalties.
- The readiness score, readiness label, weak categories, and any fixes.
- Whether the brief has at least 8 timed beats and concrete source links.
