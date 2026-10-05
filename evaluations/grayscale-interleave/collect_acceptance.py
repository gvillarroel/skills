#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Select whole current-payload cohorts and retain every reviewed outcome."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IGNORED = {'node_modules','.git','.cache','.venv','venv','.pytest_cache','.ruff_cache','.mypy_cache','.tox',
           '.vite','dist','output','playwright-report','test-results','__pycache__'}
TEXT = {'.md','.py','.json','.yaml','.yml','.js','.mjs','.ts','.css','.html','.svg','.puml','.lock','.txt'}


def inventory(root):
    files = {}
    for directory, names, leafs in os.walk(root):
        names[:] = [name for name in names if name not in IGNORED and not (Path(directory).relative_to(root)==Path('assets') and name=='examples')]
        for name in leafs:
            path = Path(directory)/name
            if path.suffix in {'.pyc','.pyo'}:
                continue
            data = path.read_bytes()
            if path.suffix.lower() in TEXT:
                data = data.replace(b'\r\n',b'\n')
            files[path.relative_to(root).as_posix()] = hashlib.sha256(data).hexdigest()
    return files


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def raw_snapshot_digest(root):
    snapshot = {}
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.relative_to(root).parts or path.suffix.lower() in {'.pyc','.pyo'}:
            continue
        data = path.read_bytes()
        snapshot[path.relative_to(root).as_posix()] = {'sizeBytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    return digest(snapshot)


def main():
    cases = json.loads((HERE/'cases.json').read_bytes())
    canonical = {skill:inventory(ROOT/'skills'/skill) for skill in cases}
    command_path = ROOT/'projects/grayscale-interleave/artifacts/reviews/contract-command-check.json'
    exact = {row['runId']:row for row in json.loads(command_path.read_bytes())} if command_path.exists() else {}
    revisions = {revision:json.loads((HERE/name).read_bytes()) for revision,name in
                 [('r1','cases.json'),('r2','cases-contrast.json'),('r3','cases-recipe.json'),('r4','cases-prefix.json')]}
    quantitative_path = ROOT/'projects/grayscale-interleave/artifacts/reviews/prefix-quantitative-owner-contract-repair.json'
    quantitative = json.loads(quantitative_path.read_bytes()) if quantitative_path.exists() else {}
    quantitative_rows = {row['runId']:row for row in quantitative.get('rows',[])}
    rows = []
    reports = {}
    current_oracle_sha256 = hashlib.sha256((HERE/'review_outputs.py').read_bytes()).hexdigest()
    for revision in ('r1','r2','r3','r4'):
        base = ROOT/'projects/grayscale-interleave/artifacts/reviews/forward-native'
        original = base/f'{revision}-results.json'
        prior_final = base/f'{revision}-final-results.json'
        final = base/f'{revision}-canvas-repair-results.json'
        owner_repair = base/f'{revision}-owner-contract-repair-results.json'
        path = owner_repair if owner_repair.exists() else (final if final.exists() else (prior_final if prior_final.exists() else original))
        if not path.exists():
            continue
        reports[revision] = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (original, prior_final, final, owner_repair) if p.exists()}
        report_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        for observed in json.loads(path.read_bytes()):
            run = ROOT/'evaluations/runs'/observed['runId']
            manifest = json.loads((run/'run-manifest.json').read_bytes())
            raw_result = json.loads((run/'evaluation-result.json').read_bytes())
            events = json.loads((run/'event-check.json').read_bytes())
            integrity = json.loads((run/'skill-integrity-check.json').read_bytes())
            artifacts = json.loads((run/'artifact-check.json').read_bytes())
            config = revisions[revision][observed['skill']]
            item = config[observed['family']]
            prompt = (run/'prompt.md').read_text(encoding='utf-8')
            expected_prompt = (HERE/item['prompt']).read_text(encoding='utf-8')
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            expected_hashes = {row['path']:row['sha256'] for row in artifacts.get('outputs',[])}
            actual_hashes = {name:hashlib.sha256((run/'workspace'/name).read_bytes()).hexdigest()
                             for name in item['outputs'] if (run/'workspace'/name).is_file()}
            repeat = int(observed['runId'].rsplit('-',1)[1])
            identity_matches = (manifest['runId'] == run.name == f"gray-20261005-{revision}-{observed['skill']}-{observed['family']}-{repeat}"
                                and repeat in ({1} if observed['family']=='contract' else {1,2,3}))
            raw_gate = (identity_matches and raw_result.get('passed') is True and raw_result.get('returnCode')==0
                        and all(raw_result.get('gates',{}).get(key) is True for key in ('artifacts','events','skillIntegrity'))
                        and events.get('passed') is True and artifacts.get('passed') is True
                        and integrity.get('passed') is True
                        and integrity.get('beforeDigest')==integrity.get('afterDigest')==manifest['skill']['payloadSha256']
                        and manifest['skill']['name']==observed['skill'] and manifest['skill']['profile']=='runtime'
                        and manifest['pi']['mode']=='json' and manifest['pi']['model']==config['model']
                        and manifest['eventPolicy']['strict'] is True
                        and manifest['expectedOutputs']==item['outputs']
                        and prompt==expected_prompt and prompt_hash==manifest['prompt']['sha256']
                        and actual_hashes==expected_hashes==observed.get('outputSha256'))
            current = inventory(run/'workspace/skills'/observed['skill'])
            current_digest = digest(current)
            copied_bytes_intact = raw_snapshot_digest(run/'workspace/skills'/observed['skill']) == manifest['skill']['payloadSha256']
            same = current == canonical[observed['skill']]
            if revision == 'r4':
                same = same and digest(canonical[observed['skill']]) == config['frozenNormalizedPayloadSha256']
            native_family = 'complete-contract' if observed['family'] == 'contract' else ('gray-prefix' if revision == 'r4' else 'full-cycle')
            native_gate = observed['artifactPassed'] is True
            if revision == 'r4':
                native_gate = native_gate and observed.get('caseFamily') == native_family and observed.get('oracleSha256') == current_oracle_sha256
                if observed['family'] == 'naturalistic':
                    native_gate = native_gate and observed.get('categoryCount') == 13
            raw_gate = raw_gate and copied_bytes_intact and observed['strictPassed'] == raw_result.get('passed')
            raw_gate = raw_gate and observed['payloadSha256'] == manifest['skill']['payloadSha256']
            if revision == 'r4' and observed['family'] == 'naturalistic':
                raw_gate = raw_gate and prompt_hash == item['promptSha256']
            raw_gate = raw_gate and all(manifest['eventPolicy'].get(name) is True for name in
                ('requirePromptReadFirst','requireObservedModel','failOnInvalidEventJson','failOnToolError'))
            supplemental = exact.get(observed['runId'],{})
            command = observed['family']!='contract' or (supplemental.get('passed') is True
                and supplemental.get('evidenceSha256')=={name:hashlib.sha256((run/name).read_bytes()).hexdigest()
                    for name in ('prompt.md','events.jsonl','run-manifest.json')})
            quantitative_passed = revision != 'r4' or observed['family'] != 'naturalistic' or (
                quantitative.get('nativeReportSha256') == report_sha256
                and quantitative_rows.get(observed['runId'],{}).get('passed') is True)
            row = {k:observed[k] for k in ('runId','skill','family','strictPassed','artifactPassed','findings','payloadSha256')}
            row.update(revision=revision,currentPayload=same,exactCommandPassed=command,rawStrictGatesPassed=raw_gate,
                       passed=observed['passed'] and native_gate and same and command and raw_gate and quantitative_passed,
                       quantitativeReviewPassed=quantitative_passed,
                       copiedBytesIntact=copied_bytes_intact,caseFamily=native_family,
                       nativeReportSha256=report_sha256,nativeOracleSha256=observed.get('oracleSha256'),
                       normalizedPayloadSha256=current_digest,promptSha256=manifest['prompt']['sha256'],
                       evidenceSha256={name:hashlib.sha256((run/name).read_bytes()).hexdigest() for name in
                           ('run-manifest.json','evaluation-result.json','event-check.json','skill-integrity-check.json','artifact-check.json','prompt.md','events.jsonl')},
                       model=manifest['pi']['model'])
            rows.append(row)
    selected = {}
    pending = []
    for skill in cases:
        contracts = [row for row in rows if row['skill']==skill and row['family']=='contract' and row['passed']]
        cohorts = []
        for revision in ('r4',):
            members = [row for row in rows if row['skill']==skill and row['family']=='naturalistic' and row['revision']==revision]
            repeats={int(r['runId'].rsplit('-',1)[1]) for r in members}
            expected_ids = {f'gray-20261005-{revision}-{skill}-naturalistic-{repeat}' for repeat in (1,2,3)}
            if len(members)==3 and {r['runId'] for r in members}==expected_ids and repeats=={1,2,3} and len({r['promptSha256'] for r in members})==1 and all(r['currentPayload'] for r in members) and sum(r['passed'] for r in members)>=2:
                cohorts.append(members)
        if not contracts or not cohorts:
            pending.append(skill)
            continue
        members = cohorts[0]
        selected[skill] = {'contract':contracts[-1]['runId'],'naturalistic':[row['runId'] for row in members],
                           'naturalisticPassed':sum(row['passed'] for row in members),
                           'caseFamily':'gray-prefix','revision':'r4','categoryCount':13,
                           'promptSha256':members[0]['promptSha256'],'normalizedPayloadSha256':digest(canonical[skill]),
                           'sourceFileCount':len(canonical[skill])}
    result = {'scope':'Current complete palette contracts plus authored thirteen-category primary-red/twelve-neutral prefix keys only; native full-cycle and primary workflows have separate evidence.',
              'ok':not pending,'ownerCount':len(cases),'acceptedOwnerCount':len(selected),'pending':pending,
              'selected':selected,'attempts':rows,'retainedNativeReports':reports,
              'quantitativeReviewSha256':hashlib.sha256(quantitative_path.read_bytes()).hexdigest() if quantitative_path.exists() else None,
              'limits':'Retained seventeen-category failures are not prefix passes; manual free-form overflow reliability is not established.',
              'nativeReviewPolicy':'Uniform validator-only repairs: canvas accepts an exact white string or unambiguous white paint object; contracts export exact whole copied owner definitions, with every canonical field present and equal and independently literal full-sequence canvas filters. All native quality gates unchanged; report captures are versioned.',
              'priorOracleSha256':'b45a9630938acfe2d2053c7013168d845ea22112fda033d21a42fa444e949e7c',
              'protocolSha256':hashlib.sha256((HERE/'protocol.md').read_bytes()).hexdigest(),
              'collectorSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'oracleSha256':current_oracle_sha256,
              'casesSha256':{revision:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for revision,name in
                  [('r1','cases.json'),('r2','cases-contrast.json'),('r3','cases-recipe.json'),('r4','cases-prefix.json')]},
              'normalization':'CRLF to LF for listed text formats only; every runtime filename and normalized byte must match.',
              'retainedExternalFailure':'gray-20261005-spark-availability'}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('ok','ownerCount','acceptedOwnerCount','pending')},indent=2))
    return 0 if result['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
