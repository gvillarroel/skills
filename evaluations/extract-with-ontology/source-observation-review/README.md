# Source observations and citation repair

On November 10, 2026, this study tested whether a reader with access
only to source windows could catch an ontology assertion that borrowed
the identity of an unnamed subject from the claim. It follows the
[strict Power Automate replay](../../ontology-context-routing-20261110.md#candidate-verification-instruction).
The split between source reading and claim review draws on independent
verification and evidence-level assessment. [Chain-of-Verification](https://aclanthology.org/2024.findings-acl.212/) ·
[WiCE](https://aclanthology.org/2023.emnlp-main.470/)

## Frozen comparison

The [fixture](fixtures.json) identifies seven source files pinned by
commit and SHA-256 across Power Automate, PostgreSQL, Compose, CPython,
and GitHub REST documentation. Ten packets contain 33 public
development assertions. The answer key has 14 supported assertions,
nine contradictions, and ten unresolved assertions. It includes both
unnamed subjects that legitimately support an anonymous assertion and
nearby named subjects that lack a sufficient source connection.

The harness creates a prompt input and a local answer key. The first
reading receives only opaque packet IDs and source windows. It extracts
literal subject and assertion spans and identifies unresolved references.
The verifier checks that each quotation occurs in its packet and records
the exact offsets. The second reading either sees the full windows with
the observations as guidance or sees only admitted observations and
selects their IDs as evidence. Each request uses GPT-6 Luna low through
the Pi 1.4.0 SDK with fresh messages, zero retries, and no tools.

| Review method | Batch A exact | Batch B exact | Total exact | Correct verdict |
| --- | ---: | ---: | ---: | ---: |
| Direct review of windows | 14/16 | 12/17 | 26/33 | 32/33 |
| Direct review with observations as guidance | 14/16 | 12/17 | 26/33 | 32/33 |
| Review limited to admitted observations | 14/16 | 4/17 | 18/33 | 20/33 |
| Direct review, independent reversed-order repeat | 14/16 | 12/17 | 26/33 | 32/33 |
| Restricted review, independent reversed-order repeat | 6/16 | 9/17 | 15/33 | 16/33 |

Exact credit requires both the correct verdict and one complete
permitted window set. Direct review repeated all 33 verdict and
window selections. Restricted review repeated 17/33. The direct arm
left all ten assertions with insufficient evidence unresolved in both
attempts.
Its main errors were incomplete citation sets for claims with a
separate source of subject or scope.

## Format and provenance follow-ups

The initial reader omitted an empty context array from every
observation in batch B and from the reversed batch A. The frozen
strict parser excluded those observations. A format-only adapter
restored 24/25 and 18/18 observations respectively. The one remaining
batch B observation failed literal quotation validation.

With the recovered observations, the restricted reviewer scored
16/16 on batch A. Its batch B reply omitted the empty question in
eleven closed decisions, so the original output contract rejected the
reply. An offline adapter supplied only those empty fields. That
diagnostic scored 14/17 exact and 15/17 verdicts in batch B. The two
format-recovery diagnostics cover 30/33 exact decisions and 31/33
correct verdicts. They use different retained reader repetitions and
the known format corrections. The original strict outcomes remain in
the table.

Adding source document IDs and line ranges to the full windows
raised the direct batch B verdict score from 16/17 to 17/17.
Its exact score stayed at 12/17. The model identified the Power
Automate operation from the surrounding passage and selected only
the provider sentence. The restricted reviewer with this provenance
scored 12/17 exact and 14/17 verdicts. [Pinned Power Automate source](https://github.com/MicrosoftDocs/power-automate-docs/blob/e7a4c26faaa37ea3432ea7011957f3e72af745c1/articles/create-cloud-flow-using-copilot.md#L23-L38)

## Archived Pi decisions

A source-only reader inspected the original Power Automate packets
without the saved Pi decisions. An offline check withheld a positive
decision when the observations contained in its selected citations all
left the subject unnamed. The check changed the one previously
unsupported approval and preserved all six control decisions.
The isolated arm rose from 3/4 to 4/4 and the contextual arm stayed
at 4/4. The combined archived replay moved from 7/8 to 8/8.

The same check preserved the 33 original direct decisions. Three
injected approvals for named subjects from unnamed-source packets
were all withheld. Applied to the batch B run with document IDs,
the check withheld the true Power Automate claim because its
selected citation omitted the available antecedent. This exposes
the need to repair a citation before treating the claim as unresolved.
The replay uses known development cases and fixed old decisions.

## Focused reference reading

The [reference cases](referent-fixture.json) ask for a specific
subject, API name, parameter, or configuration scope using a focal
quote. The reader receives no proposed assertions. Six cases
include a relevant antecedent and six lack it. The method
resolved four of six present antecedents and left all six absent
ones open. It missed the Power Automate operation and the
PostgreSQL parameter.

An offline citation repair then matched those verified quotations
to retained decisions by document, line range, and the supplied
subject aliases. It added six of the seven missing evidence
windows in a replay of the original batch A and the
document-aware batch B. Exact decisions rose from 26/33 to 32/33.
The remaining case is Power Automate. The repair was designed
after inspecting the incomplete decisions.

A further variant added a contiguous window to six eligible
packets. It used at most twelve intervening lines and 1,600
characters, skipped new section boundaries, and used text inside
the original same-document extent. The reader resolved 11/12
cases with the expanded text. Two quoted bindings crossed the
original excerpt boundaries. Requiring exact projection into
those excerpts yielded 9/12 and repaired five missing citations.
The Power Automate operation still lacked a binding.

The original harness and follow-up checks passed 16 tests on
Python 3.11 and 3.14. Ten further mechanical controls exercised
exact binding, missing references, document and section boundaries,
and context limits. The aggregate receipt reproduced
byte-for-byte on both Python versions. A clean fetch from the
published fixture reproduced the original frozen inputs. The
26 model requests all returned from GPT-6 Luna low. The SDK
reported 86,492 tokens and an estimated USD 0.02327.

## Reproduction

Copy this directory into an ignored run workspace before fetching
the pinned sources or saving model replies. For the main comparison,
set the package path to an installed Pi 1.4.0 SDK with configured
GitHub Copilot access. This prepares and verifies the public inputs.

~~~powershell
python -X utf8 -B study.py prepare run-01 --fetch
python -X utf8 -B -m unittest test_study
$pi = Join-Path ((npm root -g).Trim()) '@earendil-works/pi-coding-agent'
$modes = @('direct','observe','advisory','restricted','direct-repeat','observe-repeat','restricted-repeat')
foreach ($batch in @('a','b')) {
  foreach ($mode in $modes) {
    python -X utf8 -B study.py run run-01 $batch $mode $pi
    if ($LASTEXITCODE -ne 0) { throw "Evaluation stage failed for $batch $mode" }
  }
}
~~~

The format and source-position comparisons use the same cases and
the stored first-stage replies where applicable. The historical
command requires the exact local Pi receipts from the linked
earlier study. The raw model outputs and history receipts stay in
the local run workspace.

~~~powershell
python -X utf8 -B follow_up.py format run-01 run-02-format-a-repeat a observe-repeat
python -X utf8 -B follow_up.py format run-01 run-02-format-b b observe
python -X utf8 -B follow_up.py format run-01 run-02-format-b-repeat b observe-repeat
python -X utf8 -B study.py run run-02-format-a-repeat a restricted $pi
python -X utf8 -B study.py run run-02-format-b b advisory $pi
python -X utf8 -B study.py run run-02-format-b b restricted $pi
python -X utf8 -B follow_up.py positions run-01 run-02-positions
python -X utf8 -B study.py run run-02-positions b direct $pi
python -X utf8 -B study.py run run-02-positions b observe $pi
python -X utf8 -B follow_up.py format run-02-positions run-02-positions-adapted b observe
python -X utf8 -B study.py run run-02-positions-adapted b restricted $pi
~~~

~~~powershell
python -X utf8 -B follow_up.py history run-02-history
python -X utf8 -B study.py run run-02-history a observe $pi
python -X utf8 -B study.py run run-02-history b observe $pi
python -X utf8 -B follow_up.py replay-history run-02-history
python -X utf8 -B -m unittest test_study test_follow_up
python -X utf8 -B summarize.py summary.json
~~~

~~~powershell
python -X utf8 -B referent_probe.py prepare referents-01
python -X utf8 -B referent_probe.py run referents-01 a $pi
python -X utf8 -B referent_probe.py run referents-01 b $pi
python -X utf8 -B referent_probe.py summarize referents-01
python -X utf8 -B bridge_probe.py prepare referents-01 referents-bridge
python -X utf8 -B referent_probe.py run referents-bridge a $pi
python -X utf8 -B referent_probe.py run referents-bridge b $pi
python -X utf8 -B bridge_probe.py project referents-01 referents-bridge referents-bridge-projected
~~~

## Receipts

| Recorded artifact | SHA-256 |
| --- | --- |
| Original two-batch evaluation freeze | affdf7ab03715d196565b65f67ba3612ae9482ed07ae175b319520dac8dd69dc |
| Two-batch results and archived-decision summary | 5ec1cae20af6eb6b75741d34568a2f72cbc17d620db5fba2701d5092beabc360 |
| Archived Pi replay receipt | c7a2c6f46d6e450aad76967e234643174aa419413fa7d384c25deb8d4d901a52 |
| Focused reference evaluation freeze | b3c3f1ef83ee320d623629bc680e76cbe742301813d788f315685542435fa951 |
| Focused reference results and citation replay | a5504e4733d79e087a7adb3b18802d0cffdf85e9505766cd30dd86dd89d2e248 |
| Contiguous-window evaluation freeze | b5ca210478da3a96d95766a95674e5105e65bfecc292fd5b8a85af9f0175e9c5 |
| Contiguous-window projected results | 761c618f5a39164e4075e49155362a2e84659f0fb84095aa60b04bda2f8d5617 |
