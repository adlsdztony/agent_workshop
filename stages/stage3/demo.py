"""
Stage 3 demo: multi-agent workflow with handoffs and shared context.
Run with: python stages/stage3/demo.py
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Sequence

from agents import (
    Agent,
    LocalShellCommandRequest,
    LocalShellTool,
    ModelSettings,
    Runner,
    RunContextWrapper,
    ToolOutputText,
    function_tool,
)
from agents.mcp import MCPServerStdio, MCPServerStdioParams


WORKSPACE_ROOT = Path("/workspace").resolve()
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class WorkflowState:
    """Shared context that persists across agent handoffs."""

    research_notes: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


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
    """Restricted shell executor that also logs output into the shared context."""
    command = request.data.action.command
    program = command[0]

    allowed = {"pwd", "ls", "cat", "head"}
    if program not in allowed:
        return f"Command '{program}' not allowed. Allowed: {', '.join(sorted(allowed))}"
    if shutil.which(program) is None:
        return f"Unable to locate '{program}' in PATH."
    if not _is_safe_path(command):
        return "Command blocked: keep paths inside the workspace."

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

    output = completed.stdout.strip() or "(no stdout)"
    if completed.returncode != 0:
        output = (
            f"Command '{_format_command(command)}' exited with {completed.returncode}\n"
            f"stderr:\n{completed.stderr.strip() or '(empty)'}"
        )

    # Record the command + output into the shared context if available.
    state = getattr(request.ctx_wrapper, "context", None)
    if isinstance(state, WorkflowState):
        state.research_notes.append(f"$ {_format_command(command)} -> {output}")

    return output


def _resolve_relative_path(relative_path: str) -> Path:
    candidate = (WORKSPACE_ROOT / relative_path).resolve()
    if not str(candidate).startswith(str(WORKSPACE_ROOT)):
        msg = f"Path escape blocked for '{relative_path}'."
        raise ValueError(msg)
    return candidate


@function_tool(name_override="workflow.capture_todos")
def capture_todos(
    ctx: RunContextWrapper[WorkflowState],
    relative_path: str,
    limit: int = 5,
) -> ToolOutputText:
    """
    Record TODO/FIXME markers for the shared context and return a formatted snippet.

    Args:
        relative_path: File path relative to the workspace root.
        limit: Maximum number of matches to include.
    """
    try:
        file_path = _resolve_relative_path(relative_path)
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    if not file_path.is_file():
        return ToolOutputText(text=f"No file found at {relative_path}")

    matches: list[str] = []
    with file_path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, start=1):
            if "TODO" in line or "FIXME" in line:
                matches.append(f"L{idx}: {line.strip()}")
            if len(matches) >= limit:
                break

    if not matches:
        return ToolOutputText(text=f"No TODO markers in {relative_path}")

    ctx.context.research_notes.append(
        f"Found {len(matches)} TODO markers in {relative_path}:\n" + "\n".join(matches)
    )

    display = "\n".join(f"- {m}" for m in matches)
    return ToolOutputText(text=f"TODO summary for {relative_path}:\n{display}")


@function_tool(name_override="workflow.save_plan")
def save_plan(
    ctx: RunContextWrapper[WorkflowState],
    steps: list[str],
    risks: list[str] | None = None,
) -> str:
    """Persist the planner's steps (and optional risks) in the shared context."""
    ctx.context.action_items = steps
    if risks:
        ctx.context.risks.extend(risks)
    return f"Stored {len(steps)} workflow steps and {len(risks or [])} risks."


@function_tool(name_override="workflow.log_risk")
def log_risk(
    ctx: RunContextWrapper[WorkflowState],
    description: str,
    severity: Literal["low", "medium", "high"] = "medium",
) -> str:
    """Append a risk/guardrail recommendation."""
    ctx.context.risks.append(f"[{severity.upper()}] {description}")
    return f"Recorded {severity} risk."


CURRICULUM_SERVER_PARAMS = MCPServerStdioParams(
    command=sys.executable,
    args=[str(REPO_ROOT / "stages/stage2/mcp_servers/curriculum_server.py")],
    cwd=str(REPO_ROOT),
)


async def main() -> None:
    shell_tool = LocalShellTool(executor=safe_shell_executor)
    curriculum_server = MCPServerStdio(
        params=CURRICULUM_SERVER_PARAMS,
        cache_tools_list=True,
        name="Curriculum Server",
    )

    research_agent = Agent(
        name="Research Agent",
        handoff_description="Gathers repository signals and curriculum facts.",
        instructions=(
            "Investigate the repository to find open TODOs and relevant workshop context. "
            "Use the shell tool for quick file inspection and curriculum.fetch_stage_summary via MCP "
            "to enrich your notes. After the tools run, summarise findings for the planner."
        ),
        tools=[shell_tool, capture_todos],
        mcp_servers=[curriculum_server],
        model="qwen:30b",
        model_settings=ModelSettings(temperature=0.2),
    )

    planner_agent = Agent(
        name="Planner Agent",
        handoff_description="Transforms research into a concrete workflow plan.",
        instructions=(
            "Read the research summary and design a three-step workflow to improve the repo's Stage 2 assets. "
            "Each step should mention tools or MCP data to reuse. Call workflow.save_plan with the final steps."
        ),
        tools=[save_plan],
        model="qwen:30b",
        model_settings=ModelSettings(temperature=0.3),
    )

    reviewer_agent = Agent(
        name="Reviewer Agent",
        handoff_description="Stress-tests the workflow, adding guardrails.",
        instructions=(
            "Inspect the proposed workflow steps and add at least one risk or validation check per step. "
            "Report them via workflow.log_risk and provide a concise reviewer summary."
        ),
        tools=[log_risk],
        model="qwen:30b",
        model_settings=ModelSettings(temperature=0.1),
    )

    coordinator = Agent(
        name="Workflow Coordinator",
        instructions=(
            "Coordinate the multi-agent workflow in order:\n"
            "1. Call the Research Agent to gather context.\n"
            "2. Pass its insights to the Planner Agent to create steps.\n"
            "3. Delegate to the Reviewer Agent for guardrails.\n"
            "Finally, synthesize a JSON object with keys research, plan, and risks summarising the shared context."
        ),
        handoffs=[research_agent, planner_agent, reviewer_agent],
        model="qwen:30b",
        model_settings=ModelSettings(temperature=0.05),
    )

    prompt = (
        "We need a Stage 3 workflow that prepares learners for multi-agent collaboration. "
        "Follow the coordination plan."
    )

    state = WorkflowState()
    print("> Running multi-agent workflow...\n")
    result = await Runner.run(coordinator, prompt, context=state)

    print("=== Final Coordinator Output ===")
    print(result.final_output)

    print("\n=== Captured Workflow State ===")
    print("- Research notes:")
    for note in state.research_notes:
        print(f"  • {note}")

    print("- Action items:")
    for step in state.action_items:
        print(f"  • {step}")

    print("- Risks:")
    for risk in state.risks:
        print(f"  • {risk}")


if __name__ == "__main__":
    asyncio.run(main())
