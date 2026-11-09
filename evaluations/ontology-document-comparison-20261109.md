# Reviewed document comparison validation

The repository skill can now compile reviewed before and after
observations and compare reviewed typed snapshots. The command binds
line evidence to its revision and computes the structural result.
An optional reviewed class correspondence is bound to the exact
bytes of both sources and the snapshot-pair artifact.

The published skill lacked this deterministic subset of the local
document comparison workflow. The port keeps the existing model
validation, conflict review and Draft 7 tools. It reuses the
bundle's JSON and exclusive output helpers. Exact-decimal parsing is
enabled for the new comparison inputs. Existing callers retain their
default parser behavior.

## Qualification

Two isolated GPT-6 Luna low calls compiled a reviewed conditional
observation with exact source-line evidence. Two further calls
compared a reviewed class rename and cardinality change. All four
passed strict execution, used the bundled command, and preserved the
supplied inputs. Each pair wrote byte-identical output.

The first implementation needed a second shell call on both snapshot
trials because uv did not include the adjacent script modules on the
Python path in that process. The tested release resolves those modules
from the bundle and succeeds on the first call. A precision-loss
control rejects a decimal that would otherwise round to the same
value as its comparison counterpart. The new path also rejects
duplicate JSON keys, invalid evidence, stale class-identity digests,
overlapping observation ranges and input overwrite attempts.

The scope is reviewed typed inputs. The compiler verifies structure
and line identity. A reviewer still decides whether the source
supports the value, which context governs it, and whether a proposed
class correspondence is semantically valid. The release does not
apply the earlier document-diff prompt candidate that failed its
semantic development gate.

~~~text
uv run --no-project --python 3.14 python -B -m unittest discover -s skills/curate-semantic-model/scripts -p "test_*.py"
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
~~~
