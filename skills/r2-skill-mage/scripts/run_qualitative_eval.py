#!/usr/bin/env python3
"""Run a single qualitative eval through the configured harness.

Unlike run_eval.py (which only checks whether a skill triggers), this script
captures the full assistant response and saves it for human review. It routes
through the same harness dispatch system (SCP_HARNESS + run-harness.sh), so
the eval runs in the *selected* harness — not in whichever agent the user is
currently talking to.

Usage:
    SCP_HARNESS=copilot python -m scripts.run_qualitative_eval \
        --prompt "Create a dashboard for sales data" \
        --skill-path /path/to/my-skill \
        --output-dir /path/to/workspace/iteration-1/eval-0/with_skill \
        --with-skill

    SCP_HARNESS=claude python -m scripts.run_qualitative_eval \
        --prompt "Create a dashboard for sales data" \
        --output-dir /path/to/workspace/iteration-1/eval-0/without_skill
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from scripts.harness import (
    build_harness_command,
    build_harness_env,
    get_execution_root,
    require_harness,
    resolve_executor_model,
    temporary_prompt_env,
    temporary_skill_file,
)
from scripts.utils import parse_skill_md


def run_qualitative_eval(
    prompt: str,
    output_dir: Path,
    project_root: Path,
    skill_path: Path | None = None,
    timeout: int = 300,
) -> dict:
    """Run a qualitative eval through the harness and capture full output.

    Returns a dict with metadata about the run.
    """
    skill_name = ""
    skill_description = ""
    clean_name = ""

    if skill_path is not None:
        skill_name, skill_description, _ = parse_skill_md(skill_path)
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        clean_name = f"{skill_name}-qual-{unique_id}"

    # Build the harness environment
    extra_env = {}
    prompt_env_context = temporary_prompt_env(prompt)

    with prompt_env_context as prompt_env:
        if skill_path is not None:
            with temporary_skill_file(clean_name, skill_name, skill_description) as skill_file:
                extra_env.update({
                    "SCP_SKILL_ALIAS": clean_name,
                    "SCP_SKILL_NAME": skill_name,
                    "SCP_SKILL_DESCRIPTION": skill_description,
                    "SCP_SKILL_FILE": str(skill_file),
                })

                env = build_harness_env(
                    output_format="stream-json",
                    project_root=project_root,
                    include_partial_messages=True,
                    prompt_env=prompt_env,
                    extra_env=extra_env,
                )

                return _run_and_capture(env, project_root, output_dir, timeout)
        else:
            env = build_harness_env(
                output_format="stream-json",
                project_root=project_root,
                include_partial_messages=True,
                prompt_env=prompt_env,
                extra_env=extra_env,
            )

            return _run_and_capture(env, project_root, output_dir, timeout)


def _run_and_capture(
    env: dict,
    project_root: str | Path,
    output_dir: Path,
    timeout: int,
) -> dict:
    """Run the harness subprocess and capture full output."""
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    process = subprocess.Popen(
        build_harness_command(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(project_root),
        env=env,
        start_new_session=True,
    )

    full_text = ""
    accumulated_content = []
    tool_uses = []
    triggered_skills = []

    try:
        stdout, stderr = process.communicate(timeout=timeout)
        elapsed = time.time() - start_time

        if stdout:
            full_text = stdout.decode("utf-8", errors="replace")

        # Parse stream-json events to extract assistant content
        for line in full_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "")

            if event_type == "assistant":
                message = event.get("message", {})
                for content_item in message.get("content", []):
                    content_type = content_item.get("type", "")
                    if content_type == "text":
                        accumulated_content.append(content_item.get("text", ""))
                    elif content_type == "tool_use":
                        tool_uses.append({
                            "name": content_item.get("name", ""),
                            "input": content_item.get("input", {}),
                        })

            elif event_type == "stream_event":
                se = event.get("event", {})
                se_type = se.get("type", "")
                if se_type == "content_block_delta":
                    delta = se.get("delta", {})
                    if delta.get("type") == "text_delta":
                        accumulated_content.append(delta.get("text", ""))

            elif event_type == "result":
                result_data = event.get("result", "")
                if isinstance(result_data, str):
                    accumulated_content.append(result_data)

    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        elapsed = time.time() - start_time
        # Still capture whatever output we got
        if process.stdout:
            partial = process.stdout.read()
            if partial:
                full_text += partial.decode("utf-8", errors="replace")
            for line in full_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                event_type = event.get("type", "")
                if event_type == "assistant":
                    for content_item in event.get("message", {}).get("content", []):
                        if content_item.get("type") == "text":
                            accumulated_content.append(content_item.get("text", ""))
                elif event_type == "stream_event":
                    delta = event.get("event", {}).get("delta", {})
                    if delta.get("type") == "text_delta":
                        accumulated_content.append(delta.get("text", ""))

    combined_text = "".join(accumulated_content)

    # Save the transcript
    transcript_path = output_dir / "transcript.md"
    transcript_path.write_text(combined_text, encoding="utf-8")

    # Save raw stream output for grader analysis
    raw_path = output_dir / "raw_stream.jsonl"
    raw_path.write_text(full_text, encoding="utf-8")

    # Save metadata
    metadata = {
        "duration_seconds": round(elapsed, 1),
        "tool_uses": tool_uses,
        "output_chars": len(combined_text),
        "timed_out": elapsed >= timeout * 0.95,
        "transcript_path": str(transcript_path),
        "raw_path": str(raw_path),
    }
    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Run a qualitative eval through the configured harness."
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="The eval prompt to send through the harness.",
    )
    parser.add_argument(
        "--skill-path",
        default=None,
        help="Path to the skill directory. Omit for baseline (no-skill) runs.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save outputs (transcript, metadata, raw stream).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root for harness execution. Defaults to SCP_PROJECT_ROOT or cwd.",
    )

    args = parser.parse_args()

    harness = require_harness()
    model = resolve_executor_model()

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = get_execution_root()

    skill_path = Path(args.skill_path) if args.skill_path else None
    output_dir = Path(args.output_dir).resolve()

    print(f"Running qualitative eval via harness={harness} model={model}", file=sys.stderr)
    print(f"  Prompt: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}", file=sys.stderr)
    print(f"  Skill: {skill_path or '(baseline — no skill)'}", file=sys.stderr)
    print(f"  Output: {output_dir}", file=sys.stderr)

    metadata = run_qualitative_eval(
        prompt=args.prompt,
        output_dir=output_dir,
        project_root=project_root,
        skill_path=skill_path,
        timeout=args.timeout,
    )

    print(f"\nDone in {metadata['duration_seconds']}s.", file=sys.stderr)
    print(f"  Transcript: {metadata['transcript_path']}", file=sys.stderr)
    print(f"  Raw stream:  {metadata['raw_path']}", file=sys.stderr)


if __name__ == "__main__":
    main()