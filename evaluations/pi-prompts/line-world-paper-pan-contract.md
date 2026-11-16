Validate the paper motion revision in this isolated workspace. Keep
`skills/line-world-video/` read-only. Use no network, live account, browser
session, sibling skills, repository documents or acceptance galleries.

Run these exact commands:

```text
uv run --script skills/line-world-video/scripts/test_paper_motion.py
uv run --script skills/line-world-video/scripts/test_paper_video.py
```

Write `review/contract.json` with `ok`, each exact command, actual exit code and
observed test count. The second suite uses its own local headless browser and
temporary PDF; this is allowed. Do not claim a Google Vids export or real paper
publication. Do not edit the copied bundle.
