#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Audit the shipped mathematical template, not arbitrary adapter isolation."""

from __future__ import annotations

import contextlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from run_simulation_experiment import load_model


TEMPLATE = Path(__file__).resolve().parent.parent / "assets/templates/model.py"
AUDIT_ACTIVE = False


def reject_target_capabilities(event: str, arguments: tuple) -> None:
    """Fail this test on Python-audited process, network, or inference imports."""
    if not AUDIT_ACTIVE:
        return
    if event.startswith(("socket.", "subprocess.", "os.exec", "os.spawn")) or event in {
        "os.system", "os.fork", "os.forkpty", "os.posix_spawn", "os.startfile",
        "os.startfile/2", "ctypes.dlopen", "urllib.Request", "http.client.connect",
    }:
        raise AssertionError(f"Mathematical template attempted a forbidden capability: {event}")
    if event == "import" and arguments:
        root_module = str(arguments[0]).split(".")[0]
        if root_module in {"openai", "anthropic", "ollama", "transformers", "vllm"}:
            raise AssertionError(f"Mathematical template attempted an inference import: {root_module}")


sys.addaudithook(reject_target_capabilities)


@contextlib.contextmanager
def mathematical_scope():
    global AUDIT_ACTIVE
    previous = AUDIT_ACTIVE
    AUDIT_ACTIVE = True
    try:
        yield
    finally:
        AUDIT_ACTIVE = previous


class MathematicalTemplateTests(unittest.TestCase):
    def with_template(self, check) -> None:
        with tempfile.TemporaryDirectory(prefix="simulation-only-") as temporary:
            root = Path(temporary)
            shutil.copyfile(TEMPLATE, root / "model.py")
            with mathematical_scope():
                model, *_ = load_model(root, "model.py")
                check(model)

    def test_stochastic_template_has_no_audited_target_capabilities(self) -> None:
        def check(model):
            values = []
            for seed in range(64):
                run = {"seed": seed, "parameters": {
                    "stock_units": 100, "demand_mean": 105, "demand_sd": 15,
                }}
                result = model.simulate(run)
                self.assertEqual(result, model.simulate(run))
                values.append(result["outcomes"]["fill_rate"])
                self.assertTrue(0 <= values[-1] <= 1)
            self.assertGreater(len(set(values)), 1)
        self.with_template(check)

    def test_deterministic_limit_and_policy_effect_are_mathematical(self) -> None:
        def check(model):
            results = []
            for stock in (100, 115):
                result = model.simulate({"seed": 7, "parameters": {
                    "stock_units": stock, "demand_mean": 110, "demand_sd": 0,
                }})
                results.append(result["outcomes"])
            self.assertAlmostEqual(results[0]["fill_rate"], 100 / 110)
            self.assertEqual(results[0]["unmet_units"], 10)
            self.assertEqual(results[1]["fill_rate"], 1)
            self.assertEqual(results[1]["unmet_units"], 0)
        self.with_template(check)

    def test_audit_sentinels_fail_without_launching_or_connecting(self) -> None:
        # Emit audit records directly: no process, socket, or target is created.
        for event, arguments in (
            ("subprocess.Popen", ("forbidden-target", (), None, None)),
            ("socket.connect", (None, ("invalid.example", 443))),
            ("import", ("openai", None, (), (), ())),
        ):
            with self.subTest(event=event), mathematical_scope():
                with self.assertRaises(AssertionError):
                    sys.audit(event, *arguments)


if __name__ == "__main__":
    unittest.main()
