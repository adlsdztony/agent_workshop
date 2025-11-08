# Stage 1 · Custom Bash Tool

Stage 0 confirmed the SDK wiring with a mock weather tool. Stage 1 levels up by letting the model run *real* shell commands via a bespoke `@function_tool` that enforces a tight allowlist.

## Learning Goals

- Wrap subprocess calls with `function_tool` and return structured `ToolOutputText`.
- Enforce guardrails (command allowlist, workspace path checks, timeouts, truncation).
- Guide an agent so it calls the tool deliberately and reports what it executed.

## 1. The `bash.run` Tool

Implementation: `utils/bash_tool.py`

- Accepts commands like `ls`, `pwd`, `cat`, `head`, `tail`, `stat`, `wc`, `find`, `grep`.
- Validates that every argument stays under `/workspace`.
- Uses `subprocess.run(..., timeout=5, capture_output=True)` so results are streamed back safely.
- Returns a `ToolOutputText` payload summarising stdout/stderr plus the exit code.

Feel free to extend the allowlist or the output formatting once you are comfortable with the basics.

## 2. Demo Walkthrough

File: `stages/stage1/demo.py`

- Imports `run_bash_command` and exposes it to the agent as the `bash.run` tool.
- Instructions remind the model to cite the commands it used.
- The prompt asks for: root directories, Dockerfile presence, and a suggested next command.

Run it:

```bash
python -m stages.stage1.demo --verbose
# append --verbose to stream the tool calls in real time
```

You should see the agent call `bash.run` a few times before composing the final answer.

## 3. Activity

File: `stages/stage1/activity/starter_agent.py`

Goal: design a "workshop analyzer" agent that:

1. Uses `bash.run` to explore the workshop codebase structure.
2. Reads and analyzes README files across all stages to understand their content.
3. Produces a comprehensive Markdown summary of what each stage teaches.
4. Provides brief previews of stages 2 and 3 content.
5. Cites the files and commands used for information gathering.

The starter already wires `run_bash_command` into the agent. Your tasks:

- Re-write the system instructions so the agent knows to analyze workshop content and structure.
- Expand the allowlist or timeout (in `utils/bash_tool.py`) if your scenario needs extra commands.
- Craft a focused user prompt (the placeholder "Analyze this workshop codebase..." is already provided).

To run your agent:

```bash
python -m stages.stage1.activity.starter_agent --verbose
# append --verbose to stream the tool calls in real time
```

Once this stage feels comfortable, continue to Stage 2 to combine custom tools with a FastMCP server.
