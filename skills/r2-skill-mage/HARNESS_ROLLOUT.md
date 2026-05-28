# Harness Rollout

Canonical rollout tracker for multi-harness adapter support.

## Shared Rules

- `SCP_HARNESS` is mandatory.
- Harnesses are discovered by file convention: `scripts/harnesses/harness_<name>.sh`.
- Every harness must normalize to the existing `text` and `stream-json` contracts.
- A harness is only complete when `creation`, `eval`, and `improve-description` smoke tests pass.

## Phase Checklist

| Phase | Description |
| --- | --- |
| 1 | CLI discovery completed and help output reviewed |
| 2 | Harness script created in `scripts/harnesses/` |
| 3 | Adapter contract implemented (`SCP_*` inputs mapped) |
| 4 | `text` output normalized |
| 5 | `stream-json` output normalized |
| 6 | Smoke tests passing |
| 7 | Harness marked complete |

## Harness Status

### claude

| Item | Status | Notes |
| --- | --- | --- |
| Discovery | Complete | Existing baseline implementation already proven with real smoke tests |
| Adapter script | Complete | `scripts/harnesses/harness_claude.sh` |
| Dispatcher wiring | Complete | Requires `SCP_HARNESS=claude` |
| Smoke tests | Complete | `creation`, `eval`, and `improve-description` passed under the dispatcher architecture |
| Completion | Complete | Baseline harness for the multi-harness design |

### copilot

| Item | Status | Notes |
| --- | --- | --- |
| Discovery | Complete | Verified local Homebrew install plus current CLI docs for `-p`, `--model`, and `--output-format json` |
| Adapter script | Complete | `scripts/harnesses/harness_copilot.sh` |
| Dispatcher wiring | Complete | Requires `SCP_HARNESS=copilot` |
| Smoke tests | Complete | `creation`, `eval`, and `improve-description` passed with `SCP_COPILOT_EXECUTOR_MODEL=gpt-5.4-mini` |
| Completion | Complete | Copilot harness now meets the current multi-harness gate |

### gemini

| Item | Status | Notes |
| --- | --- | --- |
| Discovery | Complete | Verified Homebrew install fallback plus current CLI support for `-p`, `--model`, `--output-format stream-json`, and `--yolo` |
| Adapter script | Complete | `scripts/harnesses/harness_gemini.sh` |
| Dispatcher wiring | Complete | Requires `SCP_HARNESS=gemini` |
| Smoke tests | Complete | `creation`, `eval`, and `improve-description` passed with `SCP_GEMINI_EXECUTOR_MODEL=gemini-3.1-pro` |
| Completion | Complete | Gemini harness now meets the current multi-harness gate |

## Contract Refactor: Task-Scoped Harness Override And Model Split

### Decisions

- A harness named by the user in chat applies only to the current task.
- Commands run for that task must export `SCP_HARNESS=<named-harness>` explicitly.
- No new CLI flags are added in this round.
- The repo no longer depends operationally on `SCP_MODEL`, `SCP_EXECUTOR_MODEL`, or `SCP_ANALYZER_MODEL` globals.
- `scripts/improve_description.py` uses the harness-specific analyzer model.
- `scripts/open-html.sh` is postponed and out of scope for this round.

### Commit Order

1. Shared contract resolver in `scripts/harness.py`.
2. Harness adapters read only their own executor vars.
3. Python entry points stop requiring global model vars.
4. Analyzer model applied to analysis flows and benchmark metadata.
5. Skill instructions updated for task-scoped harness override.
6. Rollout/docs updated for the new contract.
7. Full regression gate across `claude`, `copilot`, and `gemini`.

### Verification Gate

- `SCP_HARNESS=claude SCP_CLAUDE_EXECUTOR_MODEL=<model> python3 -m scripts.run_harness_smoke_tests --json`
- `SCP_HARNESS=copilot SCP_COPILOT_EXECUTOR_MODEL=<model> python3 -m scripts.run_harness_smoke_tests --json`
- `SCP_HARNESS=gemini SCP_GEMINI_EXECUTOR_MODEL=<model> python3 -m scripts.run_harness_smoke_tests --json`
- Run one short benchmark/report generation pass and confirm `executor_model` and `analyzer_model` are real values, not placeholders.

### future harness template

1. Run `<name> --help` and record relevant capabilities.
2. Add `scripts/harnesses/harness_<name>.sh`.
3. Map the shared `SCP_*` contract to the harness CLI, including a harness-specific executor model variable and analyzer fallback in `scripts/harness.py`.
4. Normalize `text` and `stream-json` output locally if needed.
5. Run `SCP_HARNESS=<name> <HARNESS_EXECUTOR_ENV>=<model> python3 -m scripts.run_harness_smoke_tests --json`.
6. Update this file with status and blockers.
