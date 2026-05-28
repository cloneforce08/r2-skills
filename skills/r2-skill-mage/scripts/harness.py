"""Harness adapter utilities for r2-skill-mage scripts."""

from __future__ import annotations

import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal, Mapping


HARNESS_SCRIPT = Path(__file__).with_name("run-harness.sh")
PROMPT_ENV_MAX_BYTES = 16 * 1024
HarnessModelRole = Literal["executor", "analyzer"]

EXECUTOR_MODEL_ENV_BY_HARNESS = {
    "claude": "SCP_CLAUDE_EXECUTOR_MODEL",
    "copilot": "SCP_COPILOT_EXECUTOR_MODEL",
    "gemini": "SCP_GEMINI_EXECUTOR_MODEL",
}

ANALYZER_MODEL_ENV_BY_HARNESS = {
    "claude": "SCP_CLAUDE_ANALYZER_MODEL",
    "copilot": "SCP_COPILOT_ANALYZER_MODEL",
    "gemini": "SCP_GEMINI_ANALYZER_MODEL",
}

DEFAULT_EXECUTOR_MODEL_BY_HARNESS = {
    "claude": "sonnet",
    "copilot": "gpt-5.4",
    "gemini": "gemini-3.1-pro",
}


class HarnessConfigError(RuntimeError):
    """Raised when the harness adapter configuration is invalid."""


def _read_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return env if env is not None else os.environ


def _validate_harness(harness: str) -> str:
    harness = harness.strip()
    if not harness:
        raise HarnessConfigError(
            "SCP_HARNESS is required and must be non-empty before running r2-skill-mage harness workflows."
        )
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", harness):
        raise HarnessConfigError(
            f"SCP_HARNESS has an invalid value {harness!r}. Use lowercase letters, digits, hyphens, or underscores."
        )
    return harness


def require_harness(env: Mapping[str, str] | None = None) -> str:
    """Return the required harness selector from the effective environment."""
    source_env = _read_env(env)
    return _validate_harness(source_env.get("SCP_HARNESS", ""))


def get_execution_root() -> Path:
    """Return the execution root used when invoking the harness adapter."""
    override = os.environ.get("SCP_PROJECT_ROOT", "").strip()
    if not override:
        return Path.cwd()

    project_root = Path(override).expanduser().resolve()
    if not project_root.exists():
        raise HarnessConfigError(f"SCP_PROJECT_ROOT does not exist: {project_root}")
    if not project_root.is_dir():
        raise HarnessConfigError(f"SCP_PROJECT_ROOT is not a directory: {project_root}")
    return project_root


def _require_supported_harness(harness: str) -> str:
    if harness not in EXECUTOR_MODEL_ENV_BY_HARNESS:
        raise HarnessConfigError(
            f"No harness model configuration is defined for {harness!r}. Add it to scripts/harness.py before using this harness."
        )
    return harness


def get_model_env_var(harness: str, role: HarnessModelRole) -> str:
    harness = _require_supported_harness(_validate_harness(harness))
    if role == "executor":
        return EXECUTOR_MODEL_ENV_BY_HARNESS[harness]
    return ANALYZER_MODEL_ENV_BY_HARNESS[harness]


def get_default_executor_model(harness: str) -> str:
    harness = _require_supported_harness(_validate_harness(harness))
    return DEFAULT_EXECUTOR_MODEL_BY_HARNESS[harness]


def resolve_executor_model(harness: str | None = None, env: Mapping[str, str] | None = None) -> str:
    """Resolve the executor model for the current harness, applying defaults."""
    source_env = _read_env(env)
    resolved_harness = _validate_harness(harness) if harness is not None else require_harness(source_env)
    resolved_harness = _require_supported_harness(resolved_harness)
    model = source_env.get(EXECUTOR_MODEL_ENV_BY_HARNESS[resolved_harness], "").strip()
    return model or DEFAULT_EXECUTOR_MODEL_BY_HARNESS[resolved_harness]


def resolve_analyzer_model(harness: str | None = None, env: Mapping[str, str] | None = None) -> str:
    """Resolve the analyzer model for the current harness, falling back to the executor model."""
    source_env = _read_env(env)
    resolved_harness = _validate_harness(harness) if harness is not None else require_harness(source_env)
    resolved_harness = _require_supported_harness(resolved_harness)
    model = source_env.get(ANALYZER_MODEL_ENV_BY_HARNESS[resolved_harness], "").strip()
    return model or resolve_executor_model(resolved_harness, source_env)


def get_harness_script() -> Path:
    """Return the harness adapter path, validating that it can be executed."""
    if not HARNESS_SCRIPT.exists():
        raise HarnessConfigError(f"Harness adapter not found: {HARNESS_SCRIPT}")
    if not os.access(HARNESS_SCRIPT, os.X_OK):
        raise HarnessConfigError(
            f"Harness adapter is not executable: {HARNESS_SCRIPT}. Run chmod +x on the script."
        )
    return HARNESS_SCRIPT


def build_harness_command() -> list[str]:
    """Build the command used to invoke the harness adapter."""
    return [str(get_harness_script())]


def build_harness_env(
    *,
    output_format: str,
    project_root: Path,
    model_role: HarnessModelRole = "executor",
    harness: str | None = None,
    include_partial_messages: bool = False,
    prompt_env: dict[str, str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> dict[str, str]:
    """Build environment variables for a harness invocation."""
    env = os.environ.copy()
    resolution_env = env.copy()
    if prompt_env:
        resolution_env.update(prompt_env)
    if extra_env:
        resolution_env.update({key: value for key, value in extra_env.items() if value is not None})

    resolved_harness = _validate_harness(harness) if harness is not None else require_harness(resolution_env)
    resolved_harness = _require_supported_harness(resolved_harness)
    if model_role == "executor":
        resolved_model = resolve_executor_model(resolved_harness, resolution_env)
    else:
        resolved_model = resolve_analyzer_model(resolved_harness, resolution_env)

    managed_keys = {
        "SCP_HARNESS",
        "SCP_MODEL",
        "SCP_EXECUTOR_MODEL",
        "SCP_ANALYZER_MODEL",
        *EXECUTOR_MODEL_ENV_BY_HARNESS.values(),
        *ANALYZER_MODEL_ENV_BY_HARNESS.values(),
        "SCP_OUTPUT_FORMAT",
        "SCP_INCLUDE_PARTIAL_MESSAGES",
        "SCP_PROMPT",
        "SCP_PROMPT_FILE",
        "SCP_PROJECT_ROOT",
        "SCP_SKILL_FILE",
        "SCP_SKILL_ALIAS",
        "SCP_SKILL_NAME",
        "SCP_SKILL_DESCRIPTION",
    }
    for key in managed_keys:
        env.pop(key, None)

    if prompt_env:
        env.update(prompt_env)

    if extra_env:
        for key, value in extra_env.items():
            if value is not None:
                env[key] = value

    env["SCP_HARNESS"] = resolved_harness
    env[get_model_env_var(resolved_harness, "executor")] = resolved_model
    env["SCP_OUTPUT_FORMAT"] = output_format
    env["SCP_INCLUDE_PARTIAL_MESSAGES"] = "1" if include_partial_messages else "0"
    env["SCP_PROJECT_ROOT"] = str(project_root)

    return env


@contextmanager
def temporary_prompt_env(prompt: str) -> Iterator[dict[str, str]]:
    """Provide prompt data via env or a temporary prompt file."""
    if "\x00" not in prompt and len(prompt.encode("utf-8")) <= PROMPT_ENV_MAX_BYTES:
        yield {"SCP_PROMPT": prompt}
        return

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(prompt)
        prompt_path = Path(handle.name)

    try:
        yield {"SCP_PROMPT_FILE": str(prompt_path)}
    finally:
        if prompt_path.exists():
            prompt_path.unlink()


@contextmanager
def temporary_skill_file(skill_alias: str, skill_name: str, skill_description: str) -> Iterator[Path]:
    """Create a temporary skill artifact for the harness adapter to register."""
    with tempfile.TemporaryDirectory(prefix="r2-skill-mage-") as temp_dir:
        skill_file = Path(temp_dir) / f"{skill_alias}.md"
        indented_desc = "\n  ".join(skill_description.split("\n"))
        skill_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        skill_file.write_text(skill_content)
        yield skill_file
