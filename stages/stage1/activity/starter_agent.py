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

from utils.tools import run_bash_command, read_text_file, write_text_file
from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model

TASK_FILE = "utils/tools/read_file.py"

async def run_activity(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    write_agent = Agent(
        name="Read Tool Coach",
        instructions=(
            "You finish coding chores inside this repository.\n"
            f"Focus file: `{TASK_FILE}`. Implement the read.file tool described in that\n"
            "module so future stages can inspect files safely.\n\n"
            "Workflow:\n"
            "1. Use `bash.run` commands like `sed -n '1,160p'` to inspect the current\n"
            "   file since `read.file` is not ready yet.\n"
            "2. Outline your plan before editing so the reviewer understands your\n"
            "   approach.\n"
            "3. Call `write.file` with `start_line`/`end_line` to perform targeted\n"
            "   replacements inside the file.\n"
            "4. Once the implementation is in place you may call `read.file` to double\n"
            "   check the result.\n"
            "5. In your final response, summarize what you changed, cite any commands\n"
            "   you executed, and mention how to run the smoke test in\n"
            "   `stages/stage1/activity/test_read_file.py`."
        ),
        tools=[
            run_bash_command,
            read_text_file,
            write_text_file,
        ],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    result = await Runner.run(
        write_agent,
        (
            "Implement `read_text_file` in {TASK_FILE} so that the read.file function\n"
            "returns numbered lines, supports optional line ranges, respects\n"
            "resolve_workspace_path, and trims long outputs. Once you are satisfied,\n"
            "explain how it matches the requirements and how to verify it by running\n"
            "`python -m stages.stage1.activity.test_read_file`."
        ),
        hooks=hooks,
        max_turns=50,
    )
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(run_activity(verbose=args.verbose))
