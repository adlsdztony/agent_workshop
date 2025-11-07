"""
Stage 3 activity starter.

Objective: orchestrate a deployment workflow with multiple specialised agents.
Run with: python -m stages.stage3.activity.starter_workflow
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from agents import (
    Agent,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolOutputText,
    function_tool,
)
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel

WORKSPACE_ROOT = Path("/workspace").resolve()
REPO_ROOT = Path(__file__).resolve().parents[3]
from utils.ollama_adaptor import model


@dataclass
class DeploymentState:
    preflight_logs: list[str] = field(default_factory=list)
    deployment_steps: list[str] = field(default_factory=list)
    validation_plan: list[str] = field(default_factory=list)


class DeploymentWorkflow(BaseModel):
    preflight_checks: list[str]
    deployment_steps: list[str]
    validation_plan: list[str]


@function_tool(name_override="workflow.store_steps")
def store_steps(
    ctx: RunContextWrapper[DeploymentState],
    steps: list[str],
    category: Literal["deployment", "validation"] = "deployment",
) -> ToolOutputText:
    """
    Persist steps in the shared context.

    TODO: Update this helper to capture more metadata or craft richer feedback for the agents.
    """
    if category == "deployment":
        ctx.context.deployment_steps = steps
    else:
        ctx.context.validation_plan = steps
    return ToolOutputText(text=f"Stored {len(steps)} steps under {category}.")


CURRICULUM_SERVER_PARAMS = MCPServerStdioParams(
    command=sys.executable,
    args=[str(REPO_ROOT / "stages/stage2/mcp_servers/curriculum_server.py")],
    cwd=str(REPO_ROOT),
)

async def main() -> None:

    state = DeploymentState()
    async with MCPServerStdio(
        params=CURRICULUM_SERVER_PARAMS,
        cache_tools_list=True,
        name="Curriculum Server",
    ) as curriculum_server:
        # TODO: Refine instructions, tools, and output handling for each specialised agent.
        preflight_agent = Agent(
            name="Preflight Agent",
            handoff_description="Validates configuration before deployment.",
            instructions="Rewrite me with detailed preflight guidance.",
            tools=[],
            mcp_servers=[curriculum_server],
            model=model,
            model_settings=ModelSettings(temperature=0.2),
        )

        execution_agent = Agent(
            name="Execution Agent",
            handoff_description="Drafts deployment steps.",
            instructions="Rewrite me to produce a deployment checklist and call workflow.store_steps.",
            tools=[store_steps],
            model=model,
            model_settings=ModelSettings(temperature=0.25),
        )

        validation_agent = Agent(
            name="Validation Agent",
            handoff_description="Defines validation criteria and rollback triggers.",
            instructions="Rewrite me to define validation/rollback and call workflow.store_steps(category='validation').",
            tools=[store_steps],
            model=model,
            model_settings=ModelSettings(temperature=0.15),
        )

        coordinator = Agent(
            name="Deployment Coordinator",
            instructions=(
                "TODO: Describe how to call the preflight, execution, and validation agents. "
                "Conclude with a JSON DeploymentWorkflow object."
            ),
            handoffs=[preflight_agent, execution_agent, validation_agent],
            model=model,
            model_settings=ModelSettings(temperature=0.05),
            output_type=DeploymentWorkflow,
        )

        request = (
            "Prepare a deployment workflow for the agent workshop sample project. "
            "Highlight risks tied to the custom MCP server."
        )

        result = await Runner.run(coordinator, request, context=state)
        workflow = result.final_output_as(DeploymentWorkflow)

        print("\n=== Deployment Workflow ===")
        print(workflow.model_dump_json(indent=2))

        print("\n=== Shared State Snapshot ===")
        print(f"Preflight logs: {state.preflight_logs}")
        print(f"Deployment steps: {state.deployment_steps}")
        print(f"Validation plan: {state.validation_plan}")


if __name__ == "__main__":
    asyncio.run(main())
