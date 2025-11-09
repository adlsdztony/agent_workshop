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

    Implement this tool by:

    1. Resolving ``path`` through ``resolve_workspace_path`` (with
       ``ensure_parent=False`` so reading brand new files is allowed).
    2. Handling missing files, unreadable files, and empty files gracefully by
       returning a descriptive ``ToolOutputText``.
    3. Supporting optional ``start_line``/``end_line`` parameters that return
       only the requested slice once validated.
    4. Numbering each emitted line and clamping the overall response to
       ``max_output_chars`` characters, adding ``...`` when truncated.

    Delete the temporary return value below once you have a real
    implementation.
    """
    return ToolOutputText(
        text=(
            "read.file is not implemented yet. Open utils/tools/read_file.py "
            "and follow the docstring instructions."
        )
    )
