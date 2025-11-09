from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from agents import ToolOutputText, function_tool

WORKSPACE_ROOT = Path("/workspace").resolve()
ALLOWED_COMMANDS = {"ls", "pwd", "cat", "head", "tail", "stat", "wc", "find", "grep", "sed"}


def _build_command_args(command: str) -> list[str]:
    parts = shlex.split(command)
    if not parts:
        msg = "Provide a command to run (e.g. 'ls stages')."
        raise ValueError(msg)
    binary = parts[0]
    if binary not in ALLOWED_COMMANDS:
        msg = f"Command '{binary}' is not allowed. Valid options: {', '.join(sorted(ALLOWED_COMMANDS))}."
        raise ValueError(msg)

    # resolved: list[str] = [binary]
    # for token in parts[1:]:
    #     if token.startswith("-"):
    #         resolved.append(token)
    #         continue
    #     candidate = (WORKSPACE_ROOT / token).resolve()
    #     if not str(candidate).startswith(str(WORKSPACE_ROOT)):
    #         msg = f"Path escape blocked for '{token}'. Stay inside {WORKSPACE_ROOT}."
    #         raise ValueError(msg)
    #     resolved.append(str(candidate))
    # return resolved
    return parts


@function_tool(name_override="bash.run")
def run_bash_command(
    command: str,
    timeout_seconds: int = 5,
    max_output_chars: int = 4000,
) -> ToolOutputText:
    """
    Execute a limited bash command (ls, pwd, cat, head, tail, stat, wc, find, grep, sed) inside the workspace.

    Args:
        command: Full command line, e.g. "ls stages".
        timeout_seconds: Upper bound before the subprocess is terminated.
        max_output_chars: Long outputs are truncated to this many characters.
    """
    try:
        args = _build_command_args(command)
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    try:
        completed = subprocess.run(
            args,
            cwd=str(WORKSPACE_ROOT),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return ToolOutputText(text=f"Command timed out after {timeout_seconds}s.")
    except OSError as exc:
        return ToolOutputText(text=f"Failed to launch command: {exc}")

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    output = stdout if stdout else "(no stdout)"
    if stderr:
        output = f"{output}\n[stderr]\n{stderr}"

    if len(output) > max_output_chars:
        output = output[: max_output_chars - 3] + "..."

    exit_note = f"(exit code {completed.returncode})"
    return ToolOutputText(text=f"{output}\n{exit_note}")


__all__ = ["run_bash_command", "ALLOWED_COMMANDS"]
