"""
Stage 1 activity starter.

Goal: build a "project scout" agent that reports on repository structure.
Run with: python -m stages.stage1.activity.starter_agent
"""

from __future__ import annotations

import asyncio

from agents import (
    Agent,
    ModelSettings,
    Runner,
)

from utils.ollama_adaptor import model


async def run_activity() -> None:
    # TODO: rewrite the instructions so the agent understands the reporting goal.
    project_scout = Agent(
        name="Project Scout",
        instructions=(
            "Replace this text with system guidance that asks for a Markdown checklist "
            "covering: root directories, Dockerfile presence, and a recommended next command."
        ),
        tools=[],  # TODO: Add tools if needed for your designed flow.
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    # TODO: adjust the question to focus the agent on the reporting task you designed.
    result = await Runner.run(project_scout, "Draft the initial project scout report.")
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(run_activity())
