# Antigravity headless reference

This skill follows Google's Antigravity CLI (`agy`, verified against agy 1.1.x on 2026-08-11):

- Headless invocation: `agy -p "..."` (also `--print` / `--prompt`)
- Working directory: no dedicated flag; set the subprocess working directory and grant access with `--add-dir <DIR>` (repeatable)
- Machine-readable output: `--output-format json` (or `stream-json`, default `text`)
- Print-mode timeout: `--print-timeout <DURATION>` (default 5m0s) — must be raised for long tasks or the CLI aborts early
- Model selection: `--model <MODEL>`; list with `agy models`
- Reasoning effort: `--effort low|medium|high`
- Execution mode: `--mode accept-edits|plan`
- Automated execution: `--dangerously-skip-permissions` (auto-approve all tool permissions)
- Structured output: `--json-schema <SCHEMA-OR-PATH>`
- Resumable sessions: `--conversation <ID>` or `-c` / `--continue`
- Sandbox: `--sandbox` (terminal restrictions)
- API key: `--api-key <KEY>` exists in the CLI, but the wrapper deliberately does not use it because secrets must not be copied into process arguments.

Authentication is expected to be preconfigured through Antigravity's environment or login. The wrapper never reads credentials or copies them into process arguments. If authentication fails, return Antigravity's error and ask the user to authenticate separately.

Notes:

- The wrapper matches `--print-timeout` to the run timeout so a long delegation is not cut off at the 5-minute default.
- With `--output-format json`, the wrapper parses a single JSON object and surfaces a likely result field as `response`; when the output is plain text it keeps the raw text as `response` with a `parse_warning` instead of failing.
- Antigravity is Gemini-backed; use it when you want a Google-model second opinion or Gemini-specific code generation.

Primary sources:

- Local help: `agy help`, `agy --help`
- `agy models` for available models, `agy changelog` for release notes
