#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Native Harbor verifier: isolated visual evidence, then expert Jev judgment."""
import asyncio
import os
from pathlib import Path
import re
import shlex
import sys

from harbor.verifier.base import BaseVerifier
from harbor.models.verifier.result import VerifierResult


class SvgExcellenceVerifier(BaseVerifier):
    def __init__(self, *args, evaluator_bundle, evaluator_lock_sha256, **kwargs):
        super().__init__(*args, **kwargs)
        self.bundle = Path(evaluator_bundle)
        self.lock_sha256 = evaluator_lock_sha256

    async def verify(self):
        # Evaluator dependencies and credentials live only in the trusted host.
        # The generator never receives this bundle, observations or evaluator keys.
        sys.path.insert(0, str(self.bundle/"scripts"))
        from svg_excellence import read, sha, write
        from evaluate_svg_jev import validate_bundle
        if sha((self.bundle/"lock.json").read_bytes()) != self.lock_sha256:
            raise ValueError("Evaluator lock changed")
        validate_bundle(self.bundle)
        match = re.search(r"`(/logs/artifacts/[^`]+\.svg)`", self.task.instruction)
        if not match:
            raise ValueError("The task must declare one exact SVG delivery path")
        expected = match.group(1)
        out = self.trial_paths.verifier_dir
        out.mkdir(parents=True, exist_ok=True)
        presence = await self.environment.exec(command="test -f " + shlex.quote(expected))
        if presence.return_code != 0:
            rewards = {"artifact_valid": 0.0, "technical_excellence": 0.0}
            write(out/"metrics.json", {"status": "artifact_failure", "reason": "Required SVG is missing"})
            write(out/"reward.json", rewards)
            return VerifierResult(rewards=rewards)
        artifact = out/"input.svg"
        await self.environment.download_file(source_path=expected, target_path=artifact)
        contract = read(self.task.paths.tests_dir/"request-contract.json")
        rewards = await asyncio.to_thread(self._score, artifact, self.task.instruction, contract, out)
        validate_bundle(self.bundle)
        return VerifierResult(rewards=rewards)

    def _score(self, artifact, request, contract, out):
        from svg_excellence import aggregate, collect, encode, make_evidence, read, sha, write
        from luna_svg_observer import observe
        from prepare_visual_excellence import visual_record
        from jev_batch import execute
        evidence = make_evidence(artifact.read_bytes(), request, contract, self.bundle/"fonts", out/"render.png")
        rubric = read(self.bundle/"rubric.json")
        if not evidence["artifact_valid"]:
            result = aggregate(evidence, {}, rubric)
        else:
            identity = sha(encode({"artifact": evidence["artifact_sha256"], "request": request}))[:20]
            prepared = out/"prepared"
            ep = prepared/"evidence"/(identity+".json")
            write(ep, evidence)
            (prepared/"renders").mkdir()
            (prepared/"renders"/(identity+".png")).write_bytes((out/"render.png").read_bytes())
            auth = {"openai-codex": read(Path(os.environ["FOX_PI_AUTH"]))["openai-codex"]}
            prompt = (self.bundle/"visual-observer-prompt.txt").read_text(encoding="utf-8")
            observe(prepared, identity, out/"observer", ["docker"], auth, prompt)
            observations = read(out/"observer"/identity/"observation.json")
            (prepared/"records.jsonl").write_bytes(encode(visual_record(evidence, observations, identity))+b"\n")
            write(prepared/"manifest.json", {"items": [{"id": identity, "artifact_valid": True, "evidence_sha256": sha(ep.read_bytes())}],
                  "records_sha256": sha((prepared/"records.jsonl").read_bytes())})
            execute(self.bundle/"job.json", [prepared/"records.jsonl"], out/"jev")
            completed = collect(prepared, out/"jev", out/"judgments.json", self.bundle/"rubric.json")
            if completed["observed_models"] != read(self.bundle/"lock.json")["observed_models"]:
                raise ValueError("Unexpected Jev version; recalibration required")
            result = completed["results"][0]
        write(out/"metrics.json", result | {"verifier_version": "3.0.0", "evaluator_lock_sha256": self.lock_sha256,
               "judge_model": "typesafe/jev-1.13", "visual_observer_model": "openai-codex/gpt-6-luna", "reference_similarity_used": False})
        if result["technical_excellence"] is None:
            raise ValueError("Judge needs review; no fabricated numeric reward")
        rewards = {"technical_excellence": result["technical_excellence"], "artifact_valid": float(evidence["artifact_valid"])}
        write(out/"reward.json", rewards)
        return rewards
