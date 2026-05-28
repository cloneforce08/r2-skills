#!/usr/bin/env bash
set -euo pipefail

# Harness adapter contract
#
# Required inputs:
# - Harness-specific executor model variable (for example `SCP_CLAUDE_EXECUTOR_MODEL`)
# - SCP_OUTPUT_FORMAT: one of `text` or `stream-json`
# - Either SCP_PROMPT or SCP_PROMPT_FILE
#
# Optional inputs:
# - SCP_INCLUDE_PARTIAL_MESSAGES: `1` to request partial messages for stream mode
# - SCP_PROJECT_ROOT: working directory used for harness execution
# - SCP_SKILL_FILE: temporary skill artifact to register for this invocation
# - SCP_SKILL_ALIAS, SCP_SKILL_NAME, SCP_SKILL_DESCRIPTION: metadata for custom adapters

fail() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

if [[ -z "${SCP_HARNESS:-}" ]]; then
  fail "SCP_HARNESS is required and must be non-empty."
fi

if [[ ! "${SCP_HARNESS}" =~ ^[a-z0-9][a-z0-9_-]*$ ]]; then
  fail "SCP_HARNESS has an invalid value '${SCP_HARNESS}'. Use lowercase letters, digits, hyphens, or underscores."
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
harness_script="${script_dir}/harnesses/harness_${SCP_HARNESS}.sh"

if [[ ! -f "$harness_script" ]]; then
  fail "Unsupported harness '${SCP_HARNESS}'. Expected script: $harness_script"
fi

if [[ ! -x "$harness_script" ]]; then
  fail "Harness script is not executable: $harness_script"
fi

exec "$harness_script" "$@"
