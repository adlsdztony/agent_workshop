"""
Stage 1 activity starter.

Goal: build a write-enabled agent that implements the task in
`stages/stage1/activity/code_task.py` using a custom write tool.
Run with: python -m stages.stage1.activity.starter_agent --verbose
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from agents import Agent, ModelSettings, Runner, ToolOutputText, function_tool

from utils.bash_tool import run_bash_command
from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model

WORKSPACE_ROOT = Path("/workspace").resolve()
TASK_FILE = "stages/stage1/activity/code_task.py"


def _resolve_workspace_path(path: str, *, ensure_parent: bool = True) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / path
    resolved = candidate.resolve()
    if not str(resolved).startswith(str(WORKSPACE_ROOT)):
        msg = f"Path escape blocked for '{path}'. Stay inside {WORKSPACE_ROOT}."
        raise ValueError(msg)
    if resolved.is_dir():
        msg = f"'{path}' is a directory. write.file targets files only."
        raise ValueError(msg)
    if ensure_parent:
        resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


@function_tool(name_override="read.file")
def read_text_file(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    max_output_chars: int = 4000,
) -> ToolOutputText:
    """
    Read a workspace file and show line numbers for easier surgical edits.

    Activity author note: delete the implementation below this docstring to hand
    learners a partially completed read tool.
    """
    try:
        target = _resolve_workspace_path(path, ensure_parent=False)
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    if not target.exists():
        return ToolOutputText(text=f"{path} does not exist.")

    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        return ToolOutputText(text=f"Failed to read file: {exc}")

    lines = text.splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return ToolOutputText(text="(file is empty)")

    if start_line is None and end_line is None:
        start = 1
        end = total_lines
    else:
        if start_line is None:
            return ToolOutputText(text="Provide start_line when using end_line.")
        if start_line < 1 or (end_line is not None and end_line < start_line):
            return ToolOutputText(text="Line numbers must increase.")
        start = start_line
        end = end_line if end_line is not None else start_line
        if end > total_lines:
            return ToolOutputText(
                text=f"File only has {total_lines} lines; requested {end}."
            )

    numbered = []
    for idx in range(start, end + 1):
        line_text = lines[idx - 1] if idx - 1 < total_lines else ""
        numbered.append(f"{idx:>4}: {line_text}")

    result = "\n".join(numbered)
    if len(result) > max_output_chars:
        result = result[: max_output_chars - 3] + "..."
    return ToolOutputText(text=result)


def _replace_line_range(
    original: str, start_line: int, end_line: int, new_block: str
) -> str:
    lines = original.splitlines(keepends=True)
    total_lines = len(lines)
    if total_lines == 0:
        msg = "File is empty; unable to replace specific line ranges."
        raise ValueError(msg)
    if start_line < 1 or end_line < start_line or end_line > total_lines:
        msg = (
            f"Invalid range {start_line}-{end_line}. "
            f"File currently has {total_lines} lines."
        )
        raise ValueError(msg)
    start_idx = start_line - 1
    end_idx = end_line
    return "".join(lines[:start_idx]) + new_block + "".join(lines[end_idx:])


@function_tool(name_override="write.file")
def write_text_file(
    path: str,
    content: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> ToolOutputText:
    """
    Replace a specific line range in a workspace file with UTF-8 text.

    Activity author note: delete the implementation below this docstring to hand
    learners a partially completed write tool.
    """
    try:
        target = _resolve_workspace_path(path)
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    if start_line is None or end_line is None:
        return ToolOutputText(
            text="write.file only supports line-range replacements; provide start_line and end_line."
        )

    try:
        original = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ToolOutputText(
            text="File does not exist yet; populate it before using write.file."
        )
    except OSError as exc:
        return ToolOutputText(text=f"Failed to read file: {exc}")

    try:
        updated = _replace_line_range(
            original,
            start_line,
            end_line,
            content,
        )
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    try:
        target.write_text(updated, encoding="utf-8")
    except OSError as exc:
        return ToolOutputText(text=f"Failed to write file: {exc}")
    return ToolOutputText(
        text=(
            f"Replaced lines {start_line}-{end_line} in {path} "
            f"with {len(content)} characters."
        )
    )


async def run_activity(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    write_agent = Agent(
        name="Workshop Write Coach",
        instructions=(
            "You finish coding chores inside this repository.\n"
            f"Focus file: `{TASK_FILE}`. Implement `format_stage_report` to match the\n"
            "spec in that file by calling the provided tools.\n\n"
            "Workflow:\n"
            f"1. Use `read.file`\n"
            "   (with optional line ranges) to read the task and gather any additional\n"
            "   context you need.\n"
            "2. Outline your plan before editing so the reviewer understands your\n"
            "   approach.\n"
            "3. Call `write.file` with the `start_line`/`end_line` parameters to perform\n"
            "   targeted replacements inside the file.\n"
            "4. Verify the change by re-reading the file\n"
            "5. In your final response, summarize what you changed and cite the specific\n"
            "   commands/tools that informed your work."
        ),
        tools=[
            run_bash_command,
            read_text_file,
            write_text_file,
        ],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    result = await Runner.run(
        write_agent,
        (
            "Use the read.file and write.file tools to implement format_stage_report in "
            f"{TASK_FILE}, then explain how the result satisfies the requirements."
        ),
        hooks=hooks,
        max_turns=50,
    )
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(run_activity(verbose=args.verbose))
