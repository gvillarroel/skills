#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Reserve an untouched cohort for a new one-candidate research experiment."""
import hashlib
import json
from pathlib import Path
import shutil

from seal_technique_evolution import REPO, main as seal, sha, write


def tree(path):
    digest = hashlib.sha256()
    for file in sorted(path.rglob('*')):
        if file.is_file():
            digest.update(file.relative_to(path).as_posix().encode())
            digest.update(b'\0')
            digest.update(file.read_bytes())
    return digest.hexdigest()


def main():
    previous = REPO / 'evaluations/runs/svt3'
    root = REPO / 'evaluations/runs/svt4'
    assert not (previous / 'gate-started.json').exists()
    assert not (previous / 'validation-release-ready.json').exists()
    assert not (previous / 'private-jobs').exists()
    assert (previous / 'plateau-decision.json').exists()
    root.mkdir(exist_ok=False)
    campaign = REPO / 'evaluations/runs/svg-information-research-20260926'
    campaign.mkdir(exist_ok=False)
    write(root / 'campaign-binding.json', {'campaign':campaign.name})
    write(campaign / 'campaign.json', {'scope':'One new research candidate; prior three-rejection campaign remains closed.',
        'maximum_candidates':1,'generation_calls':24,'validation_calls_max':12,'retries':0})
    for name in ['development','evaluator','private']:
        shutil.copytree(previous / name, root / name)
        assert tree(previous / name) == tree(root / name)
    for name in ['curation-status.json','evaluator-extension.json']:
        shutil.copy2(previous / name, root / name)
    research = REPO / 'projects/svg-brief-design/evaluation/information-editing-research-20260926.md'
    shutil.copy2(research, root / 'research.md')
    adoption = {'source_study':str(previous), 'source_protocol_sha256':sha(previous / 'protocol.json'),
        'source_closed_decision_sha256':sha(previous / 'plateau-decision.json'),
        'private_tree_sha256':tree(root / 'private'),
        'evaluator_lock_sha256':sha(root / 'evaluator/lock.json'),
        'cohort_was_unreleased':True,'cohort_was_unrun':True,
        'optimizer_content_read':False,'new_curation_calls':0,
        'scope':'Adoption of the unused svt3 reserve, not newly authored private cases. Host-level read avoidance is procedural.'}
    write(root / 'cohort-adoption.json',adoption)
    seal(root, REPO / 'skills/svg-brief-design', 1, False, {
        'claim':'Bounded test of information-role decisions and reversible SVG proofing against the installed construction skill.',
        'budget':{'curator_calls':0},
        'stopping':'One research candidate, then stop. No semantic retries. Freeze a qualified development winner before releasing the untouched adopted private cohort once. No mutation after release. The prior three-failure campaign remains closed.',
        'cohort_adoption':{'receipt_sha256':sha(root / 'cohort-adoption.json'),**adoption},
        'research':{'path':str(research),'sha256':sha(research),'claim':'Proposed transfer of design techniques; performance not established.'},
        'selection':{'baseline_error_guard':'Attributable agent failures retain native semantic zero. A changed winner must also gain at least two points with no family loss over eight points on all unaffected baseline families. All candidate trials must be error-free; evaluator or external failures make the comparison unavailable.'}
    })
    print(json.dumps({'root':str(root),'new_curation_calls':0,'reserved_private_cases':3,'candidate_budget':1}))


if __name__ == '__main__': main()
