#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run ten bounded author/propose/evaluate slots; never activates a live candidate."""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid

ALLOWED = ("prompts/repo-custodian.md", "scripts/custodian.py", "src/tools/maintenance.ts")
MODEL = "gpt-6.1-sol"
PROVIDER = "openai-codex"
AST_COMMAND = "python -c \"import ast,pathlib;ast.parse(pathlib.Path('scripts/custodian.py').read_text(encoding='utf-8'));print('AST syntax OK')\""
PROTECTED = {"repo", "inventory", "scan", "tree_blobs", "fingerprint", "commands", "excluded",
             "remote", "maintain", "publish", "finish_merge", "conflict", "run", "environment"}
MUTABLE = {"inspect", "validate", "operation_event", "main"}
OPERATORS = [
    ("inspect-branch-upstream", "Add observed branch and existing upstream {remote,ref} to inspection. Preserve unknown/null without creating an upstream. Never return remote URLs."),
    ("typed-changes", "Add changes:[{path,status}] with tracked/untracked paths and spaces handled, plus changesTruncated. Preserve original status and bounded inspection."),
    ("inspection-not-run", "Make inspect explicitly state validationStatus:'not-run'; configured commands are not execution evidence."),
    ("validation-receipts", "Record actual successful trusted validation command receipts: commandIndex, commandSha256, exitCode, durationMs, status. Use validate/main/helpers only. No argv/stdout/stderr/environment exports."),
    ("publication-identities", "Add actual beforeHead/afterHead and remoteVerifiedSha only for verified pushed outcome. Main/helpers only; protected mutation functions remain exact. Clean no-op must have empty validationReceipts and validationStatus:'not-run', no invented verified push."),
    ("coded-validation-failure", "Give actual nonzero validation a stable validation_failed reasonCode and retained safe failure metadata. Preserve the same blocked mutation result and trusted command selection."),
    ("journal-receipts", "Extend only allowlisted operation_event metadata: branch/upstream, before/after SHA, verified remote SHA, safe validationReceipts and reasonCode. Never copy raw reasons, argv, stdout, stderr or credentials."),
    ("conditional-scope", "Append concise prompt guidance to apply conditional project requirements to observed changed scope; absent capability or evidence stays unknown. Never bypass required missing checks, security or fixed policy."),
    ("honest-coverage", "Append concise prompt guidance for receipt-grounded outcomes/coverage, material model-declared skip reasons, known versus unknown checks and source evidence. Do not inflate maintenance or push counts."),
    ("bounded-redaction", "Improve coherence and bounded safe metadata/redaction of the earlier permitted receipt helpers and prompt guidance. Preserve all original security/mutation functions and permissions; avoid raw diagnostic or credential export."),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def patch_digest(changes):
    return sha(canonical(sorted(changes, key=lambda value: value["path"])))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def redact(text):
    text = re.sub(r"\bBearer\s+[^\s\"'<>]+", "Bearer [REDACTED]", str(text), flags=re.I)
    text = re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-(?:ant-)?[A-Za-z0-9_-]{8,})\b", "[REDACTED]", text)
    return re.sub(r"((?:api[_-]?key|access[_-]?token|password|secret|authorization)\s*[=:]\s*)([^\s,;\"'<>]+)", r"\1[REDACTED]", text, flags=re.I)


def public_event(value):
    if isinstance(value, dict):
        kind = value.get("type", "")
        if isinstance(kind, str) and (kind in {"thinking", "reasoning", "redactedThinking"} or "thinking_" in kind or "reasoning_" in kind):
            return {"type": "private-content-omitted"}
        return {key: public_event(item) for key, item in value.items()
                if key.lower() not in {"thinking", "reasoning", "chain_of_thought", "encrypted_content", "thinkingsignature"}}
    if isinstance(value, list):
        return [public_event(item) for item in value]
    return redact(value) if isinstance(value, str) else value


def safe_environment():
    names = {"PATH", "PATHEXT", "SystemRoot", "WINDIR", "COMSPEC", "TEMP", "TMP", "HOME", "USERPROFILE",
             "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "LANG", "LC_ALL", "CODEX_HOME"}
    result = {key: value for key, value in os.environ.items() if key.upper() in {n.upper() for n in names}}
    result.update(PYTHONDONTWRITEBYTECODE="1", PI_TELEMETRY="0")
    return result


def run_command(argv, cwd, seconds, max_bytes=32 * 1024 * 1024):
    started = time.monotonic()
    child = subprocess.Popen(argv, cwd=cwd, env=safe_environment(), stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                             start_new_session=os.name != "nt")
    outputs = {"stdout": bytearray(), "stderr": bytearray()}
    overflow = threading.Event()
    kill_lock = threading.Lock()

    def stop():
        with kill_lock:
            if child.poll() is not None:
                return
            if os.name == "nt":
                subprocess.run(["taskkill.exe", "/PID", str(child.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
                               creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            else:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def collect(name, stream):
        while chunk := stream.read(8192):
            if len(outputs[name]) + len(chunk) > max_bytes:
                overflow.set()
                stop()
                break
            outputs[name].extend(chunk)

    threads = [threading.Thread(target=collect, args=(name, getattr(child, name)), daemon=True) for name in outputs]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        child.wait(timeout=max(0.1, seconds))
    except subprocess.TimeoutExpired:
        timed_out = True
        stop()
        child.wait(timeout=15)
    except BaseException:
        stop()
        raise
    finally:
        for thread in threads:
            thread.join(timeout=2)
        child.stdout.close()
        child.stderr.close()
    return {"returnCode": child.returncode, "timedOut": timed_out, "overflow": overflow.is_set(),
            "durationSeconds": round(time.monotonic() - started, 3),
            "stdout": bytes(outputs["stdout"]).decode("utf-8", "replace"),
            "stderr": bytes(outputs["stderr"]).decode("utf-8", "replace")}


def normalized(value):
    return value.replace("\r\n", "\n")


def python_scope(baseline, candidate):
    original, changed = ast.parse(baseline), ast.parse(candidate)

    def functions(tree):
        return {((parent.name + ".") if isinstance(parent, ast.ClassDef) else "") + node.name: node
                for parent in [tree, *[n for n in tree.body if isinstance(n, ast.ClassDef)]]
                for node in parent.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    before, after = functions(original), functions(changed)
    for name, node in before.items():
        leaf = name.rsplit(".", 1)[-1]
        if leaf in PROTECTED or (leaf not in MUTABLE and not name.startswith("Blocked.")):
            if name not in after or ast.dump(node, include_attributes=False) != ast.dump(after[name], include_attributes=False):
                raise ValueError("A protected worker function changed: " + name)
    globals_before = {ast.dump(node, include_attributes=False) for node in original.body if isinstance(node, (ast.Assign, ast.AnnAssign))}
    globals_after = {ast.dump(node, include_attributes=False) for node in changed.body if isinstance(node, (ast.Assign, ast.AnnAssign))}
    if not globals_before.issubset(globals_after):
        raise ValueError("An original worker global or security threshold changed.")
    bindings = {node.name for node in original.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    bindings.update(target.id for node in original.body if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name))
    before_assignments = [ast.dump(node, include_attributes=False) for node in original.body if isinstance(node, (ast.Assign, ast.AnnAssign))]
    for node in changed.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id in bindings for target in targets):
                encoded = ast.dump(node, include_attributes=False)
                if encoded not in before_assignments or sum(ast.dump(other, include_attributes=False) == encoded for other in changed.body if isinstance(other, (ast.Assign, ast.AnnAssign))) != before_assignments.count(encoded):
                    raise ValueError("A protected global/function binding was shadowed.")
    for name in after.keys() - before.keys():
        if name.rsplit(".", 1)[-1] in PROTECTED:
            raise ValueError("A new class/function overrides a protected worker operation.")
    for node in ast.walk(changed):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Attribute) and target.attr in PROTECTED for target in targets):
                raise ValueError("A protected worker method was monkeypatched.")
    original_classes = {node.name: node for node in original.body if isinstance(node, ast.ClassDef)}
    changed_classes = {node.name: node for node in changed.body if isinstance(node, ast.ClassDef)}
    for name, node in original_classes.items():
        if name not in changed_classes or ast.dump(ast.Tuple(elts=node.bases, ctx=ast.Load())) != ast.dump(ast.Tuple(elts=changed_classes[name].bases, ctx=ast.Load())):
            raise ValueError("A worker class security base changed.")
    old_imports = {ast.dump(node) for node in original.body if isinstance(node, (ast.Import, ast.ImportFrom))}
    new_imports = {ast.dump(node) for node in changed.body if isinstance(node, (ast.Import, ast.ImportFrom))}
    if not old_imports.issubset(new_imports):
        raise ValueError("An original worker import changed.")
    allowed_new_imports = {"uuid", "typing", "datetime", "math", "collections", "dataclasses"}
    for node in changed.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)) and ast.dump(node) not in old_imports:
            names = [alias.name.split(".")[0] for alias in node.names] if isinstance(node, ast.Import) else [str(node.module).split(".")[0]]
            if not set(names).issubset(allowed_new_imports):
                raise ValueError("A new worker import is outside receipt metadata scope.")
    for node in ast.walk(changed):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            raise ValueError("Dynamic worker code execution is prohibited.")
    return {"protectedFunctions": len([name for name in before if name.rsplit(".", 1)[-1] in PROTECTED]),
            "existingOtherFunctionsPreserved": True, "originalGlobalsPreserved": True}


def tool_scope(baseline, candidate):
    pattern = re.compile(r"\bdescription\s*:\s*(?P<quote>['\"`])(?:\\.|(?!(?P=quote))[\s\S])*?(?P=quote)")
    before, after = list(pattern.finditer(baseline)), list(pattern.finditer(candidate))
    if len(before) != 1 or len(after) != 1 or "${" in after[0].group():
        raise ValueError("The tool must retain one static plain description literal.")
    if normalized(pattern.sub("description:<STATIC>", baseline)) != normalized(pattern.sub("description:<STATIC>", candidate)):
        raise ValueError("The existing tool changed outside its description.")
    return {"descriptionOnly": True}


def scope_guard(baseline, candidate):
    if not normalized(candidate[ALLOWED[0]]).startswith(normalized(baseline[ALLOWED[0]]).rstrip("\n")):
        raise ValueError("The original prompt permission prefix was not preserved.")
    return {"promptPrefixPreserved": True, "lineEndingNormalizationAllowed": True,
            "worker": python_scope(baseline[ALLOWED[1]], candidate[ALLOWED[1]]),
            "tool": tool_scope(baseline[ALLOWED[2]], candidate[ALLOWED[2]])}


def trace_check(stdout, workspace):
    events, invalid = [], 0
    models, providers, calls, starts, last_text = set(), set(), [], {}, ""
    findings = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError()
        except (ValueError, json.JSONDecodeError):
            invalid += 1
            continue
        events.append(public_event(event))
        if event.get("type") == "message_end" and isinstance(event.get("message"), dict):
            message = event["message"]
            if message.get("role") == "assistant":
                models.add(message.get("model")); providers.add(message.get("provider"))
                last_text = "\n".join(block.get("text", "") for block in message.get("content", []) if block.get("type") == "text")
        if event.get("type") == "tool_execution_start":
            starts[str(event.get("toolCallId", ""))] = event
        if event.get("type") == "tool_execution_end":
            start = starts.get(str(event.get("toolCallId", "")), {})
            arguments = start.get("args", {})
            name = event.get("toolName", start.get("toolName"))
            path = next((arguments[key] for key in ("path", "file", "filePath", "target") if isinstance(arguments.get(key), str)), None)
            command = arguments.get("command")
            if name not in {"read", "write", "edit", "bash"}:
                findings.append("unexpected-tool")
            if path:
                target = Path(path) if Path(path).is_absolute() else workspace / path
                try:
                    local = target.resolve().relative_to(workspace.resolve()).as_posix()
                except ValueError:
                    local = "[outside-author-workspace]"
                if local not in ALLOWED:
                    findings.append("outside-allowed-file")
            else:
                local = None
            if isinstance(command, str) and (name != "bash" or command.strip() != AST_COMMAND):
                findings.append("forbidden-author-command")
            if event.get("isError"):
                findings.append("tool-error")
            calls.append({"tool": name, "path": local, "command": redact(command)[:1000] if isinstance(command, str) else None,
                          "isError": bool(event.get("isError"))})
    if invalid:
        findings.append("invalid-json-events")
    if models != {MODEL} or providers != {PROVIDER}:
        findings.append("observed-model-mismatch")
    if not calls:
        findings.append("no-observed-tools")
    return events, {"passed": not findings, "invalidJsonLines": invalid, "models": sorted(str(x) for x in models),
                    "providers": sorted(str(x) for x in providers), "calls": calls, "findings": findings,
                    "limitations": "Post-execution trace checks and filesystem scope; normal host tools are not an OS sandbox."}, last_text


def public_metadata(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    value = json.loads(text)
    if value.get("candidate") is None and "candidate" in value:
        return None
    for key in ("hypothesis", "decision", "expectedBenefit"):
        if not isinstance(value.get(key), str) or not 1 <= len(value[key]) <= 4000:
            raise ValueError("Author public metadata is missing or oversized.")
    risks = value.get("regressionRisks")
    if not isinstance(risks, list) or len(risks) > 20 or any(not isinstance(item, str) or len(item) > 1000 for item in risks):
        raise ValueError("Author public regression risks are invalid.")
    return {key: value[key] for key in ("hypothesis", "decision", "expectedBenefit", "regressionRisks")}


def source_guard(project, request, config_path):
    for record in request["source"]:
        path = (project / record["path"]).resolve()
        if not path.is_relative_to(project.resolve()) or not path.is_file() or sha(path.read_bytes()) != record["sha256"]:
            raise ValueError("Frozen live source drift: " + record["path"])
    if sha(config_path.read_bytes()) != request["configDigest"]:
        raise ValueError("Frozen study configuration changed.")
    for record in request["frozenVerifier"]:
        if sha((project / record["path"]).read_bytes()) != record["sha256"]:
            raise ValueError("Frozen development evaluator changed.")


def author_task(operator, baseline, seed, feedback):
    return f"""You are authoring one bounded candidate for an independent repository custodian.
Work only in this author workspace. The only readable/editable files are:
{json.dumps(ALLOWED)}
Do not read parent directories, evaluator/fixtures/grades, services, state,
credentials or environment. Do not run Git, network, package installation,
providers, another model, services or any repository maintenance. Use read/edit/
write tools for those three files. The only permitted Bash command is this exact
stdlib ast/pathlib parse, which does not import/execute the candidate or create
bytecode: {AST_COMMAND}
Do not use Bash/heredocs for editing. No new files are permitted.

Current operator {operator[0]}: {operator[1]}
Seed: {seed}. Retain earlier useful changes when coherent. The immutable paired
baseline is separate; never attempt to alter it. Existing publication/security
permissions, all protected worker mutation/safety functions, policy selection,
validation/scanner gates, thresholds, scopes and destination rules must remain.
Keep the original prompt as a prefix and only append concise relevant guidance.
In maintenance.ts only the static tool description may change; parameters,
execute, timeout, no replay and stderr suppression remain exact.
Worker changes may affect inspect, validate, operation_event, main, Blocked
metadata or new receipt helpers. Preserve all existing other functions/globals.

Public receipt contract:
inspect branch and upstream {{remote,ref}} or null; changes:[{{path,status}}] plus
changesTruncated; inspect validationStatus:'not-run'. Maintenance beforeHead,
afterHead, remoteVerifiedSha only for verified actual pushed outcome.
validationReceipts:[{{commandIndex,commandSha256,exitCode,durationMs,status}}].
commandSha256 is SHA256 UTF8 compact JSON argv with ensure_ascii=False.
Record real observed results; never expose raw argv/stdout/stderr/environment.
Failure reasonCode vocabulary: validation_failed, validation_timeout,
validation_unavailable, validation_policy_missing. Keep blocked effects intact.
Journal additive fields must be explicitly allowlisted and bounded/redacted.
Clean no-op: empty validationReceipts, validationStatus:'not-run', equal before/
after heads and no invented verified push. Do not optimize push/maintain counts.

Public prior development feedback (not reserved validation):
{json.dumps(feedback,ensure_ascii=False)}

If a safe useful change cannot be made, leave files unchanged and return only
JSON {{"candidate":null,"reason":"brief public reason"}}. Otherwise return
only JSON {{"hypothesis":"observable hypothesis","decision":"chosen public
change","expectedBenefit":"bounded expectation","regressionRisks":["risk"]}}.
Do not include private reasoning or thinking. A proposal activates nothing.
"""


def evaluate_native(argv, project, folder, label, seconds):
    result = run_command(argv, project, seconds, max_bytes=4 * 1024 * 1024)
    summary = {key: result[key] for key in ("returnCode", "timedOut", "overflow", "durationSeconds")}
    summary["stderrBytes"] = len(result["stderr"].encode())
    write_json(folder / (label + ".process.json"), summary)
    if result["returnCode"] or result["timedOut"] or result["overflow"]:
        (folder / (label + ".stderr.redacted.txt")).write_text(redact(result["stderr"])[:10000], encoding="utf-8")
        raise RuntimeError("Native " + label + " failed; inspect retained bounded diagnostics.")
    value = json.loads(result["stdout"])
    write_json(folder / (label + ".json"), public_event(value))
    return value


@contextmanager
def driver_lock(artifacts):
    path = artifacts / "development-driver.lock"
    token = uuid.uuid4().hex
    record = {"pid": os.getpid(), "parentPid": os.getppid(), "token": token, "startedAt": now()}
    try:
        write_json(path, record, exclusive=True)
    except FileExistsError:
        raise ValueError("A driver lock exists. Verify its exact owner/children before explicit recovery.") from None
    try:
        yield
    finally:
        if path.is_file() and read_json(path).get("token") == token:
            path.unlink()


def run_study(args):
    project, artifacts = args.project.resolve(strict=True), args.artifacts.resolve()
    config_path = project / args.config
    request = read_json(args.request_file)
    if request["id"] != "custodian-evo10-development-20261025" or set(request["allowedPaths"]) != set(ALLOWED):
        raise ValueError("Unexpected immutable development request or scope.")
    if read_json(args.preflight_file).get("passed") is not True:
        raise ValueError("Native preflight has not passed; no development may start.")
    config = read_json(config_path)
    if config["provider"]["model"] != MODEL or config["provider"].get("thinkingLevel") != "medium" or not config["provider"].get("catalogFile"):
        raise ValueError("Exact Sol 6.1/medium with frozen catalog is required.")
    source_guard(project, request, config_path)
    baseline = {path: (project / path).read_bytes().decode("utf-8") for path in ALLOWED}
    artifacts.mkdir(parents=True, exist_ok=True)
    if not args.start:
        return {"started": False, "slots": 10, "operators": [item[0] for item in OPERATORS], "automaticActivation": False}
    with driver_lock(artifacts):
        ledger = artifacts / "development-ledger.jsonl"
        history = [json.loads(line) for line in ledger.read_text().splitlines()] if ledger.is_file() else []
        if history and not args.resume:
            raise ValueError("A study ledger already exists; explicit resume never rerolls started slots.")
        starts = [event for event in history if event.get("event") == "started"]
        finished = [event for event in history if event.get("event") == "finished"]
        start_epoch = starts[0]["startedEpoch"] if starts else time.time()
        qualified = [event for event in finished if event.get("qualified")]
        best = sorted(qualified, key=lambda item: (-item["candidateScore"], item["patchDigest"]))[0] if qualified else None

        def append(value):
            with ledger.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(value, ensure_ascii=False) + "\n");stream.flush();os.fsync(stream.fileno())

        started_slots = {event["slot"] for event in starts}
        finished_slots = {event["slot"] for event in finished}
        for started in starts:
            if started["slot"] not in finished_slots:
                abandoned = {"event": "finished", "slot": started["slot"], "operator": started["operator"],
                             "seed": started["seed"], "qualified": False, "outcome": "abandoned-after-explicit-recovery",
                             "finishedAt": now(), "errorCategory": "InterruptedDriver", "rerolled": False}
                append(abandoned);finished.append(abandoned)
        for slot in range(1, 11):
            if slot in started_slots:
                continue
            remaining = 7200 - (time.time() - start_epoch)
            if remaining <= 0:
                break
            operator = OPERATORS[slot - 1]
            folder = artifacts / "iterations" / f"i{slot:02}"
            folder.mkdir(parents=True, exist_ok=False)
            workspace = folder / "workspace";workspace.mkdir()
            seed = baseline.copy()
            seed_id = best["slot"] if best else "baseline"
            if best:
                previous = read_json(Path(best["candidatePath"]))
                for change in previous["changes"]:
                    seed[change["path"]] = change["content"]
            for path, content in seed.items():
                target = workspace / path;target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(content.encode("utf-8"))
            started = {"event": "started", "slot": slot, "operator": operator[0], "startedAt": now(),
                       "startedEpoch": start_epoch, "seed": seed_id, "seedPatchDigest": best["patchDigest"] if best else None,
                       "baselineRequestDigest": request["digest"], "maximumStartedSlots": 10}
            append(started)
            record = {"event": "finished", "slot": slot, "operator": operator[0], "seed": seed_id,
                      "qualified": False, "outcome": "failed", "finishedAt": None}
            try:
                source_guard(project, request, config_path)
                feedback = [{"slot": item["slot"], "operator": item["operator"], "outcome": item["outcome"],
                             "score": item.get("candidateScore"), "findings": item.get("feedback", [])} for item in finished[-3:]]
                task = author_task(operator, baseline, seed_id, feedback)
                (folder / "author-task.txt").write_text(task, encoding="utf-8")
                node = shutil.which("node") or "node"
                command = [node, config["provider"]["piCliPath"], "--model", PROVIDER + "/" + MODEL,
                           "--thinking", "medium", "--mode", "json", "--no-context-files", "--no-extensions",
                           "--no-mcp", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session",
                           "--tools", "read,edit,write,bash", "--print", task]
                result = run_command(command, workspace, min(300, remaining))
                events, trace, final = trace_check(result["stdout"], workspace)
                (folder / "author-events.public.jsonl").write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")
                write_json(folder / "author-trace-check.json", trace)
                write_json(folder / "author-process.json", {key: result[key] for key in ("returnCode", "timedOut", "overflow", "durationSeconds")})
                if result["returnCode"] or result["timedOut"] or result["overflow"] or not trace["passed"]:
                    record["feedback"] = trace["findings"]
                    raise ValueError("Author process/trace gate failed.")
                metadata = public_metadata(final)
                files = {path.relative_to(workspace).as_posix(): path for path in workspace.rglob("*") if path.is_file()}
                if set(files) != set(ALLOWED) or any(path.is_symlink() for path in workspace.rglob("*")):
                    raise ValueError("Author changed the allowed filesystem surface.")
                candidate = {path: files[path].read_bytes().decode("utf-8") for path in ALLOWED}
                record["scopeCheck"] = scope_guard(baseline, candidate)
                source_guard(project, request, config_path)
                changes = [{"path": path, "beforeHash": sha(baseline[path].encode()), "content": candidate[path]}
                           for path in ALLOWED if candidate[path] != baseline[path]]
                if metadata is None or not changes:
                    record["outcome"] = "null"
                else:
                    proposal = {"requestId": request["id"], "evidenceIds": [item["id"] for item in request["evidence"]],
                                **metadata, "changes": changes}
                    candidate_path = folder / "candidate.json";write_json(candidate_path, proposal, exclusive=True)
                    digest = patch_digest(changes)
                    record.update(patchDigest=digest, candidatePath=str(candidate_path))
                    if any(item.get("patchDigest") == digest for item in finished):
                        raise ValueError("Identical candidate patch already consumed a development attempt; no reroll/evaluation.")
                    cli = project / "dist/src/evolve-cli.js"
                    imported = evaluate_native([node, str(cli), "propose", "--config", str(config_path), "--request", request["id"], "--input", str(candidate_path)], project, folder, "proposal", min(60, remaining))
                    if imported.get("requestId") != request["id"] or patch_digest(imported["changes"]) != digest:
                        raise ValueError("Native imported proposal differs from the exact candidate.")
                    remaining = 7200 - (time.time() - start_epoch)
                    evaluated = evaluate_native([node, str(cli), "evaluate", "--config", str(config_path), "--proposal", imported["id"]], project, folder, "evaluation", min(750, remaining))
                    if evaluated.get("proposalId") != imported["id"]:
                        raise ValueError("Native evaluation identity mismatch.")
                    verification = evaluated.get("candidate", {}).get("verification") or {}
                    score = verification.get("score")
                    record.update(proposalId=imported["id"], evaluationDigest=evaluated.get("digest"),
                                  qualified=evaluated.get("passed") is True,
                                  candidateScore=score if type(score) in (int, float) else None,
                                  baselineScore=(evaluated.get("baseline", {}).get("verification") or {}).get("score"),
                                  outcome="qualified" if evaluated.get("passed") is True else "rejected",
                                  feedback=[{"id": case["id"], "passed": case["passed"], "score": case.get("score")}
                                            for case in verification.get("cases", []) if not case.get("passed") or case.get("score", 1) < 1])
                    if record["qualified"] and (type(score) not in (int, float) or not 0 <= score <= 1):
                        raise ValueError("Invalid qualified native score.")
                    if record["qualified"] and (best is None or (-score, digest) < (-best["candidateScore"], best["patchDigest"])):
                        best = record.copy()
            except Exception as error:
                record.update(qualified=False, outcome="failed", errorCategory=type(error).__name__,
                              error=redact(str(error))[:1000])
            finally:
                record["finishedAt"] = now();append(record);finished.append(record)
                if best and best["slot"] == slot:
                    best = record.copy()
                write_json(folder / "iteration-result.json", record)
                summary = {"version": 1, "startedSlots": len(started_slots) + 1, "finishedSlots": len(finished),
                           "maxSlots": 10, "best": best, "automaticActivation": False,
                           "wallSeconds": round(time.time() - start_epoch, 3), "iterations": finished}
                write_json(artifacts / "development-summary.json", summary)
                print(json.dumps({"slot": slot, "outcome": record["outcome"], "score": record.get("candidateScore"),
                                  "bestSlot": best["slot"] if best else None}), flush=True)
                started_slots.add(slot)
        summary = read_json(artifacts / "development-summary.json") if (artifacts / "development-summary.json").exists() else {"startedSlots": len(starts), "finishedSlots": len(finished), "best": best}
        summary.update(completedRequestedSlots=summary["startedSlots"] == 10, automaticActivation=False,
                       next="Root freezes one finalist and owns separate curator validation/holdout; no live activation occurred.")
        write_json(artifacts / "development-summary.json", summary)
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--config", default="config.evo10.json")
    parser.add_argument("--request-file", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--preflight-file", type=Path, required=True)
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    result = run_study(args)
    print(json.dumps({key: value for key, value in result.items() if key not in {"iterations", "best"}}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"started": False, "errorCategory": type(error).__name__, "error": redact(str(error))[:1000]}), file=sys.stderr)
        raise SystemExit(1)
