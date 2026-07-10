Use $awsome-videos.

Run the awsome-videos reference completeness audit in `outputs/`.

Run this exact command:

```bash
bash -lc 'mkdir -p outputs && uv run --script skills/awsome-videos/scripts/check_reference_completeness.py --json --output outputs/reference-completeness.json > outputs/reference-completeness-stdout.json'
```

Required outputs:

- `outputs/reference-completeness.json`
- `outputs/reference-completeness-stdout.json`

The final answer must report whether `outputs/reference-completeness.json` has `"ok": true`, list the checked group names, mention the representative image byte size, mention that `imageLinkInfo.ok`, `summaryInfo.ok`, and `consistencyInfo.ok` are true, mention `summaryInfo.contactSheet`, and mention the audio profile's `medianSilenceRatio` plus `nearContinuousAudio` values.
