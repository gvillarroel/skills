Validate the installed Google Vids adapter utilities in this isolated workspace.
Treat `skills/line-world-google-vids/` as read-only. Do not access a live browser,
network, account, sibling skill, repository document or acceptance gallery.

Run these exact commands from the workspace root and require successful exits:

```text
uv run --script skills/line-world-google-vids/scripts/test_vids_ui.py
uv run --script skills/line-world-google-vids/scripts/test_vids_delivery.py
uv run --script skills/line-world-google-vids/scripts/test_vids_batch.py
uv run --script skills/line-world-google-vids/scripts/test_vids_inventory.py
```

Write `artifacts/contract.json` with `ok: true`, the four exact command strings,
their actual exit codes, and their observed test counts. Capture subprocess
output in the workspace if needed. Do not change any copied skill file or
claim that these local tests performed a native upload, export or playback.
