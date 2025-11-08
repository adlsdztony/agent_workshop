"""
Stage 1 activity starter.

Goal: build a "workshop analyzer" agent that analyzes the codebase and summarizes each stage with previews of upcoming content.
Run with: python -m stages.stage1.activity.starter_agent --verbose
"""

from __future__ import annotations

import asyncio

from agents import Agent, ModelSettings, Runner

from utils.bash_tool import run_bash_command
from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model


async def run_activity(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    # TODO: rewrite the instructions so the agent understands the reporting goal.
    project_scout = Agent(
        name="Workshop Analyzer",
        instructions=(
            "You are a workshop analyzer agent that examines this agent workshop codebase. "
            "Your task is to:\n"
            "1. Analyze the repository structure and identify all stages\n"
            "2. Read the README files in each stage to understand what each stage covers\n"
            "3. Provide a comprehensive summary of what each stage teaches and accomplishes\n"
            "4. Briefly preview what stages 2 and 3 will cover based on their README files\n"
            "5. Present your findings in a well-structured Markdown format\n\n"
            "Use the bash.run tool to explore the filesystem. Commands you may find useful:\n"
            "- 'ls stages/' to see all available stages\n"
            "- 'cat stages/stageX/README.md' to read stage documentation\n"
            "- 'find stages/ -name \"*.py\" -type f | head -10' to see Python files\n"
            "- 'cat stages/stageX/demo.py' or 'cat stages/stageX/activity/starter_agent.py' to examine code\n\n"
            "Always cite which files/commands you used to gather information."
        ),
        tools=[run_bash_command],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    # TODO: adjust the question to focus the agent on the reporting task you designed.
    result = await Runner.run(
        project_scout,
        "Analyze this workshop codebase and provide a comprehensive summary of what each stage covers, including brief previews of stages 2 and 3 content.",
        hooks=hooks,
    )
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(run_activity(verbose=args.verbose))
