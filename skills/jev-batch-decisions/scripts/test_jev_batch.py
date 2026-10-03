#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic contract, coverage, recovery and aggregation regression tests."""
from __future__ import annotations

import copy
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jev_batch import execute
from jev_contract import ContractError, decision, encode, job_valid, response_valid, strict_json
from jev_documents import batches, chunks, source_info
from jev_reduce import add, empty_stats, finish
from jev_transport import retry_delay


def native(payload, unknown=False):
    answers = {}
    for key, q in payload["questions"].items():
        kind = q["type"]
        if kind == "noul":
            answers[key] = dict(type=kind, noul=0.5 if unknown else 1.0)
        elif kind == "choice":
            options = list(q["criteria"])
            answers[key] = dict(type=kind, choice=options[0], confidence=0.1 if unknown else 1.0,
                                probabilities={k: float(k == options[0]) for k in options})
        else:
            probabilities = {str(i): float(i == 1) for i in range(len(q["criteria"]))}
            answers[key] = dict(type=kind, score=1.0, confidence=0.1 if unknown else 1.0,
                                probabilities=probabilities, legend={str(i): v for i, v in enumerate(q["criteria"])})
    return dict(model=payload["model"] + "-20260917", answers=answers,
                usage=dict(input_tokens=20, output_tokens=10, cost=0.00001))


class Tests(unittest.TestCase):
    def setUp(self):
        # Stay within the caller's permitted workspace, including on Windows.
        self.temp = tempfile.TemporaryDirectory(prefix="jev-test-", dir=Path.cwd())
        self.root = Path(self.temp.name)
        self.job = dict(version=1, questions={
            "flag": dict(type="noul", instructions="Is the feature enabled?"),
            "route": dict(type="choice", instructions="Select a route.", criteria={"a": "Route A", "unknown": "Unknown"}),
            "impact": dict(type="score", instructions="Rate impact.", criteria=["No impact", "Some impact", "Large impact"])
        }, reducers=dict(flag="any", route="histogram", impact="mean"), limits=dict(batch_items=2, concurrency=1))
        self.jobfile = self.root / "job.json"
        self.input = self.root / "records.jsonl"
        self.input.write_text('\n'.join(json.dumps(dict(id=i, text="Feature enabled")) for i in range(5)), encoding="utf-8")
        self.jobfile.write_bytes(encode(self.job))
        self.calls = []
        self.env = patch.dict(os.environ, {"OPENROUTER_API_KEY": "synthetic-test-key"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def post(self, payload, key, timeout):
        self.calls.append(payload)
        return 200, {}, encode(native(payload))

    def run_job(self, job=None, name="out", **kwargs):
        if job is not None:
            self.jobfile.write_bytes(encode(job))
        return execute(self.jobfile, [self.input], self.root/name, post=kwargs.pop("post", self.post), sleep=lambda _: None, **kwargs)

    def test_native_all_types_and_usage(self):
        payload = dict(model="typesafe/jev-1.13", questions=self.job["questions"])
        response_valid(native(payload), payload["questions"], payload["model"])

    def test_reject_response_mutations(self):
        payload = dict(model="typesafe/jev-1.13", questions=self.job["questions"])
        mutations = [lambda b: b["answers"].pop("flag"),
                     lambda b: b["answers"]["flag"].update(noul=float("nan")),
                     lambda b: b["answers"]["route"].update(choice="missing"),
                     lambda b: b["answers"]["route"].update(probabilities={"a": 0.2, "unknown": 0.2}),
                     lambda b: b["answers"]["impact"].update(score=2),
                     lambda b: b["answers"]["impact"].update(legend={"0": "bad"}),
                     lambda b: b.update(model="other/model"),
                     lambda b: b["usage"].update(input_tokens=True)]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                body = native(payload)
                mutate(body)
                with self.assertRaises(ContractError):
                    response_valid(body, payload["questions"], payload["model"])

    def test_strict_json_duplicate_and_nonfinite(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ContractError):
                strict_json(text)

    def test_invalid_job_contracts(self):
        for patch_value in ({"limits": {"batch_item": 2}}, {"review": {"noul_low": 0.9, "noul_high": 0.1}},
                            {"reducers": {"route": "mean"}}, {"model": "random/chat"}, {"version": True}):
            with self.assertRaises(ContractError):
                job_valid(self.job | patch_value)

    def test_unicode_text_exact_coverage(self):
        path = self.root / "text.md"
        texts = ["a"*321, ("A paragraph.\r\n\r\nOtro párrafo 中文 🎯. "*20), "\n"*81]
        for text in texts:
            path.write_bytes(text.encode("utf-8"))
            rows = list(chunks(source_info([path])[0], 61))
            self.assertEqual("".join(x["text"] for x in rows), text)
            self.assertEqual(rows[0]["location"]["start"], 0)
            self.assertEqual(rows[-1]["location"]["end"], len(text))
            self.assertTrue(all(len(x["text"]) <= 61 for x in rows))
            self.assertTrue(all(a["location"]["end"] == b["location"]["start"] for a,b in zip(rows, rows[1:])))

    def test_bom_and_csv_multiline(self):
        path = self.root / "rows.csv"
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(["id", "text"])
        writer.writerow(["r1", "line one\nline two, quoted"])
        path.write_bytes(b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8"))
        rows = list(chunks(source_info([path])[0], 100))
        self.assertEqual(len(rows), 1)
        self.assertEqual(json.loads(rows[0]["text"])["text"], "line one\nline two, quoted")
        self.assertEqual(rows[0]["location"]["physical_end_line"], 3)

    def test_invalid_csv_and_jsonl(self):
        for filename, text in (("x.csv", "a,a\n1,2"), ("y.csv", "a,b\n1"), ("x.jsonl", '{"a":1}\nnot json')):
            path = self.root / filename
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ContractError):
                list(chunks(source_info([path])[0], 100))

    def test_late_oversize_fails_before_calls(self):
        self.input.write_text('{"text":"valid"}\n'+json.dumps({"text": "x"*4000}), encoding="utf-8")
        with self.assertRaises(ContractError):
            self.run_job()
        self.assertEqual(self.calls, [])

    def test_duplicate_paths_and_binary(self):
        with self.assertRaises(ContractError):
            source_info([self.input, self.input])
        path = self.root / "binary.txt"
        path.write_bytes(b"abc\x00def")
        with self.assertRaises(ContractError):
            list(chunks(source_info([path])[0], 100))

    def test_no_key_needed_for_dry_run(self):
        with patch.dict(os.environ, {}, clear=True):
            report = self.run_job(dry_run=True)
        self.assertEqual(report["status"], "planned")
        self.assertFalse(self.calls)

    def test_batch_bindings_are_explicit(self):
        job = job_valid(self.job)
        items = chunks(source_info([self.input])[0], 3000)
        result = list(batches(items, job))
        self.assertEqual(len(result), 3)
        for batch, payload, bindings in result:
            self.assertEqual(len(bindings), len(batch)*3)
            for key, (item_id, _) in bindings.items():
                self.assertIn(item_id, payload["questions"][key]["instructions"])

    def test_response_fail_closed(self):
        def bad(payload, *_):
            response = native(payload)
            response["answers"].pop(next(iter(response["answers"])))
            return 200, {}, encode(response)
        with self.assertRaises(ContractError):
            self.run_job(post=bad)
        report = json.loads((self.root/"out/report.json").read_text())
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["metrics"]["http_attempts"], 1)
        self.assertFalse((self.root/"out/aggregates.json").exists())

    def test_resume_no_new_calls_and_same_decisions(self):
        self.run_job()
        before = (self.root/"out/decisions.jsonl").read_bytes()
        report = self.run_job(resume=True)
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(report["metrics"]["cache_hits_this_invocation"], 3)
        self.assertEqual(before, (self.root/"out/decisions.jsonl").read_bytes())

    def test_changed_input_and_job_refuse_resume(self):
        self.run_job()
        self.input.write_text('{"id":"changed"}', encoding="utf-8")
        with self.assertRaises(ContractError):
            self.run_job(resume=True)
        self.assertEqual(len(self.calls), 3)

    def test_checkpoint_tampering_refused(self):
        self.run_job()
        path = next((self.root/"out/checkpoints").glob("*.json"))
        saved = json.loads(path.read_text())
        saved["response"]["model"] = "changed"
        path.write_bytes(encode(saved))
        with self.assertRaises(ContractError):
            self.run_job(resume=True)
        self.assertEqual(len(self.calls), 3)

    def test_retry_and_cost_accounting(self):
        attempts = []
        def retry(payload, *_):
            attempts.append(1)
            return (429, {"Retry-After": "0"}, b"") if len(attempts) == 1 else (200, {}, encode(native(payload)))
        report = self.run_job(post=retry)
        self.assertEqual(report["metrics"]["http_attempts"], 4)
        self.assertEqual(report["metrics"]["cost_unreported_attempts"], 1)

    def test_auth_failure_no_retry(self):
        attempts = []
        def auth(*_):
            attempts.append(1)
            return 401, {}, b"secret must never enter errors"
        with self.assertRaises(ContractError):
            self.run_job(post=auth)
        self.assertEqual(len(attempts), 1)
        self.assertNotIn("secret", (self.root/"out/report.json").read_text())

    def test_transport_failure_no_retry(self):
        attempts = []
        def timeout(*_):
            attempts.append(1)
            raise ContractError("Transport failed; request charge is unknown.")
        with self.assertRaises(ContractError):
            self.run_job(post=timeout)
        self.assertEqual(len(attempts), 1)

    def test_total_attempt_cap_includes_resumes(self):
        job = copy.deepcopy(self.job)
        job["limits"].update(max_requests=3, attempts=1)
        def fail_second(payload, *_):
            self.calls.append(payload)
            return (500, {}, b"") if len(self.calls) == 2 else (200, {}, encode(native(payload)))
        with self.assertRaises(ContractError):
            self.run_job(job=job, post=fail_second)
        with self.assertRaises(ContractError):
            self.run_job(resume=True)
        report = json.loads((self.root/"out/report.json").read_text())
        self.assertEqual(report["metrics"]["http_attempts"], 3)

    def test_three_valued_logic_and_exact_mean(self):
        cases = [("any", [False, None], None), ("any", [None, True], True),
                 ("all", [True, None], None), ("all", [False, None], False),
                 ("any", [], None), ("mean", [1, 1, 4], 2), ("max", [1, None], None)]
        for op, values, expected in cases:
            stats = empty_stats(op)
            for value in values:
                add(stats, value)
            self.assertEqual(finish(stats)["value"], expected)

    def test_native_unknown_review(self):
        review = job_valid(self.job)["review"]
        self.assertIsNone(decision(dict(type="noul", noul=0.5), review)["value"])
        self.assertIsNone(decision(dict(type="choice", choice="unknown", confidence=1), review)["value"])

    def test_recursive_coverage_and_review_propagation(self):
        job = copy.deepcopy(self.job)
        job["reduce"] = dict(context="Any flag is sufficient.", questions={"flag": job["questions"]["flag"]}, fan_in=2)
        def unknown(payload, *_):
            return 200, {}, encode(native(payload, unknown="items" in payload["state"]))
        report = self.run_job(job=job, post=unknown)
        final = json.loads((self.root/"out/final.json").read_text())
        self.assertEqual(final["leaf_count"], 5)
        self.assertEqual(final["level"], 3)
        self.assertEqual(final["review_leaf_count"], 5)
        self.assertTrue(final["decisions"]["flag"]["needs_review"])
        self.assertEqual(report["metrics"]["accepted_calls"], 9)

    def test_output_lock_and_source_protection(self):
        out = self.root / "out"
        out.mkdir()
        (out/".lock").write_text("1234")
        with self.assertRaises(ContractError):
            self.run_job()
        with self.assertRaises(ContractError):
            execute(self.jobfile, [self.input], self.root, dry_run=True)

    def test_retry_after_bound(self):
        self.assertEqual(retry_delay({"Retry-After": "2"}, 0), 2)
        with self.assertRaises(ContractError):
            retry_delay({"retry-after": "120"}, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
