"""
Stage 1 activity starter.

Goal: help the agent implement the `read.file` tool in
`utils/tools/read_file.py` using the provided `bash.run` and `write.file`
helpers.
Run with: python -m stages.stage1.activity.starter_agent --verbose
"""

from __future__ import annotations

import asyncio

from agents import Agent, ModelSettings, Runner

from utils.tools import run_bash_command, write_text_file
from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model

TASK_FILE = "utils/tools/read_file.py"

async def run_activity(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    write_agent = Agent(
        name="Read Tool Coach",
        instructions=(
            # TODO: write the full instructions
            "You need to implement the `read_text_file` function in ..."
        ),
        tools=[
            run_bash_command,
            write_text_file,
        ],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    result = await Runner.run(
        write_agent,
        (
            # TODO: write the full prompt
            f"Implement the `read_text_file` function in {TASK_FILE}."
        ),
        hooks=hooks,
        max_turns=50,
    )
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(run_activity(verbose=args.verbose))
