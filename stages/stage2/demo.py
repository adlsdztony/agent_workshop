"""
Stage 2 demo: custom FunctionTool + local MCP server.
Run with: python -m stages.stage2.demo
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from agents import (
    Agent,
    ModelSettings,
    Runner,
    ToolOutputText,
    function_tool,
)
from agents.mcp import MCPServerStdio, MCPServerStdioParams

from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model

WORKSPACE_ROOT = Path("/workspace").resolve()
REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve_relative_path(relative_path: str) -> Path:
    candidate = (WORKSPACE_ROOT / relative_path).resolve()
    if not str(candidate).startswith(str(WORKSPACE_ROOT)):
        msg = f"Path escape blocked for '{relative_path}'. Keep files inside {WORKSPACE_ROOT}."
        raise ValueError(msg)
    return candidate


@function_tool(name_override="repo.find_todos")
def find_repo_todos(relative_path: str, limit: int = 5) -> ToolOutputText:
    """
    Return up to `limit` lines that contain TODO or FIXME in the target file.

    Args:
        relative_path: File path relative to the repository root.
        limit: Maximum number of matches to include.
    """
    try:
        file_path = _resolve_relative_path(relative_path)
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    if not file_path.exists() or not file_path.is_file():
        return ToolOutputText(text=f"No file found at {relative_path}")

    matches: list[str] = []
    with file_path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, start=1):
            if "TODO" in line or "FIXME" in line:
                matches.append(f"L{idx}: {line.strip()}")
            if len(matches) >= limit:
                break

    if not matches:
        return ToolOutputText(text=f"No TODO/FIXME markers in {relative_path}")

    bullet_list = "\n".join(f"- {item}" for item in matches)
    return ToolOutputText(text=f"TODO markers in {relative_path}:\n{bullet_list}")


CURRICULUM_SERVER_PARAMS = MCPServerStdioParams(
    command="python",
    args=[str(REPO_ROOT / "stages/stage2/mcp_servers/curriculum_server.py")],
    cwd=str(REPO_ROOT),
)


async def run_demo(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    async with MCPServerStdio(
        params=CURRICULUM_SERVER_PARAMS,
        cache_tools_list=True,
        name="Curriculum Server",
    ) as curriculum_server:
        mentor = Agent(
            name="Curriculum Mentor",
            instructions=(
                "You support workshop learners. Combine the repo TODO summary with curriculum facts "
                "from the MCP server. Always cite which tool you used for each fact."
            ),
            tools=[find_repo_todos],
            mcp_servers=[curriculum_server],
            model=model,
            model_settings=ModelSettings(temperature=0.1),
        )

        prompt = (
            "Prepare a short update for the instructor:\n"
            "1. Summarise outstanding TODO markers in stages/stage1/activity/starter_agent.py\n"
            "2. Explain how Stage 2 builds on Stage 1 using the curriculum MCP data\n"
            "3. Suggest the next improvement task for the learner"
        )

        print("> Running Curriculum Mentor...\n")
        result = await Runner.run(mentor, prompt, hooks=hooks)

        print("\n=== Final Answer ===")
        print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(run_demo(verbose=args.verbose))
