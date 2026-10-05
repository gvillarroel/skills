# Colorset1 grayscale interleave publication

Date: 2026-10-05. The source release is published and verified.

- Source commit: `c76c348fb6fd58079f76ba030bb475f76722b58f`.
- Baseline: `daaee75353c63ed6dde204d57cfdbae6b9936586`.
- Exact successful [Pages workflow](https://github.com/gvillarroel/skills/actions/runs/37301592826).
- Public [example catalog](https://gvillarroel.github.io/skills/).
- Result: 679 checked public resources, zero HTTP-byte findings and zero
  artifact/source findings. These comprise 648 Pages resources and 31 canonical
  palette definitions fetched through exact-commit GitHub raw URLs. Canonical
  palette definitions are source checks, not files served by Pages.

Static expectations replay the committed Pages builder's transformations from
the exact Git blobs. Compiled Slidev and ThreeJS expectations come from the
artifact of the explicitly named, SHA-matched successful workflow. All served
bytes match those expectations. The downloaded archive's SHA-256 equals the
GitHub API artifact digest.
The workflow artifact ID is `11341038306` and contains 648 files.

| Provenance | SHA-256 |
| --- | --- |
| Workflow archive and API artifact digest | `c005547fa08b177dd89e31c0131490d84194cacee2bcf3794182bb64251a4dbc` |
| Committed Pages builder | `40e8c100cba494ee5dca472bb640821cb3d64135b5ac48bc552ca391f28a11f7` |
| Publication verifier | `23fae3b71f79d14728ecc567c3aaca8ff91ad2f8ce385bb25751ffec185afe78` |
| Full publication report | `5f595df7ad78c848b1ad23ce154fa7cbe7e480ba442ff0423276e925a4791dbe` |
| Committed Pages workflow | `37c268e19f920ab3e1f6d64abe1892ed67702397a9dc943b428b2faeac685b6f` |

The committed runtime inventory binding separately passes for all thirty
accepted owners. It compares every filename and content digest under the
recorded runtime normalization profile. One unchanged `SvgAssetSlide.vue`
template has a documented transport-only newline difference: Git LF bytes
exactly equal the validated Windows checkout after CRLF-to-LF conversion.
Both hashes are retained; other content changes are rejected. This exception
was independently reviewed before release.

## Reproduction and retained evidence

```powershell
uv run --script projects/grayscale-interleave/scripts/bind_release_payload.py --ref c76c348fb6fd58079f76ba030bb475f76722b58f --report projects/grayscale-interleave/artifacts/manifests/committed-payload.json
uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --expected-ref c76c348fb6fd58079f76ba030bb475f76722b58f --base-ref daaee75353c63ed6dde204d57cfdbae6b9936586 --workflow-run 37301592826 --output-dir projects/grayscale-interleave/artifacts/reviews/publication-release
```

The full publication report and downloaded artifact are retained locally under
`projects/grayscale-interleave/artifacts/reviews/publication-release/`;
`publication.json` binds each URL, expected hash and observed hash. The
committed-payload report is retained under the command's exact output path.
Bulky evidence stays outside git. The [validation record](validation.md),
[frozen protocol](protocol.md), [results](results.json) and
[independent review](reviewer-notes.md) retain the accepted behavior and scope.

The documentation follow-up adds this publication record and its links without
changing any accepted skill runtime or published example source.
