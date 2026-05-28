# Harness Adapters

Each file in this directory implements one concrete harness behind the shared `SCP_*` adapter contract.

## Naming Convention

- Harness scripts must be named `harness_<name>.sh`.
- The dispatcher in `scripts/run-harness.sh` resolves the script from `SCP_HARNESS=<name>`.
- `SCP_HARNESS` is mandatory. There is no implicit default harness.

## Required Contract

Every harness script must accept these environment variables:

- `SCP_HARNESS`
- `SCP_OUTPUT_FORMAT`
- Either `SCP_PROMPT` or `SCP_PROMPT_FILE`

The active harness may also receive its own executor-model variable. These are optional at the call site because `scripts.harness` resolves defaults, but each adapter must accept them when present:

- Claude: `SCP_CLAUDE_EXECUTOR_MODEL` with default `sonnet`
- Copilot: `SCP_COPILOT_EXECUTOR_MODEL` with default `gpt-5.4`
- Gemini: `SCP_GEMINI_EXECUTOR_MODEL` with default `gemini-3.1-pro`

Analyzer-model variables are resolved upstream by the Python callers and currently matter for metadata plus analyzer flows such as `scripts.improve_description.py`:

- Claude: `SCP_CLAUDE_ANALYZER_MODEL` (falls back to the Claude executor model)
- Copilot: `SCP_COPILOT_ANALYZER_MODEL` (falls back to the Copilot executor model)
- Gemini: `SCP_GEMINI_ANALYZER_MODEL` (falls back to the Gemini executor model)

It may also consume:

- `SCP_INCLUDE_PARTIAL_MESSAGES`
- `SCP_PROJECT_ROOT`
- `SCP_SKILL_FILE`
- `SCP_SKILL_ALIAS`
- `SCP_SKILL_NAME`
- `SCP_SKILL_DESCRIPTION`

## Output Requirements

- For `SCP_OUTPUT_FORMAT=text`, stdout must be plain text consumable by the current Python callers.
- For `SCP_OUTPUT_FORMAT=stream-json`, stdout must normalize to the stream contract expected by `scripts/run_eval.py`.
- If the native CLI cannot produce those formats directly, the harness script must normalize the output locally.

## Completion Gate

A harness implementation is only considered complete when all smoke tests pass:

```bash
SCP_HARNESS=claude SCP_CLAUDE_EXECUTOR_MODEL=<model> python3 -m scripts.run_harness_smoke_tests --json
SCP_HARNESS=copilot SCP_COPILOT_EXECUTOR_MODEL=<model> python3 -m scripts.run_harness_smoke_tests --json
SCP_HARNESS=gemini SCP_GEMINI_EXECUTOR_MODEL=<model> python3 -m scripts.run_harness_smoke_tests --json
```

## Current Implementations

- `harness_claude.sh`: baseline implementation for Claude Code.
- `harness_copilot.sh`: GitHub Copilot CLI adapter with Homebrew fallback at `/home/linuxbrew/.linuxbrew/bin/copilot`, temporary skill injection via `COPILOT.md`, and JSONL normalization for `run_eval.py`.
- `harness_gemini.sh`: Gemini CLI adapter with Homebrew fallback at `/home/linuxbrew/.linuxbrew/bin/gemini`, project-root-local temporary skill copies, prompt-based skill registration, and `stream-json` normalization for `scripts/run_eval.py`.
- Future adapters should be added independently as `harness_<name>.sh`.
