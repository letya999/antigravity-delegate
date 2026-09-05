<p align="center">
  <strong>English</strong> · <a href="README.ru.md">Русский</a>
</p>

<p align="center">
  <h1 align="center">Antigravity Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/antigravity-delegate"><img src="https://img.shields.io/badge/status-active-brightgreen" alt="status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-discoverable-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-agy-purple" alt="CLI: agy">
</p>

Headless Google Antigravity (`agy`) delegate skill by [Artem Letyushev](https://github.com/letya999).

The command is `scripts/delegate_antigravity.py`. The primary consumer is the controlling agent or orchestrator: every execution runs Antigravity once as a bounded, non-interactive subprocess (`agy -p`) and returns one structured JSON envelope.

---

## One objective, bounded subprocess, zero trust

The wrapper acts as a deterministic isolation layer between your controlling agent and the Antigravity CLI. It guarantees safe execution boundaries:

- **Single non-interactive execution:** Invokes `agy -p` directly via `subprocess.run(..., shell=False)` without terminal takeovers.
- **Strict workspace scoping:** Automatically passes `--add-dir <cwd>` to grant explicit workspace access without ambient filesystem exposure.
- **Zero-trust verification:** Outputs are treated as unverified evidence. The controlling agent verifies diffs and tests independently before accepting changes.
- **Credential isolation:** Never reads, prints, or exposes `GEMINI_API_KEY`, OAuth credentials, private keys, or `.env` files.

## Capability matrix

| Capability / Setting | Specification | Behavior & Guarantees |
|---|---|---|
| **Headless command** | `agy -p "<task>"` | Non-interactive execution in print mode with JSON output formatting |
| **Workspace scoping** | `--add-dir <cwd>` | Grants Antigravity access to the target project directory |
| **Output format** | `--output-format json` | Structured execution result parsed into a clean `response` field |
| **Timeout alignment** | `--print-timeout <sec>` | Propagates wrapper timeout to Antigravity internal print watchdog |
| **Safety default** | Standard permissions | Prompts stay bounded; `--dangerously-skip-permissions` requires explicit `--always-approve` |
| **Executable override** | `AGY_BIN` env var | Direct path override before PATH resolution |
| **Resumable sessions** | `--conversation <id>` | Optional conversation continuation when explicitly requested |
| **Standard exit codes** | `0, 2, 65, 124, 126, 127` | Predictable error routing for orchestrators |

## Install

With `npx skills`:

```bash
npx skills add letya999/antigravity-delegate
```

Or clone into an agent skill directory:

```bash
git clone https://github.com/letya999/antigravity-delegate.git .agents/skills/antigravity-delegate
```

## Quick Start

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_antigravity.py \
  --cwd "$PWD" \
  --task "Audit this repository for security risks and report top 3 findings." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_antigravity.py `
  --cwd (Get-Location).Path `
  --task "Audit this repository for security risks and report top 3 findings." `
  --timeout 45m
```

---

<details>
<summary>JSON Manifest Schema & Agent Integration</summary>

The wrapper writes `stdout.json`, `stderr.log`, and `result.json` into an isolated temporary directory and prints the manifest to stdout:

```json
{
  "tool": "agy",
  "cwd": "C:\\work\\repo",
  "user_home": null,
  "environment_overrides": [],
  "exit_code": 0,
  "output_dir": "C:\\Temp\\antigravity-delegate-xyz",
  "stdout": "C:\\Temp\\antigravity-delegate-xyz\\stdout.json",
  "stderr": "C:\\Temp\\antigravity-delegate-xyz\\stderr.log",
  "response": "Clean extracted response text or structured data",
  "raw": {
    "status": "SUCCESS",
    "response": "..."
  }
}
```

If Antigravity returns status other than `SUCCESS` or produces an empty response despite exit code 0, the wrapper returns exit code `65`.

</details>

<details>
<summary>CLI Flags & Configuration Reference</summary>

| Flag | Type | Description |
|---|---|---|
| `--cwd` | Path (required) | Target project directory for execution. Exits with `2` if missing. |
| `--task` | String (required) | Delegated prompt / instruction for Antigravity. |
| `--timeout` | Duration (default: `45m`) | Timeout supporting `90s`, `45m`, `2h`, or integer seconds. |
| `--always-approve` | Flag | Passes `--dangerously-skip-permissions` for autonomous file modifications. |
| `--conversation` | String | Conversation ID to resume an existing session. |
| `--user-home` | Path | Disposable user home directory passed via `HOME` and `USERPROFILE`. |
| `--output-dir` | Path | Custom directory for captured artifacts and logs. |

</details>

<details>
<summary>Safety Posture & Credential Guardrails</summary>

- **No credential access:** The wrapper never inspects, logs, or exports `GEMINI_API_KEY`, `~/.antigravity` configs, or browser cookies.
- **No auto-approve by default:** Safe by default. Permission bypass is only activated when `--always-approve` is explicitly specified by the controlling agent.
- **No recursive loops:** Delegated agents must never re-invoke delegator wrappers.

</details>

<details>
<summary>Independent Verification Protocol</summary>

Delegated agent outputs are untrusted by default. When the task involves filesystem modifications:

1. Check changes independently: `git diff --stat` and `git diff`.
2. Run test suites outside the delegated environment: `pytest`, `npm test`, etc.
3. Review added dependencies before accepting the commit.

</details>

<details>
<summary>Test Suite & Quality Checks</summary>

Standard library `unittest` coverage without external mock dependencies:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Agent Skill Entry Points</summary>

- [SKILL.md](SKILL.md) — Skill instruction specification for coding agents.
- [QUICKSTART.md](QUICKSTART.md) — Quick command reference.
- [references/runtime-setup.md](references/runtime-setup.md) — Cross-platform pre-flight checks.
- [references/headless-reference.md](references/headless-reference.md) — Headless CLI flag documentation.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Discovery index for skills.sh.
- [dist/antigravity-delegate.zip](dist/antigravity-delegate.zip) — Discoverable archive artifact.

</details>

<details>
<summary>License</summary>

MIT License. See [LICENSE](LICENSE) for full text. Copyright (c) 2026 Artem Letyushev.

</details>
