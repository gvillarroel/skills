# Vectorize Art Patterns release validation — 2026-09-02

## Decision

Keep the skill at `validating`. Deterministic implementation checks, rights
boundaries, the contract case, the naturalistic case threshold, and every
independently inspected SVG artifact pass. The current payload still needs two
fresh strict generalization passes after Spark capacity returns because two of
the three otherwise-valid generalization repetitions were invalidated by the
old launcher probing a nonexistent `README.md`.

This is an infrastructure-limited release decision, not evidence of a current
artifact defect.

## Local deterministic gates

- `test_vectorize_art.py`: pass across four modes and two colorsets, including
  deterministic output, rights rejection, and bundled-asset integrity.
- `test_vectorize_with_vtracer.py`: pass with nine paths, geometry locking,
  deterministic output, and restricted-rights rejection.
- `validate_open_assets.py`: pass for all 35 bundled open assets.
- Current guidance explicitly prohibits `--require-pattern` when `--tile none`
  is requested; this removes the only ambiguity found in the generalization
  workflow.

## Isolated Spark evidence

| Cohort | Fixed payload | Strict result | Independent artifact result | Interpretation |
| --- | --- | --- | --- | --- |
| Contract | `77d3dc6a5ab536fd3f5c2bb142b9eef314b40050e0fc66dadecbea00aad40113` | 1/1 pass (`contract-spark-2`) | pass | contract threshold met |
| Naturalistic | `77d3dc6a5ab536fd3f5c2bb142b9eef314b40050e0fc66dadecbea00aad40113` | 2/3 pass (`naturalistic-spark-1`, `-3`) | 3/3 artifacts valid | repetition 2 used one wrong report filename, corrected it in-run, and is classified `agent` |
| Generalization | `4493eb12c57522fc50bc56d6a21920da320053b342bed25fef0bfc511de07a70` | 1/3 pass (`generalization-spark-7`) | 3/3 artifacts valid | repetitions 8 and 9 failed only the pre-fix harness read gate after probing absent `README.md` |
| Rights boundary | `77d3dc6a5ab536fd3f5c2bb142b9eef314b40050e0fc66dadecbea00aad40113` | 3/3 pass (`boundary-spark-1..3`) | 3/3 correct refusal records | safety threshold met |

The shared launcher was then corrected to name the exact
`skills/<name>/SKILL.md` entry point. Fresh runs against current payload
`4493eb12c57522fc50bc56d6a21920da320053b342bed25fef0bfc511de07a70`
(`contract-spark-4`, `naturalistic-spark-5`, `generalization-spark-11`, and
`boundary-spark-5`) all stopped before the first tool call with
`Codex error: The usage limit has been reached`. Each used zero tokens, made
zero tool calls, created no task artifact, and preserved the copied payload.
Classification: `infrastructure`. These attempts count as neither passes nor
skill failures.

## Independent SVG inspection

The three current generalization artifacts are byte-identical and pass the
evaluator-owned validator:

- SHA-256 `b68685c0aa124107ff780a497abbb753a9189cc99d4b641b844240d1efec729c`
- `pattern_id=biomorphic-user-owned`, `mode=organic`, `tile=none`
- five paths, 360 path commands, six visible source-derived colors
- no raster image, script, pattern wrapper, or external reference
- `rights_basis=user-owned`, `license=User-authorized`

The passing naturalistic artifact is an ink/mirror composition with one base
path, 236 commands, one pattern element, four uses, no raster or script, and a
Public Domain source declaration. Chromium screenshots of both the biomorphic
generalization and the mirrored ink composition were inspected directly and
show complete, nonblank, coherent artwork.

## Durable traces

Successful strict read-surface summaries are stored beside this report for the
contract, naturalistic repetitions 1 and 3, generalization repetition 7, and
all three rights-boundary repetitions. Bulky job folders remain under the
ignored `evaluations/runs/` tree.

## Required release follow-up

After Spark capacity resets, rerun the current generalization prompt three
times with the corrected launcher and unchanged payload. Promote only if at
least two of the three runs pass every strict gate and their evaluator-owned
artifact checks remain clean.
