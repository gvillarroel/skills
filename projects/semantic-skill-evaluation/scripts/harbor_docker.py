#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Native Harbor Docker executor with one runtime skill and audited boundaries.

Run Harbor on WSL. Only the standard Pi auth file is blindly provisioned into
each disposable container; its contents never enter configuration or reports.
Native Harbor remains the owner of task locks, trials, verifier rewards and jobs.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess

from harbor.agents.installed.base import NonZeroAgentExitCodeError, with_prompt_template
from harbor.agents.installed.pi import Pi
from harbor.environments.docker.docker import DockerEnvironment


BASE_TAG = "semantic-skill-eval-pi:1.4.0-20261102"
BASE_ID = "sha256:7a550551f59503302644eb8a2887b51261e0c7c58bd86fab2bd3477b1ce4ee04"
MODEL = "openai-codex/gpt-6.1-sol"
SKILL = "curate-semantic-model"

# Evaluator-only transport. It runs after Pi exits, never appears in its prompt,
# and changes neither the workspace nor the verifier's reward contract.
WORKSPACE_EXPORT_CODE = r'''import hashlib,json,os,stat
from pathlib import Path
source = Path('/workspace')
destination = Path('/logs/artifacts/workspace')
report = {'schema_version':1,'source':str(source),'destination':str(destination),
          'purpose':'non-scoring final workspace evidence','status':'failed',
          'file_sha256':{},'file_bytes':{},'skipped':[],'errors':[]}
def visit(source_fd,target,relative):
 for entry in sorted(os.scandir(source_fd),key=lambda entry:entry.name):
  name = (relative / entry.name).as_posix()
  try:
   info = entry.stat(follow_symlinks=False)
   if stat.S_ISLNK(info.st_mode):
    report['skipped'].append({'path':name,'reason':'symlink'})
   elif stat.S_ISDIR(info.st_mode):
    child_fd = os.open(entry.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=source_fd)
    try:
     child_target = target / entry.name
     child_target.mkdir(mode=0o700)
     visit(child_fd,child_target,relative / entry.name)
    finally: os.close(child_fd)
   elif stat.S_ISREG(info.st_mode):
    input_fd = os.open(entry.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=source_fd)
    try:
     assert stat.S_ISREG(os.fstat(input_fd).st_mode),'Source changed to a non-regular file'
     output_fd = os.open(target / entry.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
     digest = hashlib.sha256()
     size = 0
     with os.fdopen(output_fd,'wb') as writer:
      while chunk := os.read(input_fd,1024*1024):
       writer.write(chunk)
       digest.update(chunk)
       size += len(chunk)
     report['file_sha256'][name] = digest.hexdigest()
     report['file_bytes'][name] = size
    finally: os.close(input_fd)
   else: report['skipped'].append({'path':name,'reason':'non-regular file'})
  except Exception as error:
   report['errors'].append({'path':name,'error_type':type(error).__name__,'error':str(error)})
try:
 assert not source.is_symlink(),'Workspace root is a symlink'
 assert destination.parent.is_dir() and not destination.parent.is_symlink(),'Artifact mount is unavailable or linked'
 assert all(not parent.is_symlink() for parent in destination.parents),'Artifact parent is linked'
 source_fd = os.open(source,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  # Refuse an existing destination, including dangling links. Never overwrite
  # actor-created artifacts or follow their links into another directory.
  destination.mkdir(mode=0o700)
  visit(source_fd,destination,Path('.'))
 finally: os.close(source_fd)
 report['status'] = 'partial' if report['errors'] else 'ok'
except Exception as error:
 report['errors'].append({'path':'.','error_type':type(error).__name__,'error':str(error)})
report['file_count'] = len(report['file_sha256'])
report['total_bytes'] = sum(report['file_bytes'].values())
print(json.dumps(report,sort_keys=True))
'''


def event_helpers():
    path = Path(__file__).resolve().parents[3] / "scripts/run-pi-skill-eval.py"
    spec = importlib.util.spec_from_file_location("semantic_docker_pi_policy", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SemanticDockerEnvironment(DockerEnvironment):
    def __init__(self, pi_auth_source: str, blocked_host_paths: list[str], expected_base_image: str = BASE_ID, **kwargs):
        self._auth_source = Path(pi_auth_source).resolve()
        self._blocked_paths = [str(Path(path).resolve()) for path in blocked_host_paths]
        self._expected_base = expected_base_image
        if not self._auth_source.is_file():
            raise FileNotFoundError("Standard Pi authentication source is unavailable")
        if expected_base_image != BASE_ID or not self._blocked_paths:
            raise ValueError("The study must bind its exact base image and blocked host paths")
        if not all(Path(path).exists() for path in self._blocked_paths):
            raise FileNotFoundError("Every denied-access host control must actually exist")
        persistent = kwargs.pop("persistent_env", None) or {}
        super().__init__(persistent_env={
            "HARBOR_APP_DIR": "/workspace", "HARBOR_TEST_DIR": "/tests",
            "HARBOR_VERIFIER_LOG_DIR": "/logs/verifier", "HARBOR_ARTIFACT_DIR": "/logs/artifacts",
            "PYTHONDONTWRITEBYTECODE": "1", **persistent,
        }, **kwargs)

    async def start(self, force_build: bool = False) -> None:
        image = subprocess.run(["docker", "image", "inspect", BASE_TAG, "--format", "{{.Id}}"], check=True, capture_output=True, text=True, timeout=30).stdout.strip()
        dockerfile = (self.environment_dir / "Dockerfile").read_text(encoding="utf-8")
        from_lines = [line.split() for line in dockerfile.splitlines() if line.strip().upper().startswith("FROM ")]
        if image != self._expected_base or not from_lines or from_lines[0][1] not in {self._expected_base, BASE_TAG}:
            raise RuntimeError("Docker base identity drift or an unpinned task Dockerfile")
        await super().start(force_build=force_build)
        result = await self.exec("install -d -m 700 /root/.pi/agent")
        if result.return_code:
            raise RuntimeError("Could not prepare the native Pi authentication directory")
        await self.upload_file(self._auth_source, "/root/.pi/agent/auth.json")
        await self.exec("chmod 600 /root/.pi/agent/auth.json")
        probe_code = """from pathlib import Path
import json,os
targets = %r
visibility = {path: Path(path).exists() for path in targets}
tests = Path('/tests')
private_tests_present = tests.exists() and any(tests.iterdir())
result = {'agent_uid': os.getuid(), 'blocked_host_paths_visible': visibility,
          'all_declared_host_controls_absent': not any(visibility.values()),
          'docker_socket_absent': not Path('/var/run/docker.sock').exists(),
          'private_tests_absent_before_agent': not private_tests_present,
          'auth_source': 'standard Pi auth file, blindly copied; contents not inspected'}
print(json.dumps(result))
assert result['all_declared_host_controls_absent'] and result['docker_socket_absent'] and result['private_tests_absent_before_agent']
""" % self._blocked_paths
        probe = await self.exec("python3 -c " + shlex.quote(probe_code))
        self.trial_paths.agent_dir.mkdir(parents=True, exist_ok=True)
        (self.trial_paths.agent_dir / "access-isolation-probe.json").write_text(probe.stdout, encoding="utf-8")
        if probe.return_code:
            raise RuntimeError("Actual trial container failed its denied-access controls")
        # Query the actual native trial container rather than inferring mounts
        # from an earlier readiness container or a template.
        identity = await self._run_docker_compose_command(["ps", "-q", "main"])
        container = identity.stdout.strip()
        if not container or "\n" in container:
            raise RuntimeError("Could not identify the one native trial container")
        actual = json.loads(subprocess.run(["docker", "inspect", container], check=True, capture_output=True, text=True, timeout=30).stdout)[0]
        mounts = actual.get("Mounts", [])
        allowed_destinations = {"/logs", "/logs/agent", "/logs/verifier", "/logs/artifacts"}
        trial_root = self.trial_paths.trial_dir.resolve()
        for mount in mounts:
            source = Path(mount.get("Source", "")).resolve()
            if mount.get("Destination") not in allowed_destinations or (source != trial_root and trial_root not in source.parents):
                raise RuntimeError("Native trial exposes an undeclared mount")
        metadata = {"base_image_id": image, "container_id": actual["Id"], "container_image_id": actual["Image"], "mounts": mounts, "configured_user": actual.get("Config", {}).get("User"), "workspace": "/workspace"}
        (self.trial_paths.agent_dir / "container-boundary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


class VirtualContainerTrace:
    """Present a raw trace to the existing policy using container path semantics."""
    parent = Path("/")

    def __init__(self, source: Path):
        self.source = source

    def read_text(self, **kwargs):
        return self.source.read_text(**kwargs)


class SemanticDockerPi(Pi):
    @staticmethod
    def name() -> str:
        return "semantic-docker-pi"

    async def install(self, environment) -> None:
        version = await self.exec_as_agent(environment, command="pi --version")
        if version.return_code or version.stdout.strip() != "1.4.0":
            raise RuntimeError("The study image must contain exactly Pi 1.4.0")

    async def _export_workspace_artifacts(self, environment) -> None:
        """Retain final files through Harbor's existing convention mount.

        Export failures are evidence-transport diagnostics, never skill rewards
        or execution gates. Native Harbor still collects the convention mount
        on normal completion and on its exception-recovery path.
        """
        report = {"schema_version": 1, "status": "failed", "purpose": "non-scoring final workspace evidence"}
        try:
            result = await environment.exec(
                "python3 -c " + shlex.quote(WORKSPACE_EXPORT_CODE), timeout_sec=60,
            )
            parsed = json.loads(result.stdout)
            if not isinstance(parsed, dict):
                raise ValueError("Workspace export receipt must be a JSON object")
            report = parsed
            report["transport_return_code"] = result.return_code
        except Exception as error:
            report["transport_error_type"] = type(error).__name__
            report["transport_error"] = str(error)[:1000]
        encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
        # Write receipts from the evaluator, outside the actor's process. The
        # second copy accompanies the files in the native mounted artifacts.
        for path in (self.logs_dir / "workspace-artifact-export.json",
                     environment.trial_paths.artifacts_dir / "workspace-sha256.json"):
            try:
                # An actor-created symlink must never redirect a host write.
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    stream.write(encoded)
            except OSError:
                # The other receipt and native raw evidence remain available;
                # transport does not change a semantic result.
                pass

    @with_prompt_template
    async def run(self, instruction, environment, context) -> None:
        del context
        if self.model_name != MODEL or self.skills_dir != "/harbor/skills":
            raise ValueError("The study freezes its model and native Harbor skill staging path")
        helpers = event_helpers()
        launcher = helpers.build_launcher_prompt(SKILL)
        setup_code = """from pathlib import Path
import hashlib,json,shutil
source_parent = Path('/harbor/skills')
source = source_parent / 'curate-semantic-model'
destination = Path('/workspace/skills/curate-semantic-model')
assert sorted(path.name for path in source_parent.iterdir()) == ['curate-semantic-model']
assert (source / 'SKILL.md').is_file() and not destination.exists()
def snapshot(root):
 result = {}
 for path in sorted(root.rglob('*')):
  assert not path.is_symlink(), 'Payload links are forbidden'
  if path.is_file(): result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
 return result
full = snapshot(source)
ignored = {'node_modules','__pycache__','.git','.cache','.venv','.pytest_cache','dist','output'}
def ignore(directory,names):
 excluded = set(names) & ignored
 if Path(directory).relative_to(source).as_posix() == 'assets': excluded |= set(names) & {'examples'}
 return excluded
shutil.copytree(source,destination,ignore=ignore)
runtime = snapshot(destination)
assert not (destination / 'assets/examples').exists()
Path('/prompt.md').write_text(%r,encoding='utf-8')
report = {'profile':'runtime','logical_skill':'curate-semantic-model','full_staged_file_sha256':full,'runtime_file_sha256':runtime,'task_prompt_sha256':hashlib.sha256(Path('/prompt.md').read_bytes()).hexdigest(),'full_staging_removed_before_agent':True}
Path('/logs/agent/runtime-payload.json').write_text(json.dumps(report,indent=2)+'\\n',encoding='utf-8')
assert source.resolve() == Path('/harbor/skills/curate-semantic-model')
shutil.rmtree(source)
assert not source.exists()
""" % instruction
        setup = await self.exec_as_agent(environment, command="python3 -c " + shlex.quote(setup_code))
        if setup.return_code:
            raise RuntimeError("Runtime derivation failed: " + setup.stderr[-1000:])
        provenance = {"task_prompt_sha256": hashlib.sha256(instruction.encode()).hexdigest(), "launcher_sha256": hashlib.sha256(launcher.encode()).hexdigest(), "loading_policy": "Exactly one explicit runtime skill, ambient discovery disabled; first completed read ../prompt.md"}
        (self.logs_dir / "prompt-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        command = "cd /workspace && pi --print --mode json --no-session --no-context-files --no-extensions --no-skills --skill skills/curate-semantic-model --no-prompt-templates --no-themes --no-mcp --model " + shlex.quote(MODEL) + " --thinking medium " + shlex.quote(launcher) + " > /logs/agent/pi.txt 2> /logs/agent/pi-stderr.txt"
        try:
            result = await self.exec_as_agent(environment, command=command)
        finally:
            await self._export_workspace_artifacts(environment)
        integrity_code = """from pathlib import Path
import hashlib,json
root = Path('/workspace/skills/curate-semantic-model')
actual = {}
for path in sorted(root.rglob('*')):
 assert not path.is_symlink(), 'Payload links are forbidden'
 if path.is_file(): actual[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
before = json.loads(Path('/logs/agent/runtime-payload.json').read_text())['runtime_file_sha256']
report = {'unchanged':before==actual,'before':before,'after':actual}
Path('/logs/agent/runtime-integrity.json').write_text(json.dumps(report,indent=2)+'\\n')
assert report['unchanged'], 'The read-only runtime skill changed'
"""
        integrity = await self.exec_as_agent(environment, command="python3 -c " + shlex.quote(integrity_code))
        events = self.logs_dir / self._OUTPUT_FILENAME
        report = helpers.event_check_report(
            events_path=VirtualContainerTrace(events), prompt=instruction,
            require_prompt_read_first=True, require_exact_command_from_prompt=False,
            require_observed_model=True, requested_model=MODEL,
            fail_on_invalid_json=True, fail_on_tool_error=True,
            forbid_read_regex=helpers.strict_forbidden_read_patterns(SKILL, "runtime"),
            forbid_command_regex=[],
        )
        errors = []
        for line in events.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = event.get("message") or {}
            if event.get("type") == "message_end" and message.get("role") == "assistant" and message.get("stopReason") == "error":
                errors.append("assistant-stopReason-error")
        report["raw_events_sha256"] = hashlib.sha256(events.read_bytes()).hexdigest()
        report["assistant_errors"] = errors
        report["policy_owner"] = "scripts/run-pi-skill-eval.py event_check_report and strict_forbidden_read_patterns"
        report["path_normalization"] = "Container /workspace and /prompt.md; unmodified raw events"
        report["supplementary_shell_review_required"] = True
        report["passed"] = report["passed"] and not errors and not result.return_code and not integrity.return_code
        (self.logs_dir / "trace-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if errors:
            diagnostic = {"status": "error", "failure_domain": "provider", "terminal_outcome": "non-evaluable", "error_code": "provider-assistant-error", "evidence": "agent/pi.txt and agent/trace-check.json"}
            await environment.exec("python3 -c " + shlex.quote("from pathlib import Path; Path('/logs/verifier/diagnostics.json').write_text(" + repr(json.dumps(diagnostic)) + ")"))
        if not report["passed"]:
            # Native Harbor preserves this completed-agent failure and still
            # runs the unchanged verifier. Provider failures remain outside
            # semantic evaluation, retaining their diagnostic precedence.
            error_type = RuntimeError if errors else NonZeroAgentExitCodeError
            raise error_type("Native Pi failed a non-compensating execution, trace or payload gate; inspect retained native agent evidence")

    def populate_context_post_run(self, context) -> None:
        path = Path(__file__).with_name("harbor_pi_agent.py")
        spec = importlib.util.spec_from_file_location("semantic_usage_parser", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.SemanticWindowsPi.populate_context_post_run(self, context)
