#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regrade only the six manifest-pinned saved workspaces; never resample."""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(workspace):
    files = {path.relative_to(workspace).as_posix(): {'bytes': path.stat().st_size, 'sha256': sha(path)}
             for path in sorted(workspace.rglob('*')) if path.is_file()}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    return dict(sha256=digest, file_count=len(files), files=files)


def write_new(path, value):
    if path.exists():
        raise ValueError(f'Refusing to replace existing revision evidence: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[6]
    revision = Path(__file__).resolve().parent
    manifest_path = revision / 'correction-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for record in [manifest['parent_manifest'], manifest['parent_grader'], manifest['original_cohort'], *manifest['revision_controls'].values()]:
        if sha(root / record['path']) != record['sha256']:
            raise ValueError(f'Pinned revision input changed: {record["path"]}')
    grader = runpy.run_path(str(revision / 'validate_svg_cases.py'))
    records = []
    for subject in manifest['subjects']:
        workspace = (root / subject['workspace']).resolve()
        before = snapshot(workspace)
        if before['sha256'] != subject['workspace_before_sha256']:
            raise ValueError(f'Original workspace changed before regrade: {subject["run_id"]}')
        for record in subject['unchanged_gate_files']:
            if sha(root / record['path']) != record['sha256']:
                raise ValueError(f'Original gate evidence changed: {record["path"]}')
        original_path = root / subject['original_report']['path']
        if sha(original_path) != subject['original_report']['sha256']:
            raise ValueError('Original independent report changed')
        original = json.loads(original_path.read_text(encoding='utf-8'))
        result = grader['validate'](subject['case'], workspace)
        after = snapshot(workspace)
        if before != after:
            raise ValueError(f'Evaluated workspace changed: {subject["run_id"]}')
        report_path = root / subject['revision_report']
        if report_path.resolve().is_relative_to(workspace):
            raise ValueError('Revision reports must remain outside evaluated workspaces')
        result.update(verifier_revision=manifest['revision_id'], revision_manifest_sha256=sha(manifest_path),
                      original_artifact_checks_passed=original['artifact_checks_passed'], original_error=original.get('error'),
                      output_hashes_unchanged=True, workspace_hashes_before=before, workspace_hashes_after=after,
                      manual_review_gates_unchanged=True, resampling=False)
        write_new(report_path, result)
        records.append(dict(case=subject['case'], run_id=subject['run_id'], passed=result['artifact_checks_passed'],
                            artifact_checks_passed=result['artifact_checks_passed'], output_hashes_unchanged=True,
                            workspace_before_sha256=before['sha256'], workspace_after_sha256=after['sha256'],
                            workspace_file_count=before['file_count'], report=subject['revision_report'],
                            original_artifact_checks_passed=original['artifact_checks_passed'], original_error=original.get('error')))
    aggregate = dict(revision_id=manifest['revision_id'], revision_manifest_sha256=sha(manifest_path),
                     parent_manifest_sha256=manifest['parent_manifest']['sha256'], original_cohort_sha256=manifest['original_cohort']['sha256'],
                     corrected_subjects=len(records), resampling=False, manual_review_gates_unchanged=True, results=records)
    write_new(args.report.resolve(), aggregate)
    print(json.dumps({'revision_id': manifest['revision_id'], 'subjects': len(records), 'artifact_passes': sum(record['passed'] for record in records), 'all_output_hashes_unchanged': True, 'report': str(args.report.resolve())}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
