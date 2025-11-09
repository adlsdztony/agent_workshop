
from __future__ import annotations

from pathlib import Path
from agents import ToolOutputText, function_tool
from utils.workspace_path import resolve_workspace_path


WORKSPACE_ROOT = Path("/workspace").resolve()
TASK_FILE = "stages/stage1/activity/test_read_file.py"

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
        target = resolve_workspace_path(path)
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
