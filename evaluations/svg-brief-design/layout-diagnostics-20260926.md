# Auxiliary SVG layout diagnostics — 2026-09-26

This development-only audit adds independent layout observations without changing
the frozen visual-similarity reward, selecting a candidate, or opening private
validation or holdout data. It made no model calls and changed no skill bundle.
The diagnostic is evaluator-owned and is not shipped inside the skill.

Current version: **1.0.1**. A CSS regression was found and repaired after the
initial four-case audit. The original script bytes, original receipts and label
JSONs remain preserved. Both label inputs were re-evaluated with 1.0.1; their
numeric diagnostic conclusions are unchanged.

## CSS removal regression and repair

The fifth synthetic fixture adds `text { display:block !important }` plus an
inline important display declaration to two separated text elements. Version
1.0.0 falsely reported complete text overlap and zero observable ink because its
ordinary `display:none` intervention was overridden. The
[failure receipt](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/css-regression-v1.0.0.json)
preserves the exact fixture, input digest, failed assertion and renderer output.
The original [1.0.0 script bytes](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/diagnose_svg_layout-v1.0.0.py)
retain their original digest.

Appending inline `display:none!important` was also insufficient in this pinned
renderer, including after normalizing declaration syntax. Version 1.0.1 retains
that explicit override and replaces each removed drawable with an inert empty
SVG group. This guarantees removal for the tested override case and retains the
node's sibling position. It does change element type and removes attributes and
descendants, so selectors depending on those properties can alter unrelated
elements; the script explicitly reports this limitation. It does not implement
a general CSS engine or claim arbitrary selector compatibility.

The [fresh five-case receipt](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/self-test-v1.0.1.json)
records exit code 0 at 09:42:35 UTC. The updated
[original-label diagnostic](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/label-0-v1.0.1.json)
and
[candidate-label diagnostic](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/label-1-v1.0.1.json)
both retain their earlier text-ink fractions and overflow results.

| Current artifact | SHA-256 |
| --- | --- |
| Diagnostic script 1.0.1 | `c6aa02ee748f5a590e0a5b8881750b41719036948f213222dba20131358015b8` |
| Original diagnostic JSON 1.0.1 | `a2873b8da91f532aebb0971ab06fd5d3a58d5e363873343f1df393ed9d05cc4d` |
| Candidate diagnostic JSON 1.0.1 | `6e06db40ac2b9b0f5dca0feb35dd644d5b38111ee657ccc1fbd25ee5c43dafda` |

## Method and observed evidence

[diagnose_svg_layout.py](../../projects/svg-brief-design/scripts/diagnose_svg_layout.py)
renders generated SVGs using the existing verifier image and DejaVu fonts. It
measures actual glyph-ink intersections between separately rendered text
elements. It also compares the complete scene with each text removed to measure
the fraction of text ink that makes an observable difference. Finally, a
64-pixel expanded viewport detects nearby ink outside the original viewBox,
with a one-pixel edge tolerance. It neither reads reference art nor computes a
new reward.

The pre-existing development comparison for `vector-021` showed text crossing
barcode ink in the original-guide output and separated text in the candidate.
The independent diagnostic corroborated that difference:

| Existing output | Frozen visual similarity | Observable text ink | Ink beyond viewBox |
| --- | ---: | ---: | ---: |
| Original guide | 0.6614415359568970 | 0.7173507462686567 | 0 pixels |
| Mechanics candidate | 0.6147248837657242 | 1.0000000000000000 | 0 pixels |

Both contain one actual SVG text element, so neither has a text-to-text
intersection. The lower original value reflects its interaction with non-text
artwork. This is one post hoc developmental observation, not a general legibility
score, an independent test set, or a reason to override the frozen selection.

The preserved version 1.0.0 local outputs are
[label-0.json](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/label-0.json)
and
[label-1.json](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/label-1.json).

| Artifact | SHA-256 |
| --- | --- |
| Diagnostic script 1.0.0 snapshot | `22afd9f03f718dd3b1283cf362d5995cfc11a77e1c1f80c545b63db67d6b50fd` |
| Original diagnostic JSON 1.0.0 | `50b37ec202979acc5fd84ec6e974044f2b2614acf7263f7923117b22ec935057` |
| Candidate diagnostic JSON 1.0.0 | `c7c1c78988cc3036b80547383546bc8d93db4d31f1efb10ea18804da4d3c251e` |
| Original generated SVG | `a9cb02379fce2db10f45f36a542ca7245830c034c3116001cffa0a9256cc761f` |
| Candidate generated SVG | `80e39c1fa343688edb7e6c73d3fce72532379863bd6c9aec221453399113a64a` |

## Reproduction and retained test evidence

Run from `C:\Users\villa\dev\skills`. The following uses the immutable image ID,
disables networking, and mounts the repository read-only. The five synthetic
cases are built into `--self-test`; they require no generated fixtures or models.

```powershell
wsl -d Ubuntu --exec docker run --rm --network none --mount type=bind,source=/mnt/c/Users/villa/dev/skills,target=/repo,readonly sha256:f82f3a08d40b954417f8040d05f71213824906e312f477ac7ba0370e6b6427f7 python /repo/projects/svg-brief-design/scripts/diagnose_svg_layout.py --self-test
```

The original [four-case self-test receipt](../../projects/svg-brief-design/artifacts/reviews/layout-audit-20260926/self-test.json)
records exit code 0 at 09:38:29 UTC, script and image hashes, command, output, and
four assertions: colliding text is detected; separated text is observable and
does not overlap or overflow; a rectangle crossing the viewport is detected;
text fully covered by later artwork has zero observable ink. This receipt is a
successful repeat of the earlier successful four-case run, preserving the
original evidence rather than replacing any prior record. The current command
executes five cases and corresponds to the separate 1.0.1 receipt above.

Reproduce the two real-output diagnostics on stdout, without overwriting the
retained JSON files:

```powershell
$study = 'evaluations/runs/svg-brief-design-mechanics-20260925'
$manifest = Get-Content -LiteralPath "$study/review-development-pool/manifest.json" -Raw | ConvertFrom-Json
$row = $manifest | Where-Object task -EQ 'vector-021--efc288119a85154c'
foreach ($attempt in $row.attempts) {
    $trial = Split-Path -Parent "$study/$($attempt.native_result)"
    $svg = Get-ChildItem -LiteralPath "$trial/artifacts" -Filter '*.svg' -Recurse | Select-Object -First 1
    $inputRel = $svg.FullName.Substring((Get-Location).Path.Length + 1).Replace('\', '/')
    wsl -d Ubuntu --exec docker run --rm --network none --mount type=bind,source=/mnt/c/Users/villa/dev/skills,target=/repo,readonly sha256:f82f3a08d40b954417f8040d05f71213824906e312f477ac7ba0370e6b6427f7 python /repo/projects/svg-brief-design/scripts/diagnose_svg_layout.py "/repo/$inputRel"
}
```

These additional commands passed during the audit:

```powershell
uv run python -m py_compile projects/svg-brief-design/scripts/diagnose_svg_layout.py
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
```

## Sources and interpretation limits

The audit read the existing verifier at
`C:\Users\villa\OneDrive\Documentos\ChatGPT\personal\output\fox-vector-benchmark-v1\scripts\compare_svg_v1_1.py`,
the current skill, and only the completed development galleries and manifests:

- [General-instructions development gallery](../runs/svg-brief-design-gepa-20260925/review-development-pool/development.jpg).
- [Mechanics development gallery](../runs/svg-brief-design-mechanics-20260925/review-development-pool/development.jpg).
- [Mechanics output-to-trial manifest](../runs/svg-brief-design-mechanics-20260925/review-development-pool/manifest.json).

Verifier 1.1.0 crops and centers the foreground before comparison. Its final
score combines shape and style proxies, and explicitly reports semantic
adherence as unavailable. Therefore margins, intended placement, label
legibility, diagram meaning, and code decodability need separate checks. This
audit does not modify that established metric.

The added diagnostic has corresponding limits:

- Intentional overlap and bleed require human review. Observations are not automatic failures.
- Text outlines and `<use>`-instanced text are not classified as text.
- Inert-group intervention preserves sibling positions but can change selectors depending on removed node types, IDs, attributes or descendants. Outputs using these structural selectors need a separate review.
- Observable ink is a rendering intervention, not a calibrated perceptual legibility or accessibility score. Duplicate lettering can yield low values even when visible.
- Percentage-based coordinates, viewport units, filters, and nested viewports can change when the viewBox expands. Only nearby overflow is inspected.
- Existing clip paths remain active, so clipping inside them is not diagnosed.
- Spelling, factual diagram relationships, subject identity, and machine-readable code validity remain unmeasured.
- The retained files under ignored local artifact/run directories are local evidence, not portable public assets. No purchased artwork is added to the skill or this report.
