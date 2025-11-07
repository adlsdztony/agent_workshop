"""
Stage 2 activity starter.

Goal: craft a curriculum coach that combines a custom function tool and MCP data.
Run with: python -m stages.stage2.activity.starter_agent
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Literal

from agents import Agent, ModelSettings, Runner, function_tool
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel, Field

from utils.cli import build_verbose_hooks, parse_common_args

REPO_ROOT = Path(__file__).resolve().parents[3]
from utils.ollama_adaptor import model


class LessonPlan(BaseModel):
    stage: Literal["stage1", "stage2", "stage3"]
    topic: str
    learning_goals: list[str]
    hands_on_activity: str
    references: list[str] = Field(
        default_factory=list, description="Links or MCP resources used"
    )


@function_tool(name_override="coach.draft_outline")
def draft_outline(
    stage: Literal["stage1", "stage2", "stage3"],
    theme: str,
    include_activity: bool = True,
) -> LessonPlan:
    """
    Build a basic lesson plan scaffold for a workshop stage.

    Args:
        stage: Which stage the learner wants to review.
        theme: Focus or narrative you want to emphasise (e.g. "tooling", "teamwork").
        include_activity: Whether the plan should include a hands-on task suggestion.
    """
    # TODO: Replace this stub with logic that tailors the plan to the requested stage + theme.
    return LessonPlan(
        stage=stage,
        topic=f"{stage.upper()} refresher on {theme}",
        learning_goals=[
            "Identify the core objective of the stage.",
            "Explain which capabilities the learner gains.",
            "Relate the stage activity to a real project scenario.",
        ],
        hands_on_activity=(
            "Outline the modifications you would make to the stage activity to apply this theme."
            if include_activity
            else "Activity omitted."
        ),
        references=[
            "Use curriculum.fetch_stage_summary via MCP for authoritative details.",
            "Cite the stage activity README for implementation specifics.",
        ],
    )


CURRICULUM_SERVER_PARAMS = MCPServerStdioParams(
    command=sys.executable,
    args=[str(REPO_ROOT / "stages/stage2/mcp_servers/curriculum_server.py")],
    cwd=str(REPO_ROOT),
)


async def main(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    async with MCPServerStdio(
        params=CURRICULUM_SERVER_PARAMS,
        cache_tools_list=True,
        name="Curriculum Server",
    ) as curriculum_server:
        curriculum_coach = Agent(
            name="Curriculum Coach",
            # TODO: Rewrite the instructions so the agent knows it must call both the custom tool
            # and the MCP server before responding. Highlight the JSON output requirement.
            instructions=(
                "Update me! Describe how to use coach.draft_outline and curriculum.fetch_stage_summary "
                "to assemble a JSON lesson plan."
            ),
            tools=[draft_outline],
            mcp_servers=[curriculum_server],
            model=model,
            model_settings=ModelSettings(temperature=0.25),
            output_type=LessonPlan,
        )

        # TODO: Provide a richer user prompt (e.g. include a target audience and learning depth).
        query = "Generate a lesson plan for stage2 using the theme 'collaboration'."

        result = await Runner.run(curriculum_coach, query, hooks=hooks)
        lesson_plan = result.final_output_as(LessonPlan)

        print("\n=== Lesson Plan (JSON) ===")
        print(lesson_plan.model_dump_json(indent=2))


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(main(verbose=args.verbose))
