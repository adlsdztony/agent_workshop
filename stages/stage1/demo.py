"""
Stage 1 demo: minimal agent that uses the built-in LocalShellTool to explore the repo.
Run with: python -m stages.stage1.demo
"""

from __future__ import annotations

import asyncio

from agents import Agent, ModelSettings, Runner, function_tool

from utils.ollama_adaptor import model


@function_tool
async def get_weather_tool(city: str):
    """
    Mock tool to get weather information for a city.
    """
    return "Sunny, 25°C"  # Mocked response for demonstration


async def main() -> None:
    explorer = Agent(
        name="Weather Explorer",
        instructions=(
            "You are a helpful agent that provides weather information for cities. "
        ),
        tools=[get_weather_tool],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    question = "What's the weather like in San Francisco today?"

    print("> Asking the agent:", question)
    result = await Runner.run(explorer, question)

    print("\n=== Final Answer ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
