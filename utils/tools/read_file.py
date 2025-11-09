from __future__ import annotations

from agents import ToolOutputText, function_tool
from utils.workspace_path import resolve_workspace_path


@function_tool(name_override="read.file")
def read_text_file(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    max_output_chars: int = 4000,
) -> ToolOutputText:
    """
    Read a workspace file and show line numbers for easier surgical edits.
    """

    try:
        target = resolve_workspace_path(path, ensure_parent=False)
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

    # TODO: Numbering each emitted line and clamping the overall response to
    # ``max_output_chars`` characters, adding ``...`` when truncated.

    return ToolOutputText(
        text=(
            "read.file is not implemented yet. Open utils/tools/read_file.py "
            "and follow the docstring instructions."
        )
    )
