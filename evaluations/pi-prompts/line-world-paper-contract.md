# Bounded original-paper contract

Use only the loaded Line World Video bundle and normal tools. This is an exact
runtime contract with supplied reviewed regions, not an open-ended design task.
Keep the skill read-only and use its paper builder without restyling its output.
Download https://arxiv.org/pdf/2506.10943v2 as `paper.pdf` and prepare pages 5 and 8
under `tour/`. The paper is CC BY 4.0; preserve original colors and text.

Write `tour/story.json` from this supplied acceptance fixture:

```json
{"fps":30,"source":{"title":"Self-Adapting Language Models","authors":"Adam Zweiger, Jyothish Pari, Han Guo, Ekin Akyurek, Yoon Kim and Pulkit Agrawal","version":"2506.10943v2","url":"https://arxiv.org/abs/2506.10943v2","license":"CC BY 4.0","adaptation":"Original PDF capture plus red guide and derived bars; synthetic silent probe timing."},"scenes":[{"id":"diagram","duration":7,"script":"Silent contract probe.","layout":"paper","cameraZoom":false,"page":5,"view":[102,302,507,377],"targets":{"edit":[237,320,311,363]},"cues":[{"target":"edit","phrase":"self-edit","at":1}]},{"id":"table","duration":7,"script":"Silent contract probe.","layout":"table-stack","page":8,"view":[104,68,524,177],"targets":{"single":[259,139,282,149],"multiple":[333,139,358,149]},"chart":{"unit":"Accuracy (%) - no passage in context","columns":["1 passage - LoRA","200 documents - full tuning"],"rows":[{"id":"base","label":"Base","values":[32.7,32.7]},{"id":"passage","label":"Passage","values":[33.5,36.0]},{"id":"synthetic","label":"Synthetic","values":[39.7,50.6]},{"id":"gpt","label":"GPT-4.1","values":[46.3,59.4]},{"id":"seal","label":"SEAL","values":[47.0,58.2]}]},"cues":[{"target":"single","phrase":"single passage","at":1,"row":"seal","column":0},{"target":"multiple","phrase":"multiple passages","at":4,"row":"seal","column":1}]}]}
```

Use `paper_video.py inspect` on page 8 with `--max-chars 14000` and save its JSON
as `review/inspect.json`. Verify that the request is bounded to 12000 characters
without a failed command. Build the supplied story, then run the actual browser
audit and save its poster with `--poster review/hero.png --poster-scene table
--poster-at 5`. Preserve the exact output paths:

- `tour/index.html`
- `tour/story.json`
- `tour/timing.json`
- `review/inspect.json`
- `review/audit.json`
- `review/hero.png`
- `review/receipt.json`

Inspect the poster and report actual scene/frame counts, source preservation,
capture-mode behavior, full guide-trajectory outcome and inspection budget in
the receipt. Do not render a final MP4, operate a live editor, claim narration
synchronization or read any repository/project context outside this workspace.
