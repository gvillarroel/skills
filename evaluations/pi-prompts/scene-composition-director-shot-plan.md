Use $scene-composition-director to create exactly `composition-plan.json` from this shot list. Do not create implementation code.

Video constraints:
- Format: 1920x1080 landscape
- Style: quiet technical product explainer
- Captions: possible, so keep the bottom caption band clear
- Renderer: later HTML/D3/Anime.js, but this task is composition planning only. Anime.js may appear in renderer handoff, but do not write implementation code.
- Do not use GSAP

Source anchors that must survive in the plan:
- "cache hit rate"
- "37 ms"
- "before/after diff"
- "final CTA"

Shots:
1. `scene-01-hook`, 4s: introduce the problem that teams cannot see whether their new cache policy helps.
2. `scene-02-mechanism`, 6s: show a request entering cache lookup, either hitting a warm key or falling through to origin.
3. `scene-03-proof`, 5s: show the before/after diff and call out the 37 ms latency improvement plus cache hit rate.
4. `scene-04-cta`, 4s: final CTA to review the rollout checklist.

Each scene must explain why its composition choice fits and must include validation checks.
