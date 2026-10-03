#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Trusted native Harbor verifier for professional SVG art direction."""
import asyncio
import re
import shlex
import sys
from pathlib import Path
from harbor.verifier.base import BaseVerifier
from harbor.models.verifier.result import VerifierResult


class SvgArtDirectionVerifier(BaseVerifier):
    def __init__(self,*args,evaluator_bundle,evaluator_lock_sha256,**kwargs):
        super().__init__(*args,**kwargs)
        self.bundle=Path(evaluator_bundle)
        self.lock_sha256=evaluator_lock_sha256

    def _validate(self):
        sys.path.insert(0,str(self.bundle/"scripts"))
        from svg_excellence import sha
        from evaluate_svg_jev import validate_bundle
        if sha((self.bundle/"lock.json").read_bytes())!=self.lock_sha256:
            raise ValueError("Art-direction evaluator lock drift")
        return validate_bundle(self.bundle)

    async def verify(self):
        self._validate()
        from svg_excellence import write
        matches=re.findall(r"`(/logs/artifacts/[^`]+\.svg)`",self.task.instruction)
        if len(set(matches))!=1:
            raise ValueError("Declare exactly one SVG output path")
        expected=matches[0]
        out=self.trial_paths.verifier_dir;out.mkdir(parents=True,exist_ok=True)
        presence=await self.environment.exec(command="test -f "+shlex.quote(expected))
        if presence.return_code!=0:
            rewards={"artifact_valid":0.0,"professional_quality":0.0}
            write(out/"metrics.json",{"status":"artifact_failure","reason":"Required SVG missing"})
            write(out/"reward.json",rewards)
            return VerifierResult(rewards=rewards)
        artifact=out/"input.svg"
        await self.environment.download_file(source_path=expected,target_path=artifact)
        rewards=await asyncio.to_thread(self._score,artifact,self.task.instruction,out)
        self._validate()
        return VerifierResult(rewards=rewards)

    def _score(self,artifact,request,out):
        from svg_excellence import make_evidence,encode,read,sha,write
        from svg_art_direction import aggregate,judge_record,observe_art
        from art_direction_review import verified_decisions
        from jev_batch import execute
        evidence=make_evidence(artifact.read_bytes(),request,{},self.bundle/"fonts",out/"render.png")
        write(out/"evidence.json",evidence)
        if evidence["artifact_valid"]:
            critic_prompt=(self.bundle/"visual-critic-prompt.txt").read_text(encoding="utf-8")
            critique=observe_art(evidence,out/"render.png",out/"critic",critic_prompt)
            identity=sha(encode({"artifact":evidence["artifact_sha256"],"request":request}))[:20]
            records=out/"records.jsonl";records.write_bytes(encode(judge_record(evidence,critique,identity))+b"\n")
            execute(self.bundle/"job.json",[records],out/"jev")
            decisions,models=verified_decisions(out/"jev",records)
            if models!=read(self.bundle/"lock.json")["observed_models"]:
                raise ValueError("Unexpected Jev model version")
            result=aggregate(decisions[identity]["decisions"])
        else:
            result=aggregate({},False)
        write(out/"metrics.json",result|{"verifier_version":"4.0.0","evaluator_lock_sha256":self.lock_sha256,"reference_artwork_supplied":False})
        if result["professional_quality"] is None:
            raise ValueError("Art-direction evidence is inconclusive; no fabricated reward")
        rewards={"artifact_valid":float(evidence["artifact_valid"]),"professional_quality":result["professional_quality"]}
        write(out/"reward.json",rewards)
        return rewards
