#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Direct CLI tests for a reviewed bridge between two local class namespaces."""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from typed_snapshot_delta import compare_snapshots


CLI = Path(__file__).with_name('compare_document_versions.py')
ABSENT = object()


def span(line, quote):
    return {'start_line': line, 'end_line': line, 'quote': quote}


def inventory(classes, *assertions):
    rows = {kind: [] for kind in ('classes', 'subclasses', 'relations', 'constraints')}
    lines = []
    for identifier, label in classes:
        lines.append(f'{label} is a class.')
        rows['classes'].append({'id': identifier, 'label': label, 'evidence': span(len(lines), lines[-1])})
    for kind, row, quote in assertions:
        lines.append(quote)
        rows[kind].append({**row, 'evidence': span(len(lines), quote)})
    return rows, lines


def bridge(*pairs):
    return {'pairs': [{'base': before, 'head': after} for before, after in pairs]}


def bindings(base, head, pair):
    return {'source_sha256': {'base': sha256(base).hexdigest(), 'head': sha256(head).hexdigest()},
            'snapshot_pair_sha256': sha256(pair).hexdigest()}


class TestClassIdentityBridge(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.run_index = 0

    def invoke(self, base, head, identity=ABSENT, *, review=ABSENT, draft=False, output_is_map=False,
               seed='17', mapping_json=None, mutate=None, source_format=None):
        self.run_index += 1
        run_dir = self.root / str(self.run_index)
        run_dir.mkdir()
        base_path, head_path = (run_dir / f'{side}.txt' for side in ('base', 'head'))
        for path, side in ((base_path, base), (head_path, head)):
            raw = ('\n'.join(side[1]) + '\n').encode()
            path.write_bytes(source_format(raw) if source_format else raw)
        pair = {'base': base[0], 'head': head[0]}
        if review is not ABSENT:
            pair['review'] = review
        proposal = run_dir / 'proposal.json'
        proposal.write_bytes(json.dumps(pair if not draft else {'observations': []}).encode())
        map_path = run_dir / 'map.json'
        target = map_path if output_is_map else run_dir / 'delta.json'
        flags = []
        if identity is not ABSENT or mapping_json is not None:
            if isinstance(identity, dict) and identity.keys() == {'pairs'}:
                identity = {**identity, **bindings(base_path.read_bytes(), head_path.read_bytes(), proposal.read_bytes())}
            map_path.write_bytes((json.dumps(identity) if mapping_json is None else mapping_json).encode())
            flags = ['--class-identity', str(map_path)]
        if mutate is not None:
            mutate({'base': base_path, 'head': head_path, 'pair': proposal, 'map': map_path})
        input_hashes = {path: path.read_bytes() for path in (base_path, head_path, proposal, map_path) if path.exists()}
        completed = subprocess.run([sys.executable, '-B', str(CLI), '--base', str(base_path), '--head', str(head_path),
                                    '--draft' if draft else '--snapshot-pair', str(proposal), '--output', str(target),
                                    *flags], capture_output=True, check=False,
                                   env={**os.environ, 'PYTHONHASHSEED': seed})
        self.assertTrue(all(path.read_bytes() == original for path, original in input_hashes.items()))
        return completed, target

    def success(self, *args, **kwargs):
        process, target = self.invoke(*args, **kwargs)
        self.assertEqual(process.returncode, 0, (process.stdout, process.stderr))
        self.assertEqual(json.loads(process.stdout)['semantic_status'], 'not_run')
        return json.loads(target.read_bytes()), target.read_bytes(), process.stdout

    def invalid(self, base, head, mapping=ABSENT, *, code='INVALID_CLASS_IDENTITY', path=None, **kwargs):
        process, target = self.invoke(base, head, mapping, **kwargs)
        self.assertEqual(process.returncode, 2, (process.stdout, process.stderr))
        error = json.loads(process.stdout)['error']
        self.assertEqual(error['code'], code)
        if path:
            self.assertEqual(error['path'], path)
        if not kwargs.get('output_is_map'):
            self.assertFalse(target.exists())

    def test_reused_id_alone_does_not_align_distinct_labels(self):
        base = inventory([('role', 'Old name')])
        head = inventory([('role', 'New name')])
        absent, _, _ = self.success(base, head)
        self.assertEqual(absent['added'], [{'collection': 'classes', 'index': 0}])
        self.assertEqual(absent['removed'], [{'collection': 'classes', 'index': 0}])
        aligned, _, _ = self.success(base, head, bridge(('role', 'role')))
        self.assertEqual(aligned, {'status': 'unchanged', 'added': [], 'removed': [],
                                   'modified': [], 'review': None})

    def test_cross_namespace_roles_constraint_change_and_exact_selectors(self):
        base = inventory([('old-a', 'Parcel'), ('old-b', 'Signature')],
                         ('subclasses', {'child': 'old-b', 'parent': 'old-a'}, 'Signature is a kind of Parcel.'),
                         ('relations', {'subject': 'old-a', 'object': 'old-b', 'predicate': 'includes'}, 'Parcel includes Signature.'),
                         ('constraints', {'subject': 'old-a', 'object': 'old-b', 'predicate': 'includes',
                                          'kind': 'max-cardinality', 'value': 2}, 'Parcel includes at most two signatures.'))
        head = inventory([('new-b', 'Signed token'), ('new-a', 'Shipping parcel'), ('unused', 'Policy')],
                         ('subclasses', {'child': 'new-b', 'parent': 'new-a'}, 'Signed token is a kind of Shipping parcel.'),
                         ('relations', {'subject': 'new-b', 'object': 'new-a', 'predicate': 'includes'}, 'Signed token includes Shipping parcel.'),
                         ('constraints', {'subject': 'new-a', 'object': 'new-b', 'predicate': 'includes',
                                          'kind': 'max-cardinality', 'value': 1}, 'Shipping parcel includes at most one signed token.'))
        decision = bridge(('old-a', 'new-a'), ('old-b', 'new-b'))
        pair = {'base': base[0], 'head': head[0]}
        original = deepcopy(pair)
        observed = bindings(('\n'.join(base[1]) + '\n').encode(), ('\n'.join(head[1]) + '\n').encode(),
                            json.dumps(pair).encode())
        expected = compare_snapshots(pair, base[1], head[1], class_identity={**decision, **observed},
                                     input_sha256=observed)
        self.assertEqual(pair, original)
        first, data, stdout = self.success(base, head, decision)
        self.assertEqual(first, expected)
        self.assertEqual(first['added'], [{'collection': 'classes', 'index': 2}, {'collection': 'relations', 'index': 0}])
        self.assertEqual(first['removed'], [{'collection': 'relations', 'index': 0}])
        self.assertEqual(first['modified'], [{'collection': 'constraints', 'before': 0, 'after': 0}])
        self.assertEqual(self.success(base, head, bridge(('old-b', 'new-b'), ('old-a', 'new-a')), seed='91'),
                         (first, data, stdout))

    def test_unknown_class_or_id_in_wrong_namespace(self):
        base = inventory([('old', 'Parcel')])
        head = inventory([('new', 'Shipping parcel')])
        self.invalid(base, head, bridge(('new', 'new')), path='/class_identity/pairs/0/base')
        self.invalid(base, head, bridge(('old', 'old')), path='/class_identity/pairs/0/head')

    def test_duplicate_endpoints_and_duplicate_pairs_are_rejected(self):
        base = inventory([('a', 'Parcel'), ('b', 'Signature')])
        head = inventory([('x', 'Container'), ('y', 'Token')])
        for first, second, endpoint in ((('a', 'x'), ('a', 'y'), 'base'),
                                        (('a', 'x'), ('b', 'x'), 'head'),
                                        (('a', 'x'), ('a', 'x'), 'base')):
            with self.subTest(first=first, second=second):
                self.invalid(base, head, bridge(first, second), path=f'/class_identity/pairs/1/{endpoint}')

    def test_literal_matches_win_on_both_sides_and_use_existing_normalization(self):
        base = inventory([('a', 'Same Cafe\u0301'), ('b', 'Old token')])
        head = inventory([('x', 'Same  Caf\u00e9'), ('y', 'New token')])
        for pair in (('a', 'y'), ('b', 'x')):
            with self.subTest(pair=pair):
                self.invalid(base, head, bridge(pair), path='/class_identity/pairs/0')
        self.assertEqual(self.success(base, head, bridge(('a', 'x'))), self.success(base, head))

    def test_malformed_bridge_and_duplicate_json_keys_fail(self):
        base = inventory([('a', 'Parcel')])
        head = inventory([('b', 'Shipping parcel')])
        for payload in (None, [], {'pairs': None}, {'pairs': [], 'unknown': True},
                        {'pairs': ['a']}, {'pairs': [{'base': True, 'head': 'b'}]},
                        {'pairs': [{'base': 'a'}]}):
            with self.subTest(payload=payload):
                self.invalid(base, head, payload)
        self.invalid(base, head, mapping_json='{"pairs":[],"pairs":[]}', code='JSON_DUPLICATE_KEY')
        self.invalid(base, head, mapping_json=json.dumps(bridge(('a', 'b'))), path='/class_identity')

    def test_empty_bridge_is_byte_identical_and_non_snapshot_use_fails(self):
        base = inventory([('a', 'Parcel')])
        head = inventory([('b', 'Shipping parcel')])
        self.assertEqual(self.success(base, head), self.success(base, head, bridge()))
        self.invalid(base, head, bridge(), draft=True, path='/class_identity')

    def test_bridge_is_protected_as_an_input_and_bad_evidence_still_fails(self):
        base = inventory([('a', 'Parcel')])
        head = inventory([('b', 'Shipping parcel')])
        self.invalid(base, head, bridge(('a', 'b')), output_is_map=True, code='INPUT_OVERWRITE_FORBIDDEN')
        head[0]['classes'][0]['evidence']['quote'] = 'Not in the source.'
        self.invalid(base, head, bridge(('a', 'b')), code='INVALID_SNAPSHOT_EVIDENCE')

    def test_changed_source_bytes_reject_a_map_for_either_revision(self):
        base = inventory([('role', 'Parcel')])
        head = inventory([('role', 'Shipping parcel')])
        mutations = {
            'uncited': lambda raw: raw + b'New material outside the citation.\n',
            'cited': lambda raw: raw.replace(b'is a class', b'is now a class'),
        }
        for side in ('base', 'head'):
            for label, transform in mutations.items():
                def change_source(paths):
                    path = paths[side]
                    path.write_bytes(transform(path.read_bytes()))
                with self.subTest(side=side, label=label):
                    self.invalid(base, head, bridge(('role', 'role')), mutate=change_source,
                                 code='CLASS_IDENTITY_BINDING_MISMATCH', path=f'/class_identity/source_sha256/{side}')

    def test_identical_ids_do_not_reuse_map_for_changed_snapshot(self):
        base = inventory([('role', 'Parcel')])
        head = inventory([('role', 'Shipping parcel')])

        def reuse_id(paths):
            path = paths['pair']
            data = json.loads(path.read_bytes())
            data['head']['classes'][0]['label'] = 'Unrelated class with same ID'
            self.assertEqual(data['head']['classes'][0]['id'], 'role')
            path.write_bytes(json.dumps(data).encode())

        self.invalid(base, head, bridge(('role', 'role')), mutate=reuse_id,
                     code='CLASS_IDENTITY_BINDING_MISMATCH', path='/class_identity/snapshot_pair_sha256')

    def test_snapshot_reformatting_is_a_different_exact_pair(self):
        base = inventory([('a', 'Parcel')])
        head = inventory([('b', 'Shipping parcel')])
        def reformat(paths):
            path = paths['pair']
            path.write_bytes(json.dumps(json.loads(path.read_bytes()), indent=2).encode())
        self.invalid(base, head, bridge(('a', 'b')), mutate=reformat,
                     code='CLASS_IDENTITY_BINDING_MISMATCH', path='/class_identity/snapshot_pair_sha256')

    def test_bound_utf8_bom_and_crlf_match_existing_line_validation(self):
        base = inventory([('a', 'Caf\u00e9 parcel')])
        head = inventory([('b', 'Shipping caf\u00e9 parcel')])
        mapping = bridge(('a', 'b'))
        converted = lambda raw: b'\xef\xbb\xbf' + raw.replace(b'\n', b'\r\n')
        self.assertEqual(self.success(base, head, mapping), self.success(base, head, mapping, source_format=converted))

    def test_malformed_digest_is_reported_before_using_pairs(self):
        base = inventory([('a', 'Parcel')])
        head = inventory([('b', 'Shipping parcel')])
        def invalid_digest(paths):
            path = paths['map']
            data = json.loads(path.read_bytes())
            data['source_sha256']['head'] = '0' * 63
            path.write_bytes(json.dumps(data).encode())
        self.invalid(base, head, bridge(('a', 'b')), mutate=invalid_digest,
                     path='/class_identity/source_sha256/head')

    def test_abstention_preserves_caller_citations_and_validates_bridge(self):
        base = inventory([('a', 'Parcel')])
        head = inventory([('b', 'Shipping parcel')])
        review = {'reason': 'Other contextual evidence remains unresolved.',
                  'base': [span(1, base[1][0])], 'head': [span(1, head[1][0])]}
        self.assertEqual(self.success(base, head, bridge(('a', 'b')), review=review)[0],
                         {'status': 'abstain', 'added': [], 'removed': [], 'modified': [], 'review': review})
        self.invalid(base, head, bridge(('missing', 'b')), review=review)


if __name__ == '__main__':
    unittest.main()
