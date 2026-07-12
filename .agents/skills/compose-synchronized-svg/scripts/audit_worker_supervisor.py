#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Supervise one browser-audit worker without importing Playwright."""

from __future__ import annotations

import math
import os
import signal
import subprocess
import sys
import threading
from collections.abc import Callable
from typing import Any, NamedTuple, TextIO


PopenFactory = Callable[..., subprocess.Popen[str]]
MAX_ATTEMPT_TIMEOUT_SECONDS = min(3600.0, float(threading.TIMEOUT_MAX) * 0.9)


class WorkerAttempt(NamedTuple):
    """Captured outcome of one isolated audit-worker attempt."""

    timed_out: bool
    returncode: int
    stdout: str
    stderr: str


def configure_utf8_stream(stream: Any) -> None:
    """Configure a standard stream without assuming a real TextIOWrapper."""

    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")


def configure_utf8_standard_streams() -> None:
    """Make relayed worker diagnostics safe on Windows consoles."""

    configure_utf8_stream(sys.stdout)
    configure_utf8_stream(sys.stderr)


def configured_attempt_timeout() -> float:
    """Read the bounded per-attempt timeout used by the audit wrapper."""

    raw_timeout = os.environ.get("SYNC_SVG_AUDIT_ATTEMPT_TIMEOUT_SECONDS", "180")
    try:
        parsed = float(raw_timeout)
    except ValueError:
        return 180.0
    if not math.isfinite(parsed):
        return 180.0
    return min(MAX_ATTEMPT_TIMEOUT_SECONDS, max(30.0, parsed))


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _normalize_returncode(returncode: int | None) -> int:
    if returncode is None:
        return 1
    if returncode < 0:
        return 128 + abs(returncode)
    return int(returncode)


def worker_popen_options() -> dict[str, Any]:
    """Create one text-mode pipe contract and an isolated process group."""

    options: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        options["start_new_session"] = True
    return options


WINDOWS_JOB_HANDLE_ATTRIBUTE = "_sync_svg_kill_job_handle"


def attach_worker_containment(process: subprocess.Popen[str]) -> None:
    """Attach a Windows kill-on-close job before the worker imports Playwright."""

    if os.name != "nt":
        return
    process_handle = getattr(process, "_handle", None)
    if not isinstance(process_handle, int):
        return

    job_handle: int | None = None
    try:
        import ctypes
        from ctypes import wintypes

        class IoCounters(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class BasicLimitInformation(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class ExtendedLimitInformation(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", BasicLimitInformation),
                ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        raw_job_handle = kernel32.CreateJobObjectW(None, None)
        if not raw_job_handle:
            return
        job_handle = int(raw_job_handle)
        information = ExtendedLimitInformation()
        information.BasicLimitInformation.LimitFlags = 0x00002000
        configured = kernel32.SetInformationJobObject(
            wintypes.HANDLE(job_handle),
            9,
            ctypes.byref(information),
            ctypes.sizeof(information),
        )
        assigned = configured and kernel32.AssignProcessToJobObject(
            wintypes.HANDLE(job_handle),
            wintypes.HANDLE(process_handle),
        )
        if not assigned:
            kernel32.CloseHandle(wintypes.HANDLE(job_handle))
            return
        setattr(process, WINDOWS_JOB_HANDLE_ATTRIBUTE, job_handle)
    except (AttributeError, ImportError, OSError, TypeError, ValueError):
        if job_handle is not None:
            try:
                import ctypes
                from ctypes import wintypes

                ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(
                    wintypes.HANDLE(job_handle)
                )
            except (AttributeError, ImportError, OSError, TypeError, ValueError):
                pass


def close_worker_containment(process: subprocess.Popen[str]) -> None:
    """Kill any surviving descendants after a worker has exited or hung."""

    if os.name == "nt":
        job_handle = getattr(process, WINDOWS_JOB_HANDLE_ATTRIBUTE, None)
        if not isinstance(job_handle, int):
            return
        try:
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            kernel32.CloseHandle(wintypes.HANDLE(job_handle))
        except (AttributeError, ImportError, OSError, TypeError, ValueError):
            pass
        try:
            delattr(process, WINDOWS_JOB_HANDLE_ATTRIBUTE)
        except AttributeError:
            pass
        return

    process_id = getattr(process, "pid", None)
    if not isinstance(process_id, int) or process_id <= 0:
        return
    try:
        os.killpg(process_id, signal.SIGKILL)
    except (OSError, ProcessLookupError, PermissionError):
        pass


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    """Best-effort termination of a live audit worker process group."""

    close_worker_containment(process)
    if process.poll() is None:
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError:
                pass
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (OSError, ProcessLookupError, PermissionError):
                pass

    if process.poll() is None:
        try:
            process.kill()
        except (OSError, ProcessLookupError):
            pass


def terminate_and_drain(
    process: subprocess.Popen[str],
    timeout_error: subprocess.TimeoutExpired | None = None,
) -> tuple[str, str]:
    """Terminate a worker and drain both pipes without losing timeout output."""

    terminate_process_tree(process)
    stdout = ""
    stderr = ""
    try:
        drained_stdout, drained_stderr = process.communicate(timeout=5)
        stdout = _as_text(drained_stdout)
        stderr = _as_text(drained_stderr)
    except subprocess.TimeoutExpired as final_timeout:
        try:
            process.kill()
        except (OSError, ProcessLookupError):
            pass
        try:
            drained_stdout, drained_stderr = process.communicate(timeout=5)
            stdout = _as_text(drained_stdout)
            stderr = _as_text(drained_stderr)
        except (OSError, ValueError, subprocess.TimeoutExpired):
            stdout = _as_text(final_timeout.output)
            stderr = _as_text(final_timeout.stderr)
    except (OSError, ValueError):
        pass

    if timeout_error is not None:
        if not stdout:
            stdout = _as_text(timeout_error.output)
        if not stderr:
            stderr = _as_text(timeout_error.stderr)
    return stdout, stderr


def run_worker_attempt(
    command: list[str],
    timeout_seconds: float,
    *,
    popen_factory: PopenFactory | None = None,
) -> WorkerAttempt:
    """Run one worker, cleaning its process group on timeout or cancellation."""

    factory = popen_factory or subprocess.Popen
    process: subprocess.Popen[str] | None = None
    try:
        process = factory(command, **worker_popen_options())
        attach_worker_containment(process)
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as error:
            stdout, stderr = terminate_and_drain(process, error)
            return WorkerAttempt(True, 124, stdout, stderr)

        return WorkerAttempt(
            False,
            _normalize_returncode(process.returncode),
            _as_text(stdout),
            _as_text(stderr),
        )
    except BaseException:
        if process is not None:
            try:
                terminate_and_drain(process)
            except BaseException:
                pass
        raise
    finally:
        if process is not None:
            close_worker_containment(process)


def _install_termination_handlers() -> list[tuple[int, Any]]:
    """Turn termination signals into exceptions so cleanup can run."""

    previous: list[tuple[int, Any]] = []

    def raise_termination(signum: int, _frame: Any) -> None:
        raise SystemExit(128 + signum)

    candidates = [signal.SIGTERM]
    for signal_name in ("SIGHUP", "SIGBREAK"):
        candidate = getattr(signal, signal_name, None)
        if candidate is not None and candidate not in candidates:
            candidates.append(candidate)
    for candidate in candidates:
        try:
            old_handler = signal.getsignal(candidate)
            signal.signal(candidate, raise_termination)
        except (OSError, RuntimeError, ValueError):
            continue
        previous.append((candidate, old_handler))
    return previous


def _restore_termination_handlers(previous: list[tuple[int, Any]]) -> None:
    for candidate, old_handler in previous:
        try:
            signal.signal(candidate, old_handler)
        except (OSError, RuntimeError, ValueError):
            pass


def _write(stream: TextIO, value: str) -> None:
    if value:
        stream.write(value)
        stream.flush()


def supervise_worker(
    command: list[str],
    *,
    timeout_seconds: float | None = None,
    popen_factory: PopenFactory | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run at most two attempts while preserving real worker exit semantics."""

    if timeout_seconds is None:
        attempt_timeout = configured_attempt_timeout()
    else:
        attempt_timeout = float(timeout_seconds)
        if (
            not math.isfinite(attempt_timeout)
            or attempt_timeout <= 0
            or attempt_timeout > MAX_ATTEMPT_TIMEOUT_SECONDS
        ):
            raise ValueError(
                "timeout_seconds must be finite, greater than zero, and no more than "
                f"{MAX_ATTEMPT_TIMEOUT_SECONDS:g}"
            )
    output_stream = stdout or sys.stdout
    error_stream = stderr or sys.stderr
    timed_out_attempts: list[WorkerAttempt] = []
    previous_handlers = _install_termination_handlers()
    try:
        for attempt_index in range(2):
            result = run_worker_attempt(
                command,
                attempt_timeout,
                popen_factory=popen_factory,
            )
            if not result.timed_out:
                _write(output_stream, result.stdout)
                _write(error_stream, result.stderr)
                return result.returncode

            timed_out_attempts.append(result)
            if attempt_index == 0:
                print(
                    "Browser audit worker attempt 1 timed out; retrying once.",
                    file=error_stream,
                )
                continue

            for index, timed_out in enumerate(timed_out_attempts, start=1):
                if timed_out.stdout:
                    print(f"[browser-audit attempt {index} stdout]", file=error_stream)
                    _write(error_stream, timed_out.stdout)
                if timed_out.stderr:
                    print(f"[browser-audit attempt {index} stderr]", file=error_stream)
                    _write(error_stream, timed_out.stderr)
            print(
                "Browser audit worker timed out twice after "
                f"{attempt_timeout:g} seconds per attempt.",
                file=error_stream,
            )
            return 124
    finally:
        _restore_termination_handlers(previous_handlers)

    return 124
