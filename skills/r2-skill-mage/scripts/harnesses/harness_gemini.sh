#!/usr/bin/env bash
set -euo pipefail

# Google Gemini CLI adapter implementation for the generic SCP_* contract.

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

resolve_gemini_bin() {
  if [[ -n "${SCP_GEMINI_BIN:-}" ]]; then
    [[ -x "$SCP_GEMINI_BIN" ]] || fail "SCP_GEMINI_BIN is not executable: $SCP_GEMINI_BIN"
    printf '%s\n' "$SCP_GEMINI_BIN"
    return
  fi

  if command -v gemini >/dev/null 2>&1; then
    command -v gemini
    return
  fi

  if [[ -x "/home/linuxbrew/.linuxbrew/bin/gemini" ]]; then
    printf '%s\n' "/home/linuxbrew/.linuxbrew/bin/gemini"
    return
  fi

  fail "Could not find an executable Gemini CLI. Install 'gemini', add it to PATH, or set SCP_GEMINI_BIN."
}

resolved_skill_file=""

prepare_skill_file() {
  if [[ -z "${SCP_SKILL_FILE:-}" ]]; then
    return
  fi

  [[ -f "$SCP_SKILL_FILE" ]] || fail "SCP_SKILL_FILE does not exist: $SCP_SKILL_FILE"
  [[ -n "${SCP_SKILL_DESCRIPTION:-}" ]] || fail "SCP_SKILL_DESCRIPTION is required when SCP_SKILL_FILE is set."
  [[ -n "${SCP_SKILL_ALIAS:-}" ]] || fail "SCP_SKILL_ALIAS is required when SCP_SKILL_FILE is set."

  local basename=""
  local extension=""
  local stem=""
  local skill_target=""

  basename="$(basename "$SCP_SKILL_FILE")"
  extension="${basename##*.}"
  stem="${basename%.*}"

  if [[ "$SCP_SKILL_FILE" == "$project_root"/* ]]; then
    resolved_skill_file="$SCP_SKILL_FILE"
    return
  fi

  if [[ "$extension" == "$basename" ]]; then
    skill_target="$(mktemp "$project_root/${basename}.XXXXXX")"
  else
    skill_target="$(mktemp "$project_root/${stem}.XXXXXX.$extension")"
  fi

  cp -- "$SCP_SKILL_FILE" "$skill_target"
  cleanup_paths+=("$skill_target")
  resolved_skill_file="$skill_target"
}

build_prompt() {
  if [[ -z "$resolved_skill_file" ]]; then
    printf '%s' "$prompt"
    return
  fi

  SCP_GEMINI_USER_PROMPT="$prompt" RESOLVED_SKILL_FILE="$resolved_skill_file" python3 - <<'PY'
import os

user_prompt = os.environ["SCP_GEMINI_USER_PROMPT"]
skill_alias = os.environ["SCP_SKILL_ALIAS"]
skill_name = os.environ.get("SCP_SKILL_NAME", "")
skill_desc = os.environ["SCP_SKILL_DESCRIPTION"]
skill_file = os.environ["RESOLVED_SKILL_FILE"]

lines = [
    "You are handling a request with one temporary skill available.",
    "Decide whether to inspect the skill file based only on the temporary skill description below.",
    "If the request overlaps with the description, workflow name, codename, onboarding flow, checklist, ritual, or verification language from this skill, you must read the skill file before answering.",
    "Use the read_file tool on the exact skill file path shown below when the request matches.",
    "If you read the temporary skill file, do not search the workspace, list files, or use any other tools unless the user explicitly asks for extra work.",
    "After reading the temporary skill file, answer directly from that file and the user's request.",
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
        "",
        "User request:",
        user_prompt,
    ]
)
print("\n".join(lines))
PY
}

executor_model="${SCP_GEMINI_EXECUTOR_MODEL:-gemini-3.1-pro}"

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

prepare_skill_file
prompt="$(build_prompt)"

gemini_bin="$(resolve_gemini_bin)"
gemini_cmd=(
  "$gemini_bin"
  -p "$prompt"
  --output-format stream-json
  --model "$executor_model"
  --yolo
)

export CI=1
export NO_COLOR=1
export PAGER=cat
export TERM=dumb

cd "$project_root"

normalizer_script="$(mktemp)"
cleanup_paths+=("$normalizer_script")
cat > "$normalizer_script" <<'PY'
import json
import os
import sys

mode = os.environ.get("SCP_OUTPUT_FORMAT", "text")

text_chunks: list[str] = []


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()


for raw_line in sys.stdin:
    line = raw_line.strip()
    if not line:
        continue

    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue

    event_type = event.get("type", "")

    if mode == "text":
        if event_type == "tool_use":
            text_chunks.clear()
        elif event_type == "message" and event.get("role") == "assistant":
            content = event.get("content", "")
            if content:
                text_chunks.append(content)
        elif event_type == "result" and event.get("status") != "success":
            raise SystemExit(1)
        continue

    if event_type == "tool_use":
        tool_name = event.get("tool_name", "")
        parameters = event.get("parameters") or {}
        if tool_name == "read_file":
            file_path = parameters.get("file_path", "")
            if file_path:
                emit(
                    {
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "name": "Read",
                                    "input": {
                                        "file_path": file_path,
                                    },
                                }
                            ]
                        },
                    }
                )
        continue

    if event_type == "message" and event.get("role") == "assistant":
        content = event.get("content", "")
        if content:
            emit(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "text",
                                "text": content,
                            }
                        ]
                    },
                }
            )
        continue

    if event_type == "result":
        status = event.get("status", "success")
        emit(
            {
                "type": "result",
                "subtype": "success" if status == "success" else "error",
                "is_error": status != "success",
            }
        )

if mode == "text":
    sys.stdout.write("".join(text_chunks))
    sys.stdout.flush()
PY

"${gemini_cmd[@]}" | python3 "$normalizer_script"