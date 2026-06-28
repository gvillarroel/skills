# Storyboard And Shot Contract

Create the storyboard and shot contract after the source package is stable. The storyboard explains the viewer experience; the shot contract gives a renderer enough structure to build without reinterpreting the source.

## Storyboard Structure

Use this order for `storyboard.md`:

1. `# <Project Title>`
2. `## Source Facts` with a filled table copied from the source package.
3. `## Narrative Angle` with one sentence stating the viewer takeaway.
4. `## Shot List` with one subsection per shot.
5. `## Validation Anchors` listing the literal strings that must appear in artifacts or rendered inspection notes.

Each shot subsection should include:

- `Duration`: seconds or time range.
- `Purpose`: what changes in the viewer's understanding.
- `Source facts used`: fact IDs or exact anchors.
- `Visual frame`: the static hero layout at maximum clarity.
- `Motion intent`: semantic verbs such as reveal, scan, compare, accumulate, route, branch, retry, exhaust, converge, isolate, rank, transform, highlight, hold, or handoff.
- `Media`: assets, narration, captions, music, or `none`.
- `Validation`: what to inspect before render.

## Shot Contract JSON

Use this shape for `shot-contract.json`:

```json
{
  "version": 1,
  "sourcePackage": "source-package.json",
  "durationSeconds": 24,
  "aspect": "16:9",
  "rendering": {
    "engine": "unspecified",
    "seekDeterministic": true,
    "forbiddenDependencies": ["gsap"]
  },
  "shots": [
    {
      "id": "s01",
      "start": 0,
      "duration": 6,
      "purpose": "Introduce the failed stream disconnect problem.",
      "sourceAnchors": ["worker.ts"],
      "visual": {
        "heroFrame": "Worker, stream, and disconnect marker visible at once.",
        "roles": ["worker", "stream", "disconnect", "retry budget"]
      },
      "motionIntent": [
        {
          "verb": "scan",
          "subject": "stream",
          "target": "disconnect marker",
          "timing": "0.5-2.5s"
        }
      ],
      "media": {
        "narration": null,
        "music": null,
        "captions": false,
        "assets": []
      },
      "validation": ["worker.ts is represented", "no placeholder labels"]
    }
  ],
  "literalAnchors": ["worker.ts"],
  "missingFacts": []
}
```

## Engine-Agnostic Motion

- Name motion by the viewer-visible transformation, not by a library API.
- Define final visual states before transitions.
- Use timestamps, durations, and semantic state changes. Avoid timeline snippets, easing APIs, plugins, framework imports, or runtime-specific lifecycle instructions.
- Prefer small repeated motion verbs over one-off prose that a builder cannot validate.
- If a later renderer needs implementation code, hand off to the relevant renderer skill after this contract exists.

## Contract Gate

Pass only when:

- The storyboard and JSON agree on shot count, duration, route, and literal anchors.
- The storyboard `Source Facts` table preserves the important source-package literals instead of replacing them with generic intake notes.
- Supplied audience, duration, aspect, style, and audio constraints appear in the storyboard table and shot contract metadata.
- Every shot cites at least one source fact or explains why it is structural.
- Every shot has a static hero frame and motion intent.
- Media needs are explicit, including silence and no-caption constraints.
- No placeholder text remains.
- No forbidden animation dependency appears in the artifacts.
