---
name: antigravity-delegate
description: Run Antigravity CLI (`agy`) as a headless delegate. Use when the user names Antigravity or agy, says "ask Antigravity", wants a Gemini-backed second opinion, or compares coding agents. Do NOT use for interactive sessions, other CLIs, or tasks not meant for delegation.
---

# Antigravity Delegate

Run Antigravity as a bounded headless subprocess (`agy -p`) and hand its final response back to the user. Keep the current project as the working directory unless the user specifies another directory.

## Anti-Rationalization

Trigger this skill when the user explicitly asks for Antigravity, `agy`, a Gemini-backed second opinion, or a comparison that needs Antigravity evidence. Do not skip it just because another CLI can run the same task; the requested value is the Google/Antigravity perspective.

Pause instead when Antigravity is missing or unauthenticated, the user wants an interactive session, the task requires exposing secrets, or the requested permission mode exceeds the user's authorization.

## Runtime Pre-Flight

Read [runtime-setup.md](references/runtime-setup.md) before invoking the wrapper. Verify Python 3.10+ and `agy` or `AGY_BIN`; stop and report the missing prerequisite instead of inventing an installer or assuming a specific shell.

## Workflow

1. Clarify the delegated objective, scope, and whether Antigravity may edit files or run commands. Do not delegate secrets or expose protected files in the prompt.
2. Resolve the project directory to an absolute path. Prefer the current working directory. Verify it exists before starting.
   For disposable-harness experiments, pass its parent home with `--user-home`; the wrapper records and exposes it through `HOME` and `USERPROFILE` without changing `LOCALAPPDATA`.
3. Run the bundled wrapper with the Python command discovered by [runtime-setup.md](references/runtime-setup.md).
4. Read [headless-reference.md](references/headless-reference.md) when flags, sessions, timeouts, output parsing, or authentication details are needed.

5. Report the wrapper's result, output-file path, exit status, and any stderr warning. A successful process is not proof that the requested change is correct: inspect the diff and run relevant tests independently when the delegated task changed files.
6. If the task is long-running, use a generous explicit timeout. The wrapper passes the same value to Antigravity's own `--print-timeout`, so the CLI does not abort at its 5-minute default. Never create a hidden daemon, polling loop, or unbounded background process.

## Wrapper behavior

- `delegate_antigravity.py` invokes `agy` directly, never through a shell, and supports `AGY_BIN` for an explicit executable path.
- Antigravity has no working-directory flag, so the wrapper sets the subprocess working directory and also passes `--add-dir <cwd>` to grant workspace access.
- It uses print mode with `-p`, `--output-format json`, and `--print-timeout` matched to the run timeout; it adds `--dangerously-skip-permissions` only when `--always-approve` is requested, otherwise it runs with the default permission mode.
- Authentication is handled entirely by Antigravity's preconfigured environment or login. The wrapper never reads credentials or places them in command-line arguments.
- It writes stdout, stderr, and a small result manifest to a temporary output directory, then prints the manifest as JSON. It surfaces Antigravity's parsed result under `response`, degrading to the raw text when the output is not a single JSON object.
- It returns nonzero for missing Antigravity, an invalid project directory, timeout, or a failed process. Do not hide these failures.
- It also returns nonzero for a non-`SUCCESS` JSON status or an empty response, even if the process exit code is zero.
- Prefer a one-shot invocation. Use `--conversation` or `--continue` only when the user explicitly asks for a resumable Antigravity session.

## Safety and verification

- Do not read or print `GEMINI_API_KEY`, OAuth tokens, `~/.antigravity` or agy credentials, `.env*`, private keys, or browser profiles.
- Do not add plugins, disable repository protections, publish code, push commits, or delete data unless the user explicitly asks for that exact action.
- Default to the standard permission mode. Only escalate to `--always-approve` when the user authorizes autonomous edits and the directory is trusted.
- Treat Antigravity's report as unverified. Inspect changed files, `git diff`, and tests from the controlling agent.
- If `agy` is not found, tell the user to verify the official installation and PATH; do not install packages or run an installer automatically.

## Resources

Use `references/runtime-setup.md` for Python and CLI pre-flight, `scripts/delegate_antigravity.py` for deterministic invocation, and `references/headless-reference.md` for the documented Antigravity interface.
