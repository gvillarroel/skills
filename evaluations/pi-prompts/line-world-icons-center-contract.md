Validate the background-aware icon and alignment revision in this isolated
workspace. Keep `skills/line-world-video/` read-only. Use no network, live account,
browser session, sibling skills, repository documents or acceptance galleries.

Run these exact commands:

```text
uv run --script skills/line-world-video/scripts/test_item_contrast.py
uv run --script skills/line-world-video/scripts/test_theme.py
uv run --script skills/line-world-video/scripts/test_focus.py
```

Write `review/contract.json` with `ok`, the exact commands, observed exit codes
and actual test counts. The suites own a local headless browser; this is allowed.
Do not edit the copied skill or claim a native editor export.
