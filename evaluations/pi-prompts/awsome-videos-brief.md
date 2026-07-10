Use $awsome-videos to create a production-ready fast technical explainer brief for a video titled "SQLite in 100 Seconds".

Requirements:

- Do not browse the web.
- Write the brief to exactly `outputs/sqlite-100-seconds-brief.md`.
- Use a compressed explainer format with a target runtime under 2 minutes.
- Include title, promise, audience, format, runtime, hook, timed beat table, visual source plan, animation/transition plan, music/SFX plan, and evaluation checklist.
- The timed beat table must contain at least 8 time ranges and include columns for time, script purpose, visual, animation, transition, and audio.
- After writing the brief, run the skill's `scripts/check_video_brief.py` validator in JSON mode against the brief.
- Write the validator JSON output to exactly `outputs/sqlite-100-seconds-validation.json`.

Expected result: both files exist, the validation JSON has `"ok": true`, and the brief is specific enough for a video producer to execute.
