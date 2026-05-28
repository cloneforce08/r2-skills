#!/usr/bin/env python3
"""Run reusable smoke tests against the configured harness adapter.

This script exercises the three highest-value harness paths used by the
r2-skill-mage tooling:

1. Direct text-mode skill creation via ``scripts/run-harness.sh``.
2. Trigger evaluation via ``scripts.run_eval``.
3. Description improvement via ``scripts.improve_description``.

The tests use the real configured harness. ``SCP_HARNESS`` is required, while
model selection comes from harness-specific executor/analyzer variables with
defaults resolved in ``scripts.harness``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from scripts.harness import (
    PROMPT_ENV_MAX_BYTES,
    HarnessConfigError,
    build_harness_command,
    build_harness_env,
    require_harness,
    resolve_analyzer_model,
    resolve_executor_model,
)
from scripts.utils import parse_skill_md


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PYTHON_BIN = sys.executable or "python3"


@dataclass
class SmokeTestResult:
    name: str
    passed: bool
    summary: str
    artifact_dir: str | None
    details: dict[str, object]


def _write_text(path: Path, content: str) -> None:
    path.write_text(content)


def _store_process_outputs(artifact_dir: Path, result: subprocess.CompletedProcess[str]) -> None:
    _write_text(artifact_dir / "stdout.txt", result.stdout)
    _write_text(artifact_dir / "stderr.txt", result.stderr)


def _finalize_result(
    *,
    name: str,
    passed: bool,
    summary: str,
    artifact_dir: Path,
    keep_artifacts: bool,
    details: dict[str, object],
) -> SmokeTestResult:
    retained_dir: str | None = str(artifact_dir)
    if passed and not keep_artifacts:
        shutil.rmtree(artifact_dir)
        retained_dir = None

    return SmokeTestResult(
        name=name,
        passed=passed,
        summary=summary,
        artifact_dir=retained_dir,
        details=details,
    )


def _make_artifact_dir(base_dir: Path | None, prefix: str) -> Path:
    root = base_dir if base_dir else Path(tempfile.gettempdir())
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=root))


def _check_eval_cleanup(harness_name: str, project_root: Path) -> tuple[bool, str, list[str]]:
    """Run any harness-specific cleanup assertions for eval smoke tests."""
    if harness_name == "claude":
        commands_dir = project_root / ".claude" / "commands"
        commands_entries = sorted(p.name for p in commands_dir.iterdir()) if commands_dir.exists() else []
        return (not commands_entries, "claude_commands", commands_entries)

    return (True, "none", [])


def run_creation_smoke_test(keep_artifacts: bool, artifact_root: Path | None) -> SmokeTestResult:
    harness_name = require_harness()
    artifact_dir = _make_artifact_dir(artifact_root, f"scp-smoke-{harness_name}-create.")
    project_root = artifact_dir / "project-root"
    project_root.mkdir()
    prompt_file = artifact_dir / "create_prompt.txt"
    generated_skill_dir = artifact_dir / "generated-skill"
    generated_skill_dir.mkdir()
    generated_skill_file = generated_skill_dir / "SKILL.md"

    prompt = (
        "Return exactly the following SKILL.md contents and nothing else.\n"
        "---\n"
        "name: smoke-weather-alerts\n"
        "description: Use this skill whenever the user asks for a concise weather alert summary.\n"
        "---\n\n"
        "# Smoke Weather Alerts\n\n"
        "1. Ask for the city or region if it is missing.\n"
        "2. Summarize active weather alerts first.\n"
        "3. Keep the response concise and practical.\n"
    )
    _write_text(prompt_file, prompt)

    env = build_harness_env(
        output_format="text",
        project_root=project_root,
        prompt_env={"SCP_PROMPT_FILE": str(prompt_file)},
    )
    result = subprocess.run(
        build_harness_command(),
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
    )
    _store_process_outputs(artifact_dir, result)

    details: dict[str, object] = {
        "harness": harness_name,
        "returncode": result.returncode,
        "prompt_file": str(prompt_file),
    }

    if result.returncode != 0:
        details["stderr_excerpt"] = result.stderr[-1000:]
        return _finalize_result(
            name="creation",
            passed=False,
            summary="Direct text-mode harness call failed.",
            artifact_dir=artifact_dir,
            keep_artifacts=keep_artifacts,
            details=details,
        )

    _write_text(generated_skill_file, result.stdout)

    try:
        name, description, content = parse_skill_md(generated_skill_dir)
    except Exception as exc:
        details["parse_error"] = str(exc)
        details["stdout_excerpt"] = result.stdout[:1000]
        return _finalize_result(
            name="creation",
            passed=False,
            summary="Harness returned text, but it was not a valid SKILL.md artifact.",
            artifact_dir=artifact_dir,
            keep_artifacts=keep_artifacts,
            details=details,
        )

    has_heading = "# Smoke Weather Alerts" in content
    passed = (
        name == "smoke-weather-alerts"
        and bool(description)
        and has_heading
        and result.stdout.lstrip().startswith("---\n")
    )
    details.update({
        "parsed_name": name,
        "parsed_description": description,
        "has_heading": has_heading,
        "output_bytes": len(result.stdout.encode("utf-8")),
    })

    summary = (
        "Harness returned a parseable SKILL.md artifact in text mode."
        if passed
        else "Harness returned text, but the generated skill artifact did not match the expected structure."
    )
    return _finalize_result(
        name="creation",
        passed=passed,
        summary=summary,
        artifact_dir=artifact_dir,
        keep_artifacts=keep_artifacts,
        details=details,
    )


def run_eval_smoke_test(keep_artifacts: bool, artifact_root: Path | None) -> SmokeTestResult:
    harness_name = require_harness()
    artifact_dir = _make_artifact_dir(artifact_root, f"scp-smoke-{harness_name}-eval.")
    skill_dir = artifact_dir / "skill"
    project_root = artifact_dir / "project-root"
    skill_dir.mkdir()
    project_root.mkdir()

    skill_content = """---
name: neon-ledger
description: Use this skill whenever the user mentions the exact phrase \"neon octopus ledger\" or asks for the neon octopus ledger ritual, onboarding, checklist, or verification sequence.
---

# Neon Octopus Ledger

1. Explain the ritual in order.
2. Include verification steps.
3. Keep the answer procedural.
"""
    _write_text(skill_dir / "SKILL.md", skill_content)

    eval_set = [
        {
            "query": "I'm onboarding a new analyst to our neon octopus ledger ritual. Please walk through the full neon octopus ledger checklist, including the verification sequence and the order of checks.",
            "should_trigger": True,
        }
    ]
    eval_path = artifact_dir / "eval.json"
    _write_text(eval_path, json.dumps(eval_set, indent=2))

    env = os.environ.copy()
    env["SCP_PROJECT_ROOT"] = str(project_root)
    result = subprocess.run(
        [
            PYTHON_BIN,
            "-m",
            "scripts.run_eval",
            "--eval-set",
            str(eval_path),
            "--skill-path",
            str(skill_dir),
            "--num-workers",
            "1",
            "--runs-per-query",
            "1",
            "--timeout",
            "90",
            "--verbose",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=240,
    )
    _store_process_outputs(artifact_dir, result)

    details: dict[str, object] = {"harness": harness_name, "returncode": result.returncode}
    if result.returncode != 0:
        details["stderr_excerpt"] = result.stderr[-1500:]
        return _finalize_result(
            name="eval",
            passed=False,
            summary="run_eval failed to complete successfully.",
            artifact_dir=artifact_dir,
            keep_artifacts=keep_artifacts,
            details=details,
        )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        details["json_error"] = str(exc)
        details["stdout_excerpt"] = result.stdout[:1500]
        return _finalize_result(
            name="eval",
            passed=False,
            summary="run_eval completed, but stdout was not valid JSON.",
            artifact_dir=artifact_dir,
            keep_artifacts=keep_artifacts,
            details=details,
        )

    cleanup_ok, cleanup_scope, cleanup_entries = _check_eval_cleanup(harness_name, project_root)
    results = output.get("results", [])
    first_result = results[0] if results else {}
    passed = (
        output.get("summary", {}).get("passed") == 1
        and output.get("summary", {}).get("total") == 1
        and bool(first_result.get("pass"))
        and first_result.get("trigger_rate", 0) > 0
        and cleanup_ok
    )
    details.update({
        "summary": output.get("summary", {}),
        "first_result": first_result,
        "cleanup_scope": cleanup_scope,
        "cleanup_entries": cleanup_entries,
    })

    summary = (
        "run_eval triggered the temporary skill and passed the harness cleanup check."
        if passed
        else "run_eval returned, but either the skill did not trigger or the harness cleanup check failed."
    )
    return _finalize_result(
        name="eval",
        passed=passed,
        summary=summary,
        artifact_dir=artifact_dir,
        keep_artifacts=keep_artifacts,
        details=details,
    )


def run_improve_description_smoke_test(keep_artifacts: bool, artifact_root: Path | None) -> SmokeTestResult:
    harness_name = require_harness()
    artifact_dir = _make_artifact_dir(artifact_root, f"scp-smoke-{harness_name}-improve.")
    skill_dir = artifact_dir / "skill"
    project_root = artifact_dir / "project-root"
    skill_dir.mkdir()
    project_root.mkdir()

    body_lines = [
        "# Ledger Rules",
        "",
        "This skill documents a fictional ledger workflow.",
        "",
    ]
    for index in range(600):
        body_lines.append(
            f"- Reference note {index}: neon octopus ledger handling guidance for scenario {index}."
        )

    original_description = "Help with stuff."
    _write_text(
        skill_dir / "SKILL.md",
        "---\n"
        "name: ledger-rules\n"
        f"description: {original_description}\n"
        "---\n\n"
        + "\n".join(body_lines)
        + "\n",
    )

    eval_results_path = artifact_dir / "eval-results.json"
    eval_results = {
        "description": original_description,
        "results": [
            {
                "query": "I need the neon octopus ledger onboarding ritual and checklist.",
                "should_trigger": True,
                "trigger_rate": 0.0,
                "triggers": 0,
                "runs": 1,
                "pass": False,
            }
        ],
        "summary": {"passed": 0, "failed": 1, "total": 1},
    }
    _write_text(eval_results_path, json.dumps(eval_results, indent=2))

    env = os.environ.copy()
    env["SCP_PROJECT_ROOT"] = str(project_root)
    result = subprocess.run(
        [
            PYTHON_BIN,
            "-m",
            "scripts.improve_description",
            "--eval-results",
            str(eval_results_path),
            "--skill-path",
            str(skill_dir),
            "--verbose",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
    )
    _store_process_outputs(artifact_dir, result)

    skill_size_bytes = (skill_dir / "SKILL.md").stat().st_size
    details: dict[str, object] = {
        "harness": harness_name,
        "returncode": result.returncode,
        "skill_size_bytes": skill_size_bytes,
        "prompt_env_threshold_bytes": PROMPT_ENV_MAX_BYTES,
    }
    if result.returncode != 0:
        details["stderr_excerpt"] = result.stderr[-1500:]
        return _finalize_result(
            name="improve-description",
            passed=False,
            summary="improve_description failed to complete successfully.",
            artifact_dir=artifact_dir,
            keep_artifacts=keep_artifacts,
            details=details,
        )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        details["json_error"] = str(exc)
        details["stdout_excerpt"] = result.stdout[:1500]
        return _finalize_result(
            name="improve-description",
            passed=False,
            summary="improve_description completed, but stdout was not valid JSON.",
            artifact_dir=artifact_dir,
            keep_artifacts=keep_artifacts,
            details=details,
        )

    improved_description = output.get("description", "")
    history = output.get("history", [])
    passed = (
        bool(improved_description)
        and improved_description != original_description
        and len(improved_description) <= 1024
        and "neon octopus ledger" in improved_description.lower()
        and len(history) == 1
        and skill_size_bytes > PROMPT_ENV_MAX_BYTES
    )
    details.update({
        "description_length": len(improved_description),
        "improved_description": improved_description,
        "history_length": len(history),
    })

    summary = (
        "improve_description returned a bounded replacement description and exercised prompt-file transport."
        if passed
        else "improve_description returned, but the improved description did not meet the expected contract."
    )
    return _finalize_result(
        name="improve-description",
        passed=passed,
        summary=summary,
        artifact_dir=artifact_dir,
        keep_artifacts=keep_artifacts,
        details=details,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run reusable smoke tests for the configured harness adapter")
    parser.add_argument(
        "--test",
        action="append",
        choices=["creation", "eval", "improve-description", "all"],
        help="Smoke test(s) to run. Defaults to all.",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep temporary artifact directories even for passing tests.",
    )
    parser.add_argument(
        "--artifact-root",
        default=None,
        help="Directory under which to create smoke-test artifact folders.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the final summary as JSON.",
    )
    return parser.parse_args()


def select_tests(raw_tests: list[str] | None) -> list[str]:
    if not raw_tests or "all" in raw_tests:
        return ["creation", "eval", "improve-description"]
    ordered = ["creation", "eval", "improve-description"]
    return [test_name for test_name in ordered if test_name in raw_tests]


def print_human_summary(results: list[SmokeTestResult]) -> None:
    harness_name = require_harness()
    print(f"Harness: {harness_name}")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.summary}")
        if result.artifact_dir:
            print(f"  artifacts: {result.artifact_dir}")

    passed = sum(1 for result in results if result.passed)
    total = len(results)
    print(f"Summary: {passed}/{total} smoke tests passed.")


def main() -> int:
    args = parse_args()

    try:
        executor_model = resolve_executor_model()
        analyzer_model = resolve_analyzer_model()
        harness_name = require_harness()
    except HarnessConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    artifact_root = Path(args.artifact_root).expanduser().resolve() if args.artifact_root else None
    selected_tests = select_tests(args.test)
    test_functions: dict[str, Callable[[bool, Path | None], SmokeTestResult]] = {
        "creation": run_creation_smoke_test,
        "eval": run_eval_smoke_test,
        "improve-description": run_improve_description_smoke_test,
    }

    results = [test_functions[test_name](args.keep_artifacts, artifact_root) for test_name in selected_tests]
    payload = {
        "harness": harness_name,
        "executor_model": executor_model,
        "analyzer_model": analyzer_model,
        "passed": all(result.passed for result in results),
        "results": [asdict(result) for result in results],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human_summary(results)

    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())