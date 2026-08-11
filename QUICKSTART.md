# Antigravity Delegate Quickstart

Use this skill when the caller explicitly wants Antigravity (`agy`) to run as a separate headless agent.

## Requirements

- Python 3.10+
- Antigravity CLI (`agy`) on `PATH`, or `AGY_BIN` set to the executable path
- Antigravity authentication already configured by the user

## Run

POSIX shell on macOS, Linux, or WSL:

```sh
python3 scripts/delegate_antigravity.py \
  --cwd "$PWD" \
  --task "Review this repository and report the highest-risk issue." \
  --timeout 45m
```

Windows PowerShell:

```powershell
py -3 .\scripts\delegate_antigravity.py `
  --cwd (Get-Location).Path `
  --task "Review this repository and report the highest-risk issue." `
  --timeout 45m
```

If `python3` or `py -3` is not available, use the Python command discovered in `references/runtime-setup.md`.

## Result

The wrapper prints a JSON manifest with `response`, `exit_code`, `stdout`, `stderr`, and `output_dir`. Treat Antigravity's answer as unverified until the controlling agent checks the diff and tests.
