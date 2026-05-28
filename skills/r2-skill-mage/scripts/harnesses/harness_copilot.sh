#!/usr/bin/env bash
set -euo pipefail

# GitHub Copilot CLI adapter implementation for the generic SCP_* contract.

cleanup_paths=()
instructions_target=""
instructions_backup=""
instructions_parent_created=""
instructions_created=0

cleanup() {
  local path

  if [[ -n "$instructions_target" ]]; then
    if [[ -n "$instructions_backup" && -f "$instructions_backup" ]]; then
      mv -- "$instructions_backup" "$instructions_target"
      instructions_backup=""
    elif [[ "$instructions_created" == "1" && -f "$instructions_target" ]]; then
      rm -f -- "$instructions_target"
    fi
  fi

  if [[ -n "$instructions_parent_created" && -d "$instructions_parent_created" ]]; then
    rmdir --ignore-fail-on-non-empty "$instructions_parent_created" 2>/dev/null || true
  fi

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

resolve_copilot_bin() {
  if [[ -n "${SCP_COPILOT_BIN:-}" ]]; then
    [[ -x "$SCP_COPILOT_BIN" ]] || fail "SCP_COPILOT_BIN is not executable: $SCP_COPILOT_BIN"
    printf '%s\n' "$SCP_COPILOT_BIN"
    return
  fi

  if command -v copilot >/dev/null 2>&1; then
    command -v copilot
    return
  fi

  if [[ -x "/home/linuxbrew/.linuxbrew/bin/copilot" ]]; then
    printf '%s\n' "/home/linuxbrew/.linuxbrew/bin/copilot"
    return
  fi

  fail "Could not find an executable Copilot CLI. Install 'copilot', add it to PATH, or set SCP_COPILOT_BIN."
}

append_temporary_skill_instructions() {
  if [[ -z "${SCP_SKILL_FILE:-}" ]]; then
    return
  fi

  [[ -f "$SCP_SKILL_FILE" ]] || fail "SCP_SKILL_FILE does not exist: $SCP_SKILL_FILE"
  [[ -n "${SCP_SKILL_DESCRIPTION:-}" ]] || fail "SCP_SKILL_DESCRIPTION is required when SCP_SKILL_FILE is set."
  [[ -n "${SCP_SKILL_ALIAS:-}" ]] || fail "SCP_SKILL_ALIAS is required when SCP_SKILL_FILE is set."

  local instructions_path=""
  local instructions_parent=""
  local temp_section=""

  if [[ -f "$project_root/COPILOT.md" ]]; then
    instructions_path="$project_root/COPILOT.md"
  elif [[ -f "$project_root/.github/copilot-instructions.md" ]]; then
    instructions_path="$project_root/.github/copilot-instructions.md"
  else
    instructions_path="$project_root/COPILOT.md"
    instructions_created=1
  fi

  instructions_parent="$(dirname "$instructions_path")"
  if [[ ! -d "$instructions_parent" ]]; then
    mkdir -p "$instructions_parent"
    instructions_parent_created="$instructions_parent"
  fi

  temp_section="$(mktemp)"
  cleanup_paths+=("$temp_section")
  python3 - <<'PY' > "$temp_section"
import os
from pathlib import Path

skill_alias = os.environ["SCP_SKILL_ALIAS"]
skill_name = os.environ.get("SCP_SKILL_NAME", "")
skill_desc = os.environ["SCP_SKILL_DESCRIPTION"]
skill_file = Path(os.environ["SCP_SKILL_FILE"]).resolve()

lines = [
    "",
    "<!-- r2-skill-mage temporary instructions: do not commit -->",
    "## Temporary Skill Catalog",
    "",
    "A temporary skill is available for this session.",
    f"- Alias: {skill_alias}",
]
if skill_name:
    lines.append(f"- Name: {skill_name}")
lines.extend(
    [
        f"- Description: {skill_desc}",
        f"- Skill file: {skill_file}",
        "",
    "At the start of each task, compare the user's request against the Temporary Skill Catalog in this file.",
    "If the request overlaps with a skill description, workflow name, codename, checklist, onboarding flow, or other distinctive terms from an entry, inspect that skill file before answering.",
    "Treat explicit phrase matches and close semantic matches as strong evidence that you should read the skill file.",
        f"Use the bash tool to run: cat '{skill_file}'",
    "Do not skip the skill file when the request plausibly matches the description above.",
    "Do not read the skill file when the request is clearly unrelated to the description.",
        "After reading the skill file, follow its instructions when producing the answer.",
    ]
)
print("\n".join(lines))
PY

  if [[ -f "$instructions_path" ]]; then
    instructions_backup="$(mktemp)"
    cp -- "$instructions_path" "$instructions_backup"
    python3 - "$instructions_path" "$temp_section" <<'PY' > "$instructions_path.tmp"
from pathlib import Path
import sys

original = Path(sys.argv[1]).read_text(encoding="utf-8")
addition = Path(sys.argv[2]).read_text(encoding="utf-8")

if original and not original.endswith("\n"):
    original += "\n"

sys.stdout.write(original)
sys.stdout.write(addition)
if addition and not addition.endswith("\n"):
    sys.stdout.write("\n")
PY
    mv -- "$instructions_path.tmp" "$instructions_path"
  else
    cp -- "$temp_section" "$instructions_path"
  fi

  instructions_target="$instructions_path"
}

executor_model="${SCP_COPILOT_EXECUTOR_MODEL:-gpt-5.4}"

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

prompt=""
if [[ -n "${SCP_PROMPT_FILE:-}" ]]; then
  [[ -f "$SCP_PROMPT_FILE" ]] || fail "SCP_PROMPT_FILE does not exist: $SCP_PROMPT_FILE"
  prompt="$(cat "$SCP_PROMPT_FILE")"
elif [[ -n "${SCP_PROMPT:-}" ]]; then
  prompt="$SCP_PROMPT"
else
  fail "Provide either SCP_PROMPT or SCP_PROMPT_FILE."
fi

if [[ -n "${SCP_SKILL_FILE:-}" ]]; then
  prompt="$({
    SCP_COPILOT_USER_PROMPT="$prompt" python3 - <<'PY'
import os

user_prompt = os.environ["SCP_COPILOT_USER_PROMPT"]
skill_alias = os.environ["SCP_SKILL_ALIAS"]
skill_name = os.environ.get("SCP_SKILL_NAME", "")
skill_desc = os.environ["SCP_SKILL_DESCRIPTION"]
skill_file = os.environ["SCP_SKILL_FILE"]

lines = [
    "You are handling a request with one temporary skill available.",
    "Decide whether to inspect the skill file based only on the temporary skill description below.",
    "If the request overlaps with the description, workflow name, codename, onboarding flow, checklist, ritual, or verification language from this skill, you must read the skill file before answering.",
    "Use the bash tool to run the exact command shown below when the request matches.",
    "If the request is clearly unrelated, do not read the skill file.",
    "",
    "Temporary skill:",
    f"- Alias: {skill_alias}",
]
if skill_name:
    lines.append(f"- Name: {skill_name}")
lines.extend(
    [
        f"- Description: {skill_desc}",
        f"- Skill file: {skill_file}",
        f"- Read command: cat '{skill_file}'",
        "",
        "User request:",
        user_prompt,
    ]
)
print("\n".join(lines))
PY
  } )"
fi

append_temporary_skill_instructions

copilot_bin="$(resolve_copilot_bin)"
copilot_cmd=(
  "$copilot_bin"
  -p "$prompt"
  --silent
  --no-color
  --allow-all-tools
  --allow-all-paths
  --allow-all-urls
  --no-ask-user
  --add-dir "$project_root"
  --model "$executor_model"
)

if [[ -n "${SCP_SKILL_FILE:-}" ]]; then
  copilot_cmd+=(--add-dir "$(dirname "$SCP_SKILL_FILE")")
fi

export CI=1
export NO_COLOR=1
export PAGER=cat
export TERM=dumb

cd "$project_root"

if [[ "$output_format" == "text" ]]; then
  exec "${copilot_cmd[@]}"
fi

copilot_cmd+=(--output-format json)

normalizer_script="$(mktemp)"
cleanup_paths+=("$normalizer_script")
cat > "$normalizer_script" <<'PY'
import json
import os
import sys

skill_file = os.environ.get("SCP_SKILL_FILE", "")


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()


def normalize_tool_request(tool: dict) -> dict | None:
    name = tool.get("name", "")
    arguments = tool.get("arguments") or {}

    if name == "view":
        path = arguments.get("path", "")
        if skill_file and path == skill_file:
            return {
                "type": "tool_use",
                "name": "Read",
                "input": {
                    "file_path": path,
                },
            }
        return {"type": "tool_use", "name": "view", "input": arguments}

    if name == "bash":
        command = arguments.get("command", "")
        if skill_file and skill_file in command:
            return {
                "type": "tool_use",
                "name": "Read",
                "input": {
                    "file_path": skill_file,
                    "command": command,
                },
            }
        return {"type": "tool_use", "name": "bash", "input": arguments}

    return {"type": "tool_use", "name": name, "input": arguments}


for raw_line in sys.stdin:
    line = raw_line.strip()
    if not line:
        continue

    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue

    event_type = event.get("type", "")
    data = event.get("data") or {}

    if event_type == "assistant.message":
        content = []
        for tool in data.get("toolRequests") or []:
            normalized = normalize_tool_request(tool)
            if normalized is not None:
                content.append(normalized)
        text = data.get("content", "")
        if text:
            content.append({"type": "text", "text": text})
        emit({"type": "assistant", "message": {"content": content}})
    elif event_type == "result":
        exit_code = int(event.get("exitCode", 0) or 0)
        emit({"type": "result", "subtype": "success" if exit_code == 0 else "error", "is_error": exit_code != 0})
PY

"${copilot_cmd[@]}" | python3 "$normalizer_script"