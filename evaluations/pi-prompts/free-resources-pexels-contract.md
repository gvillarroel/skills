# Pexels access contract

Treat `skills/pexels-media-search/` as read-only. This workspace has no Pexels
API key. Do not create an account or search for credentials. Run exactly:

```sh
uv run --script skills/pexels-media-search/scripts/pexels.py status --out artifacts/access.json
```

Run the bundled offline Pexels tests as an additional contract check. Write
`artifacts/review.md` explaining which integration behavior can be validated
without a real key and which live behavior remains untested. Required outputs:
`artifacts/access.json`, `artifacts/review.md`. Do not invent media candidates.
