"""
Stage 1 demo: minimal agent that uses the built-in LocalShellTool to explore the repo.
Run with: python stages/stage1/demo.py
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from agents import (
    Agent,
    LocalShellCommandRequest,
    LocalShellTool,
    ModelSettings,
    Runner,
)


ALLOWED_COMMANDS: set[str] = {"pwd", "ls", "cat"}
WORKSPACE_ROOT = Path("/workspace").resolve()


def _format_command(command: Sequence[str]) -> str:
    """Return a human-friendly command string."""
    return " ".join(command)


def _is_safe_path(command: Sequence[str]) -> bool:
    """Prevent the model from reading outside the workshop workspace."""
    for token in command[1:]:
        if token.startswith("/"):
            return False
        if token.startswith(".."):
            return False
    return True


def safe_shell_executor(request: LocalShellCommandRequest) -> str:
    """
    Execute a whitelisted shell command and return its output.

    LocalShellExecutor can be synchronous; the SDK awaits the result if needed.
    The executor receives the original RunContext through `request.ctx_wrapper`
    should you need it for deeper scenarios later on.
    """
    command = request.data.action.command
    program = command[0]

    if program not in ALLOWED_COMMANDS:
        return f"Command '{program}' is not allowed. Allowed commands: {', '.join(ALLOWED_COMMANDS)}"

    if shutil.which(program) is None:
        return f"The binary '{program}' is not available in this environment."

    if not _is_safe_path(command):
        return "Blocked command: stay within the workshop workspace."

    try:
        completed = subprocess.run(
            command,
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out: {_format_command(command)}"
    except Exception as exc:  # noqa: BLE001 - surface executor errors to the model
        return f"Executor error running {_format_command(command)}: {exc}"

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    if completed.returncode != 0:
        return (
            f"Command '{_format_command(command)}' exited with {completed.returncode}.\n"
            f"stderr:\n{stderr or '(empty)'}"
        )

    return stdout or "(command produced no stdout)"


async def main() -> None:
    shell_tool = LocalShellTool(executor=safe_shell_executor)

    explorer = Agent(
        name="Workspace Explorer",
        instructions=(
            "You are a local project assistant. Use the shell tool to inspect the repository, "
            "then answer the user concisely. Explain what you ran when relevant."
        ),
        tools=[shell_tool],
        model="qwen:30b",
        model_settings=ModelSettings(temperature=0.2),
    )

    question = (
        "List the root level files in this project and tell me what looks important."
    )

    print("> Asking the agent:", question)
    result = await Runner.run(explorer, question)

    print("\n=== Final Answer ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
