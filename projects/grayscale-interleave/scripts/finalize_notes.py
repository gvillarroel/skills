#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record accepted scoped evidence while preserving pre-existing backlog states."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
EVAL = ROOT/'evaluations/grayscale-interleave'


def main():
    result = json.loads((EVAL/'results.json').read_bytes())
    if result.get('ok') is not True or result.get('acceptedOwnerCount') != 30:
        raise ValueError('Do not finalize before all thirty current-source scoped cohorts pass')
    original = json.loads((ROOT/'projects/grayscale-interleave/artifacts/manifests/backlog-before.json').read_bytes())
    rows = []
    for owner, selected in sorted(result['selected'].items()):
        revision = selected['naturalistic'][0].split('-')[2]
        rows.append(f"| {owner} | {revision} | {selected['naturalisticPassed']}/3 | {selected['sourceFileCount']} | `{selected['normalizedPayloadSha256']}` |")
    attempts = result['attempts']
    joint = sum(row['passed'] for row in attempts)
    strict = sum(row['rawStrictGatesPassed'] for row in attempts)
    report = f'''# Colorset1 grayscale interleave validation

Date: 2026-10-05. Baseline: `daaee75353c63ed6dde204d57cfdbae6b9936586`.

## Change and coverage

Primary red remains first. The twelve neutral tokens are sorted by relative
luminance, split into equal dark/light halves, and interleaved. White and the
remaining red/pink tokens retain their suffix priority. The central definition
and thirty self-contained skill copies agree. Exact allowed tokens, named
roles, text-on-fill choices and the entire Colorset2 definition are unchanged.
Canvas filtering follows the fixed sequence. Ordered numeric ramps and source
artwork retain their separate mappings.

The neutral sequence is `#000000`, `#828282`, `#1c1c1c`, `#9c9c9c`, `#363636`,
`#b5b5b5`, `#333e48`, `#cfcfcf`, `#4f4f4f`, `#e7e7e7`, `#696969`, `#f7f7f7`.
Minimum adjacent neutral CIE lightness separation increases from 7.988 to
41.744; revised gaps range from 41.744 to 58.042. This is a scalar D65-relative
sRGB lightness comparison, not full color distance or accessibility certification.
The formula follows [W3C CSS Color 4](https://www.w3.org/TR/css-color-4/#color-conversion-code).
Filtered spatial neighbors, pale gray next to white, connectors and text still
need their own readability checks.

## Isolated forward evidence

The [frozen protocol](protocol.md), [complete results](results.json) and
[independent review](reviewer-notes.md) define the narrow palette-key scope.
All thirty owners have a current-source exact-command contract and one complete
three-run natural cohort with at least two joint strict/native passes.
There are {len(attempts)} retained reviewed attempts: {strict} pass raw strict
gates and {joint} pass all current-source and artifact gates. Older payloads and
genuine agent/artifact failures remain unaccepted. No successful repetitions are mixed across
cohorts.

The original seventeen-category cases additionally tested manual first-overflow
styling. Several failed border contrast, suffix indexing or label geometry.
The new thirteen-category prefix family directly exercises primary red plus
all twelve changed neutral positions. Its complete-label, actual-paint,
opacity, contrast, overlap, canvas and ordered-quantitative-legend checks are
unchanged. Full seventeen-token contracts and owning native capacity tests
separately protect white, remaining colors, canvas filtering and overflow.
These scoped results do not establish reliable unconstrained manual overflow
styling or recertify every media retrieval/conversion workflow.

The validator's initial string-only canvas check was an overconstraint: the
prompts leave that metadata field's type open. The explicit uniform repair
accepts an unambiguous white declaration in a string or object, while keeping
actual native white-backing and all visual gates. Original reports remain
separate. Earlier diagnostic capture passes reused screenshot filenames;
final captures are separated by review version. The immutable raw artifacts,
strict results and prior JSON reviews remain retained. Final supplemental
checks cover exact quantitative indexes, positive in-stage swatch geometry
and label association. A second contract overconstraint compared complete owner
definitions with the shorter central definition, rejecting the vectorization
bundle's preserved artwork extensions. The uniform repair requires an exact
export of the copied owner's full definition and equality of every central
canonical field; missing canonical fields still fail. Baseline comparisons
independently preserve all owner extensions. The protocol and independent review record all repairs
and binding hashes; no model cohort is rerun for a schema-only correction.

The fresh Spark availability probe failed before tools because the ChatGPT
account does not support `gpt-5.3-codex-spark`. The recorded scoped model
exception is `openai-codex/gpt-5.6-luna`. Runs use `pi --mode json --strict`,
exact expected paths, prompt-first/event/read-surface gates and immutable
runtime-only copies under `evaluations/runs/`. The collector binds raw gates,
prompt hashes, output hashes, native observations and every normalized source
filename/byte. `bind_release_payload.py` independently binds those inventories
to staged and committed Git blobs.
The release binder reads immutable Git objects in one batch. For the unchanged
Vue template, it additionally proves Git LF bytes equal the validated CRLF
checkout after only newline conversion, recording both hashes. That format was
absent from the original runtime normalizer; all other bytes and filenames
remain exact under the recorded profile.

| Skill | Natural cohort | Joint passes | Runtime files | Normalized runtime SHA-256 |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Native renderers and publication

Native evidence is summarized in [SVG-family validation](svg-native-summary.md),
[renderer validation](renderer-native-summary.md), and the separate
[primary-logo assessment](primary-logo-validation.md). Actual automatic
allocators and embedded registries were tested beyond JSON equality. Native
checks cover both palettes, finite capacity/canvas boundaries, visible text,
motion/replay, export states and protected numeric mappings where applicable.

The vectorization fixtures retain their source geometry and paint byte-for-byte
after removing refreshed metadata. Procedural fixture geometry is unchanged;
two text-ink switch times adjust to the changed substrate luminance. The
inference composition fixture needed a narrow slot/route correction before
its new native audit passed. Mermaid C4 retains its qualified baseline source
and outputs after an attempted regeneration reduced readability; its existing
caption contact is recorded in the renderer note. No universal claim that
every historical gallery is free of layout defects is made.

The two pre-existing ECharts gallery drafts are preserved outside the commit.
The isolated committed gallery candidate changed only a non-drawing timestamp;
its qualified Colorset2 baseline is retained. Historical evaluations remain
unchanged. Source publication uses explicit owned paths, the Pages build,
exact-commit deployment workflow, and committed-builder byte verification.

Required repository gates passed: `validate-pattern-ids.py`,
`validate-skills.py`, `test-skill-independence.py`, `check-repo-payload.py`,
`validate-colorsets.py` (34 skills, 30 copies, 672 artifacts, no findings),
`test-colorsets.py` (19 tests), and `test-pages-output.py` (3 tests).
`build-pages.py` and local skill synchronization/check also passed. Runtime
behavior commands are retained in the owning summaries and run manifests.

The scoped revision restores each owner's previous backlog state, preserving
broader pre-existing `validating` states instead of claiming those independent
capabilities are newly done.
'''
    (EVAL/'validation.md').write_text(report, encoding='utf-8')
    backlog_path = ROOT/'SKILLS.md'
    backlog = backlog_path.read_text(encoding='utf-8')
    old = 'Grayscale interleave revision 2026-10-05: validating the categorical dark/middle alternation with unchanged tokens, roles, text choices, Colorset2 and quantitative ramps.'
    new = 'Grayscale interleave revision 2026-10-05: the scoped categorical dark/middle alternation passes current-source strict/native contract and whole-cohort forward checks; tokens, roles, text choices, Colorset2 and quantitative ramps are unchanged.'
    lines = []
    for line in backlog.splitlines():
        if line.startswith('| '):
            cells = line.split('|')
            owner = cells[1].strip()
            if owner in original:
                cells[2] = f" `{original[owner]}` "
                line = '|'.join(cells).replace(old, new)
                line = line.replace('[Frozen protocol and scope](evaluations/grayscale-interleave/protocol.md).', '[Scope, evidence and limits](evaluations/grayscale-interleave/validation.md).')
        lines.append(line)
    backlog = '\n'.join(lines)+'\n'
    recent = '\n- Colorset1 grayscale interleave, 2026-10-05: primary red, twelve dark/middle neutral alternations, white, then remaining colors. Thirty isolated runtime owners pass scoped current-source contracts and whole natural cohorts; native allocators preserve both palette boundaries and ordered scalar mappings. Complete attempted evidence, model exception, source binding, readable fixture decisions and publication checks are in [the validation record](evaluations/grayscale-interleave/validation.md).\n'
    marker = '## Recent Validation Notes'
    if recent.strip() not in backlog:
        if marker in backlog:
            backlog = backlog.replace(marker, marker+'\n'+recent, 1)
        else:
            backlog += recent
    backlog_path.write_text(backlog, encoding='utf-8')
    colorsets_path = ROOT/'docs/colorsets.md'
    colorsets = colorsets_path.read_text(encoding='utf-8')
    needle = 'Run:\n\n```powershell'
    replacement = 'The [grayscale interleave revision](../evaluations/grayscale-interleave/validation.md) records the current categorical order, protected numeric ramps, current-source isolated checks and native rendering evidence. Run:\n\n```powershell'
    if needle not in colorsets:
        raise ValueError('Missing colorset validation command anchor')
    if '[grayscale interleave revision](../evaluations/grayscale-interleave/validation.md)' not in colorsets:
        colorsets_path.write_text(colorsets.replace(needle, replacement, 1), encoding='utf-8')
    print(json.dumps({'ok': True, 'ownerCount': 30, 'attempts': len(attempts), 'jointPassed': joint, 'strictPassed': strict}))


if __name__ == '__main__':
    main()
