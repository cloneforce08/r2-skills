#!/usr/bin/env bash
set -euo pipefail

# Claude Code adapter implementation for the generic SCP_* contract.

cleanup_paths=()

cleanup() {
  local path
  for path in "${cleanup_paths[@]:-}"; do
    if [[ -n "$path" && -e "$path" ]]; then
      rm -f -- "$path"
    fi
  done
}

trap cleanup EXIT INT TERM

fail() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

executor_model="${SCP_CLAUDE_EXECUTOR_MODEL:-sonnet}"

output_format="${SCP_OUTPUT_FORMAT:-}"
case "$output_format" in
  text|stream-json)
    ;;
  *)
    fail "SCP_OUTPUT_FORMAT must be 'text' or 'stream-json'."
    ;;
esac

project_root="${SCP_PROJECT_ROOT:-$PWD}"
if [[ ! -d "$project_root" ]]; then
  fail "SCP_PROJECT_ROOT does not exist or is not a directory: $project_root"
fi

prompt_file=""
if [[ -n "${SCP_PROMPT_FILE:-}" ]]; then
  prompt_file="$SCP_PROMPT_FILE"
  if [[ ! -f "$prompt_file" ]]; then
    fail "SCP_PROMPT_FILE does not exist: $prompt_file"
  fi
elif [[ -n "${SCP_PROMPT:-}" ]]; then
  prompt_file="$(mktemp)"
  cleanup_paths+=("$prompt_file")
  printf '%s' "$SCP_PROMPT" > "$prompt_file"
else
  fail "Provide either SCP_PROMPT or SCP_PROMPT_FILE."
fi

if [[ -n "${SCP_SKILL_FILE:-}" ]]; then
  if [[ ! -f "$SCP_SKILL_FILE" ]]; then
    fail "SCP_SKILL_FILE does not exist: $SCP_SKILL_FILE"
  fi
  commands_dir="$project_root/.claude/commands"
  mkdir -p "$commands_dir"
  target_skill="$commands_dir/$(basename "$SCP_SKILL_FILE")"
  cp "$SCP_SKILL_FILE" "$target_skill"
  cleanup_paths+=("$target_skill")
fi

claude_bin="${SCP_CLAUDE_BIN:-claude}"
claude_cmd=("$claude_bin" -p --output-format "$output_format" --model "$executor_model")
if [[ "$output_format" == "stream-json" ]]; then
  claude_cmd+=(--verbose)
  if [[ "${SCP_INCLUDE_PARTIAL_MESSAGES:-0}" == "1" ]]; then
    claude_cmd+=(--include-partial-messages)
  fi
fi

unset CLAUDECODE

cd "$project_root"
"${claude_cmd[@]}" < "$prompt_file"
