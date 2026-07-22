# Source Package

Use a source package to freeze what the video is allowed to claim before any story, layout, or renderer work starts.

## Rules

- Preserve literal anchors from the prompt or inspected source: titles, IDs, URLs, filenames, constants, metrics, quotes, event names, durations, audience, style constraints, and deliverable paths.
- Treat Markdown tables as structured source facts. A table headed `Source facts`, `Facts`, `Field/Value`, or similar is not missing context; it is the primary source package input.
- Separate facts from interpretation. A fact is copied or sourced; an interpretation explains why that fact matters to the viewer.
- Do not use placeholders for provided information. If information is absent, use `null` in JSON and add a short `missingFacts` entry.
- Keep source packages local to the project or requested output path. Do not write into the skill directory during normal use or isolated validation.
- Keep routes and constraints engine-agnostic. The source package should still be useful if the renderer changes.

## Prompt Table Intake

When the prompt includes a source table, convert every non-empty row into the package before adding narrative interpretation:

1. Copy the row label into a stable fact or constraint field.
2. Copy the row value exactly, preserving filenames, constants, event names, counts, punctuation, and casing.
3. Put code identifiers, event names, filenames, and exact titles into `literalAnchors`.
4. Put route, duration, aspect, audience, style, and audio rows into `constraints`.
5. Put behavior, claim, summary, or feature rows into `facts`.
6. Leave `missingFacts` empty for fields supplied by the table.

If a source table exists, never write "No source material was supplied." Instead, use the table as the source package.

## Route Table

| Route | Use For | Required Source Facts |
| --- | --- | --- |
| `code-change` | PR, diff, commit, changelog, code walkthrough | title, summary, changed files, additions/deletions if known, touched constants/events/APIs, behavior change, audience |
| `site-or-product` | Website, product launch, app demo, landing page | URL or product name, visible claims, target user, brand constraints, pages or features to show |
| `topic-explainer` | Research, educational concept, process | claim, audience, source notes, vocabulary, caveats, examples |
| `short-motion` | Stat hit, quote, headline, lower third, kinetic type | exact text, duration, platform/aspect, brand/style, motion emphasis |
| `audio-led` | Music, narration, transcript, beat-driven clip | audio source, beat or transcript anchors, mood, required silence/caption rules |
| `footage-or-assets` | Existing media, screenshots, diagrams, logos | asset paths, ownership/status, visual role, crop/use constraints |

## JSON Shape

Use this shape unless the user provides a stricter schema:

```json
{
  "version": 1,
  "sourceId": "stable-lowercase-id",
  "route": "code-change",
  "createdFor": "one-line user request",
  "deliverables": ["storyboard.md", "shot-contract.json"],
  "constraints": {
    "durationSeconds": 24,
    "aspect": "16:9",
    "audience": "Backend engineers",
    "style": "Quiet technical diagram",
    "audio": "silent"
  },
  "facts": [
    {
      "id": "behavior",
      "value": "Workers retry transient stream disconnects up to a per-job retry budget, then write a terminal failure event.",
      "source": "user prompt",
      "useInVideo": "core causal story"
    }
  ],
  "literalAnchors": [
    "STREAM_RETRY_BUDGET",
    "stream_retry_exhausted",
    "worker.ts"
  ],
  "assets": [],
  "missingFacts": [],
  "risks": []
}
```

## Markdown Source Facts Table

When creating a Markdown plan or storyboard, put a `Source Facts` section near the top with a filled table. Include every supplied literal that will matter later:

| Field | Value |
| --- | --- |
| Title | Exact title from prompt or source |
| Route | `code-change`, `site-or-product`, `topic-explainer`, `short-motion`, `audio-led`, or `footage-or-assets` |
| Audience | Exact audience if supplied |
| Duration | Exact or recommended duration |
| Key Files/Assets | Exact filenames or asset paths |
| Constants/Events | Exact code constants, event names, metrics, or identifiers |
| Style/Audio | Exact constraints such as silent, no captions, narration, music, or brand style |

## Source Package Gate

Pass only when:

- Every supplied literal anchor appears in either `facts`, `literalAnchors`, or `constraints`.
- Every non-empty row from a prompt source table appears in the package.
- Audience, duration, aspect, style, and audio constraints are copied when supplied; they must not become `null`.
- The route matches the input source type.
- Missing information is explicit instead of hidden behind placeholders.
- The package contains no renderer dependency or implementation code.
