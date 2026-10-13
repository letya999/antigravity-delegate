#!/usr/bin/env python3
"""Run Antigravity (agy) once in headless print mode and capture its result."""

from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_bounded(
    command: list[str], cwd: Path, timeout: float, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run in a process group so a timeout can terminate the whole CLI tree."""
    group_options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True})
    process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", **group_options)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        exc.stdout, exc.stderr = stdout, stderr
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def parse_duration(value: str) -> float:
    value = value.strip().lower()
    units = {"s": 1, "m": 60, "h": 3600}
    if value[-1:] in units:
        seconds = float(value[:-1]) * units[value[-1]]
    else:
        seconds = float(value)
    if seconds <= 0:
        raise ValueError("timeout must be greater than zero")
    return seconds


def find_agy() -> str | None:
    explicit = os.environ.get("AGY_BIN")
    if explicit:
        return explicit
    found = shutil.which("agy")
    if found:
        return found
    localappdata = os.environ.get("LOCALAPPDATA")
    candidates = []
    if localappdata:
        candidates.extend([Path(localappdata) / "agy" / "bin" / "agy.exe", Path(localappdata) / "agy" / "bin" / "agy"])
    candidates.extend([Path.home() / ".agy" / "bin" / "agy.exe", Path.home() / ".agy" / "bin" / "agy"])
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def extract_response(payload: object) -> object:
    """Pull the human-facing result out of Antigravity's JSON envelope."""
    if isinstance(payload, dict):
        for key in ("result", "response", "content", "text", "output", "message"):
            if key in payload:
                return payload[key]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", required=True, help="Absolute project directory")
    parser.add_argument("--task", required=True, help="Task to delegate")
    parser.add_argument("--timeout", default="45m", help="Timeout, e.g. 90s, 45m, 2h")
    parser.add_argument("--model", help="Optional Antigravity model")
    parser.add_argument("--conversation", help="Optional conversation id to resume")
    parser.add_argument("--always-approve", action="store_true", help="Auto-approve tool permissions (--dangerously-skip-permissions)")
    parser.add_argument("--output-dir", help="Directory for captured output")
    parser.add_argument("--user-home", help="Disposable user home exposed to Antigravity")
    args = parser.parse_args()

    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        print(f"error: project directory does not exist: {cwd}", file=sys.stderr)
        return 2

    agy = find_agy()
    if not agy:
        print("error: agy executable not found; set AGY_BIN or add agy to PATH", file=sys.stderr)
        return 127
    if not Path(agy).is_file():
        resolved = shutil.which(agy)
        if not resolved:
            print("error: agy executable not found; set AGY_BIN or add agy to PATH", file=sys.stderr)
            return 127
        agy = resolved

    try:
        seconds = parse_duration(args.timeout)
    except (TypeError, ValueError) as exc:
        parser.error(f"invalid --timeout: {exc}")
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="antigravity-delegate-"))
    output_dir.mkdir(parents=True, exist_ok=True)
    user_home = Path(args.user_home).expanduser().resolve() if args.user_home else None
    if user_home:
        user_home.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / "stdout.json"
    stderr_path = output_dir / "stderr.log"
    manifest_path = output_dir / "result.json"

    # Match agy's own print-timeout to the run timeout so it does not abort at its 5m default.
    command = [agy, "--output-format", "json", "--add-dir", str(cwd), "--print-timeout", f"{int(seconds)}s"]
    if args.model:
        command.extend(["--model", args.model])
    if args.conversation:
        command.extend(["--conversation", args.conversation])
    if args.always_approve:
        command.append("--dangerously-skip-permissions")
    command.extend(["-p", args.task])

    try:
        child_env = os.environ.copy()
        if user_home:
            child_env.update({"HOME": str(user_home), "USERPROFILE": str(user_home)})
        completed = run_bounded(command, cwd, seconds + 30, child_env)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        stdout_path.write_text(stdout if isinstance(stdout, str) else stdout.decode("utf-8", "replace"), encoding="utf-8")
        stderr_path.write_text(stderr if isinstance(stderr, str) else stderr.decode("utf-8", "replace"), encoding="utf-8")
        manifest = {"tool": "agy", "cwd": str(cwd), "exit_code": 124, "timed_out": True, "output_dir": str(output_dir), "stdout": str(stdout_path), "stderr": str(stderr_path)}
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print(f"error: Antigravity timed out after {args.timeout}; output: {output_dir}", file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"error: could not start Antigravity: {exc}", file=sys.stderr)
        return 126

    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    manifest = {"tool": "agy", "cwd": str(cwd), "user_home": str(user_home) if user_home else None, "environment_overrides": ["HOME", "USERPROFILE"] if user_home else [], "exit_code": completed.returncode, "output_dir": str(output_dir), "stdout": str(stdout_path), "stderr": str(stderr_path)}
    try:
        payload = json.loads(completed.stdout)
        manifest["response"] = extract_response(payload)
        manifest["raw"] = payload
    except json.JSONDecodeError:
        # agy may emit plain text; treat it as the response rather than a hard failure.
        manifest["response"] = completed.stdout.strip()
        manifest["parse_warning"] = "Antigravity output was not a single JSON object; response is raw text"

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

    status = manifest.get("raw", {}).get("status") if isinstance(manifest.get("raw"), dict) else None
    if completed.returncode == 0 and status not in (None, "SUCCESS"):
        print(f"error: Antigravity returned status {status}; raw output: {stdout_path}", file=sys.stderr)
        return 65
    if completed.returncode == 0 and not manifest.get("response"):
        print(f"error: Antigravity produced no response; raw output: {stdout_path}", file=sys.stderr)
        return 65
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
