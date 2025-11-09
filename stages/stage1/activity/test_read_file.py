"""
Stage 1 activity spec and agent-driven smoke test.

Implement ``utils/tools/read_file.py::read_text_file`` so it:

1. Resolves the target path with ``resolve_workspace_path``.
2. Returns numbered lines, either for the whole file or for a validated
   ``start_line``/``end_line`` range.
3. Truncates long outputs using the ``max_output_chars`` budget.
4. Surfaces empty-file and missing-file situations with helpful messages.

Run ``python -m stages.stage1.activity.test_read_file --verbose`` to launch a small
agent that exercises the tool against ``sample_notes.txt`` and a missing-file
case. The agent mirrors the structure used in the demos/activities, so you can
see real tool calls in the verbose stream.
"""

from __future__ import annotations

import asyncio
from typing import Iterable, Sequence

from agents import Agent, ModelSettings, Runner

from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model
from utils.tools import read_text_file

SAMPLE_FILE = "stages/stage1/activity/sample_notes.txt"
SCENARIOS: Sequence[tuple[str, dict[str, object]]] = (
    ("Full file", {"path": SAMPLE_FILE}),
    ("Line range 2-3", {"path": SAMPLE_FILE, "start_line": 2, "end_line": 3}),
    ("Over-long output demo", {"path": SAMPLE_FILE, "max_output_chars": 40}),
    (
        "Missing file",
        {"path": "stages/stage1/activity/does_not_exist.txt"},
    ),
)


def _format_scenarios_for_prompt(scenarios: Iterable[tuple[str, dict[str, object]]]) -> str:
    """Produce a numbered description of scenario arguments."""

    formatted: list[str] = []
    for idx, (label, kwargs) in enumerate(scenarios, start=1):
        arg_bits = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        formatted.append(f"{idx}. {label}: call read.file with {arg_bits}.")
    return "\n".join(formatted)


async def preview_read_tool(verbose: bool = False) -> None:
    """Spin up an agent that runs the read.file tool for each scenario."""

    hooks = build_verbose_hooks(verbose)
    tester = Agent(
        name="Read Tool Previewer",
        instructions=(
            "You validate the read.file tool for workshop students.\n"
            "For each scenario the user listed:\n"
            "  * Print a heading like `--- Label ---`.\n"
            "  * Call the read.file tool exactly once with the provided arguments.\n"
            "  * Paste the tool output verbatim so learners can eyeball it.\n"
            "After all scenarios, remind the user how to rerun this script."
        ),
        tools=[read_text_file],
        model=model,
        model_settings=ModelSettings(temperature=0),
    )

    prompt = (
        "Demonstrate the read.file tool using these scenarios:\n"
        f"{_format_scenarios_for_prompt(SCENARIOS)}\n"
        "Follow the workflow in your system instructions."
    )

    result = await Runner.run(tester, prompt, hooks=hooks)
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(preview_read_tool(verbose=args.verbose))
