#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Trusted-host Harbor adapter for the frozen purpose-specific technique evaluator."""
import asyncio
from pathlib import Path
import re
import shlex
import sys
from harbor.verifier.base import BaseVerifier
from harbor.models.verifier.result import VerifierResult


class SvgTechniqueVerifier(BaseVerifier):
    def __init__(self, *args, evaluator_bundle, evaluator_lock_sha256, **kwargs):
        super().__init__(*args, **kwargs)
        self.bundle = Path(evaluator_bundle)
        self.lock_sha256 = evaluator_lock_sha256

    def _validate(self):
        sys.path.insert(0,str(self.bundle / "scripts"))
        from svg_excellence import sha
        from evaluate_svg_jev import validate_bundle
        if sha((self.bundle / "lock.json").read_bytes()) != self.lock_sha256:
            raise ValueError("Evaluator lock changed")
        return validate_bundle(self.bundle)

    async def verify(self):
        self._validate()
        from svg_excellence import read, write
        paths = re.findall(r"`(/logs/artifacts/[^`]+\.svg)`", self.task.instruction)
        if len(set(paths)) != 1:
            raise ValueError("One exact SVG path required")
        out = self.trial_paths.verifier_dir
        out.mkdir(parents=True,exist_ok=True)
        present = await self.environment.exec(command="test -f " + shlex.quote(paths[0]))
        if present.return_code != 0:
            rewards = {"artifact_valid":0.0,"technique_quality":0.0}
            write(out / "reward.json", rewards)
            write(out / "metrics.json", {"status":"missing_artifact"})
        else:
            artifact = out / "input.svg"
            await self.environment.download_file(source_path=paths[0],target_path=artifact)
            spec = read(self.task.paths.tests_dir / "quality-anchor.json")
            rewards = await asyncio.to_thread(self._score, artifact, self.task.instruction, spec, out)
        self._validate()
        return VerifierResult(rewards=rewards)

    def _score(self, artifact, request, spec, out):
        from svg_excellence import read, write, sha, encode, make_evidence
        from svg_curated_pairs import observe_pair
        from svg_technique_review import judge_record
        from svg_technique_score import aggregate
        from art_direction_review import verified_decisions
        from jev_batch import execute
        from jev_transport import http_post
        from jev_contract import digest
        candidate = make_evidence(artifact.read_bytes(),request,{},self.bundle / "fonts",out / "candidate.png")
        write(out / "candidate-evidence.json",candidate)
        if not candidate["artifact_valid"]:
            rewards = {"artifact_valid":0.0,"technique_quality":0.0}
            write(out / "metrics.json",candidate); write(out / "reward.json",rewards)
            return rewards
        profiles = read(self.bundle / "use-profiles.json")
        profile = spec["profile"]
        if profile not in profiles:
            raise ValueError("Unknown declared use profile")
        anchor = (self.bundle / spec["file"]).resolve()
        if not anchor.is_relative_to(self.bundle.resolve()) or sha(anchor.read_bytes()) != spec["sha256"]:
            raise ValueError("Anchor identity mismatch")
        anchor_evidence = make_evidence(anchor.read_bytes(),request,{},self.bundle / "fonts",out / "anchor.png")
        if not anchor_evidence["artifact_valid"]:
            raise ValueError("Invalid evaluator anchor")
        first = int(candidate["artifact_sha256"][:2],16)%2 == 0
        side = "A" if first else "B"
        pair = {"brief":request.split("\n\n")[0],"A_render":out / ("candidate.png" if first else "anchor.png"),"B_render":out / ("anchor.png" if first else "candidate.png"),"A_sha256":candidate["artifact_sha256"] if first else spec["sha256"],"B_sha256":spec["sha256"] if first else candidate["artifact_sha256"]}
        template = (self.bundle / "observer-prompt.txt").read_text(encoding="utf-8") + "\n\nUSE PROFILE:\n" + profiles[profile]
        critique = observe_pair(pair,out / "critic",template)
        identity = sha(encode({"candidate":candidate["artifact_sha256"],"anchor":spec["sha256"],"request":request}))[:20]
        records = out / "records.jsonl"
        records.write_bytes(encode(judge_record(identity,pair["brief"],critique,profile)) + b"\n")
        def recorded(payload,key,timeout):
            status,headers,data = http_post(payload,key,timeout)
            if status == 200:
                with (out / ("provider-response-" + digest(payload) + ".json")).open("xb") as stream:
                    stream.write(data)
            return status,headers,data
        execute(self.bundle / "job.json",[records],out / "jev",post=recorded)
        decisions,models = verified_decisions(out / "jev",records)
        if models != read(self.bundle / "lock.json")["observed_models"]:
            raise ValueError("Jev version changed")
        result = aggregate(decisions[identity]["decisions"],side)
        write(out / "metrics.json",result | {"candidate_side":side,"use_profile":profile,"evaluator_lock_sha256":self.lock_sha256,"verifier_version":"6.3.0","pixel_similarity_used":False,"anchor_used_only_by_host_verifier":True})
        if result["technique_quality"] is None:
            raise ValueError("Insufficient evidence; no numeric reward")
        rewards = {"artifact_valid":1.0,"technique_quality":result["technique_quality"]}
        write(out / "reward.json",rewards)
        return rewards
