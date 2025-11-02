"""
Stage 1 activity starter.

Goal: build a "project scout" agent that reports on repository structure.
Run with: python stages/stage1/activity/starter_agent.py
"""

from __future__ import annotations

import asyncio
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


WORKSPACE_ROOT = Path("/workspace").resolve()

# TODO: expand this whitelist if your report flow needs extra commands.
ALLOWED_COMMANDS: set[str] = {"pwd", "ls", "cat"}


def _format_command(command: Sequence[str]) -> str:
    return " ".join(command)


def _is_safe_path(command: Sequence[str]) -> bool:
    for token in command[1:]:
        if token.startswith("/"):
            return False
        if token.startswith(".."):
            return False
    return True


def safe_shell_executor(request: LocalShellCommandRequest) -> str:
    """
    Restricted shell executor shared by the demo and your activity agent.

    Customize the whitelist and output formatting to steer how the model
    can explore the repository.
    """
    command = request.data.action.command
    program = command[0]

    if program not in ALLOWED_COMMANDS:
        return (
            f"Command '{program}' is not allowed yet. "
            "Update ALLOWED_COMMANDS in starter_agent.py if this command is safe."
        )

    if not _is_safe_path(command):
        return "Command blocked: keep paths inside the workshop workspace."

    try:
        completed = subprocess.run(
            command,
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return f"Executor error: {_format_command(command)} -> {exc}"

    if completed.returncode != 0:
        return (
            f"Command '{_format_command(command)}' exited with {completed.returncode}.\n"
            f"stderr:\n{completed.stderr.strip() or '(empty)'}"
        )

    return completed.stdout.strip() or "(no stdout from command)"


async def run_activity() -> None:
    # TODO: rewrite the instructions so the agent understands the reporting goal.
    project_scout = Agent(
        name="Project Scout",
        instructions=(
            "Replace this text with system guidance that asks for a Markdown checklist "
            "covering: root directories, Dockerfile presence, and a recommended next command."
        ),
        tools=[LocalShellTool(executor=safe_shell_executor)],
        model="qwen:30b",
        model_settings=ModelSettings(temperature=0.2),
    )

    # TODO: adjust the question to focus the agent on the reporting task you designed.
    result = await Runner.run(project_scout, "Draft the initial project scout report.")
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(run_activity())
