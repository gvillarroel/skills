# AI Concept Videos

Private production scripts for the AI concept video series. The public, reusable scene fixture remains in `.agents/skills/html-d3-anime-video-workflow/assets/examples/ai-concept-videos/`.

Run from the repository root:

```powershell
node videos/ai-concept-videos/scripts/validate-concepts.mjs
node videos/ai-concept-videos/scripts/render-videos.mjs --preset fast --concept 01-what-is-an-llm --start 36 --duration 30
node videos/ai-concept-videos/scripts/review-videos.mjs --root output/ai-concept-videos/final
```

The renderer accepts concept IDs from the fixture data model, such as `01-what-is-an-llm`, `02-llm-billing`, and `03-probabilities-and-evaluation`.
