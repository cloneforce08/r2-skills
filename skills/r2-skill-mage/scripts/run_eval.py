#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes the harnessed agent to trigger
(read the skill) for a set of queries. Outputs results as JSON.
"""

import argparse
import json
import os
import select
import signal
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.harness import (
    HarnessConfigError,
    build_harness_command,
    build_harness_env,
    get_execution_root,
    require_harness,
    resolve_executor_model,
    temporary_prompt_env,
    temporary_skill_file,
)
from scripts.utils import parse_skill_md


def find_project_root() -> Path:
    """Return the execution root used for harness invocations."""
    return get_execution_root()


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a temporary skill artifact, asks the harness adapter to register it,
    then runs the raw query through the adapter. Uses partial stream events to
    detect triggering early rather than waiting for the full assistant message,
    which only arrives after tool execution.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"

    with temporary_skill_file(clean_name, skill_name, skill_description) as skill_file:
        with temporary_prompt_env(query) as prompt_env:
            env = build_harness_env(
                output_format="stream-json",
                project_root=Path(project_root),
                include_partial_messages=True,
                prompt_env=prompt_env,
                extra_env={
                    "SCP_SKILL_ALIAS": clean_name,
                    "SCP_SKILL_NAME": skill_name,
                    "SCP_SKILL_DESCRIPTION": skill_description,
                    "SCP_SKILL_FILE": str(skill_file),
                },
            )
            process = subprocess.Popen(
                build_harness_command(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root,
                env=env,
                start_new_session=True,
            )

        triggered = False
        start_time = time.time()
        buffer = ""
        raw_preview = ""
        early_outcome: bool | None = None
        timed_out = False
        # Track state for stream event detection
        pending_tool_name = None
        accumulated_json = ""

        def handle_event_line(line: str) -> bool | None:
            nonlocal pending_tool_name, accumulated_json, triggered

            line = line.strip()
            if not line:
                return None

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                return None

            # Early detection via stream events
            if event.get("type") == "stream_event":
                se = event.get("event", {})
                se_type = se.get("type", "")

                if se_type == "content_block_start":
                    cb = se.get("content_block", {})
                    if cb.get("type") == "tool_use":
                        tool_name = cb.get("name", "")
                        if tool_name in ("Skill", "Read"):
                            pending_tool_name = tool_name
                            accumulated_json = ""
                        else:
                            return False

                elif se_type == "content_block_delta" and pending_tool_name:
                    delta = se.get("delta", {})
                    if delta.get("type") == "input_json_delta":
                        accumulated_json += delta.get("partial_json", "")
                        if clean_name in accumulated_json:
                            return True

                elif se_type in ("content_block_stop", "message_stop"):
                    if pending_tool_name:
                        return clean_name in accumulated_json
                    if se_type == "message_stop":
                        return False

            # Fallback: full assistant message
            elif event.get("type") == "assistant":
                message = event.get("message", {})
                saw_tool_use = False
                for content_item in message.get("content", []):
                    if content_item.get("type") != "tool_use":
                        continue
                    saw_tool_use = True
                    tool_name = content_item.get("name", "")
                    tool_input = content_item.get("input", {})
                    if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                        triggered = True
                    elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                        triggered = True
                if saw_tool_use:
                    return triggered

            elif event.get("type") == "result":
                return triggered

            return None

        try:
            while time.time() - start_time < timeout:
                process_finished = False
                if process.poll() is not None:
                    remaining = process.stdout.read()
                    if remaining:
                        text = remaining.decode("utf-8", errors="replace")
                        buffer += text
                        raw_preview = (raw_preview + text)[-1000:]
                    process_finished = True
                else:
                    ready, _, _ = select.select([process.stdout], [], [], 1.0)
                    if not ready:
                        continue

                    chunk = os.read(process.stdout.fileno(), 8192)
                    if not chunk:
                        break
                    text = chunk.decode("utf-8", errors="replace")
                    buffer += text
                    raw_preview = (raw_preview + text)[-1000:]

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    outcome = handle_event_line(line)
                    if outcome is not None:
                        early_outcome = outcome
                        break

                if early_outcome is not None:
                    break

                if process_finished:
                    outcome = handle_event_line(buffer)
                    if outcome is not None:
                        early_outcome = outcome
                    break
            if early_outcome is not None:
                return early_outcome
            timed_out = True
        finally:
            # Clean up process on any exit path (return, exception, timeout)
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    process.wait(timeout=5)
                except ProcessLookupError:
                    pass
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()

        stderr_output = ""
        if process.stderr is not None:
            stderr_output = process.stderr.read().decode("utf-8", errors="replace").strip()

        if timed_out:
            return triggered
        if process.returncode not in (None, 0):
            detail = stderr_output or "no stderr output"
            raise RuntimeError(
                f"Harness adapter exited {process.returncode} while evaluating query {query!r}: {detail}"
            )
        preview = raw_preview.strip() or "<no output>"
        raise RuntimeError(
            "Harness adapter completed without emitting a recognizable terminal "
            f"stream-json event while evaluating query {query!r}. Output preview: {preview[:300]}"
        )


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
) -> dict:
    """Run the full eval set and return results."""
    resolve_executor_model()
    require_harness()
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    str(project_root),
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as exc:
                raise RuntimeError(f"Query failed for {query!r}: {exc}") from exc

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    try:
        resolve_executor_model()
        require_harness()
        eval_set = json.loads(Path(args.eval_set).read_text())
        skill_path = Path(args.skill_path)

        if not (skill_path / "SKILL.md").exists():
            print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
            sys.exit(1)

        name, original_description, content = parse_skill_md(skill_path)
        description = args.description or original_description
        project_root = find_project_root()
    except HarnessConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    try:
        output = run_eval(
            eval_set=eval_set,
            skill_name=name,
            description=description,
            num_workers=args.num_workers,
            timeout=args.timeout,
            project_root=project_root,
            runs_per_query=args.runs_per_query,
            trigger_threshold=args.trigger_threshold,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
