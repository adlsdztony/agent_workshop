# Stage 2 · Custom Tools & MCP

Time to augment the base agent with bespoke capabilities. You will create a structured `FunctionTool`, wire in a local MCP (Model Context Protocol) server, and expose both to the agent runtime.

## Learning Goals

- Design custom tools using `@function_tool` and strict docstrings.
- Build a lightweight MCP server with `FastMCP` and connect via stdio.
- Combine multiple capabilities within a single agent run.
- Observe tool call traces with verbose logging.

## 1. Prerequisites

Carry over the Docker environment from Stage 1:

```bash
docker compose up -d
docker compose exec ollama ollama pull qwen:30b   # ensure the model exists (first time only)
docker compose exec workshop bash
```

### Helpful environment flags

- `OPENAI_BASE_URL=http://ollama:11434/v1`
- `OPENAI_API_KEY=ollama`

You can enable verbose tool tracing while experimenting:

```bash
export AGENTS_LOG_LEVEL=DEBUG
```

## 2. Custom Function Tools

Key imports:

- `from agents import function_tool, ToolOutputText`
- `@function_tool()` decorator automatically derives JSON schemas from type hints and docstrings.
- Return values can be plain Python primitives or `ToolOutputText`/`ToolOutputFileContent` for richer payloads.

### Example Walkthrough

Open `stages/stage2/demo.py`. It defines:

1. `@function_tool()` decorated `find_repo_todos` helper that scans for TODO/FIXME comments while ensuring paths stay in `/workspace`.
2. An MCP server (`curriculum_server.py`) that surfaces structured curriculum knowledge.
3. An agent that combines both capabilities to answer a higher-level question.

Run it as a module from the repo root:

```bash
python -m stages.stage2.demo
```

You should see streaming traces similar to:

```
> Running Curriculum Mentor...
• Tool call: repo.find_todos
• MCP call: curriculum.fetch_stage_summary
• Final answer combining both tool results
```

Review the code to notice:

- The docstring of `find_repo_todos` doubles as the tool description.
- Paths are validated before accessing the filesystem.
- `MCPServerStdio` automatically spawns the server script with the active Python interpreter.
- `agent.mcp_servers=[curriculum_server]` exposes all MCP tools under the `curriculum.` namespace.

## 3. Building the MCP Server

File: `stages/stage2/mcp_servers/curriculum_server.py`

- Uses `FastMCP("Curriculum Server", instructions=...)`.
- Exposes a `curriculum.fetch_stage_summary` tool plus a contextual resource.
- The `if __name__ == "__main__": mcp.run()` block enables stdio transport by default.
- When `demo.py` runs, the SDK forks this script and handles the lifecycle automatically.

Feel free to extend the server with more resources (e.g. `@mcp.resource("curriculum://stage/{name}")`) to share richer context.

## 4. Activity

File: `stages/stage2/activity/starter_agent.py`

> Build a “curriculum coach” agent that:
>
> 1. Uses a custom tool to assemble a mini-lesson outline (topic, learning goals, hands-on task).
> 2. Pulls supporting facts from the MCP curriculum server.
> 3. Returns a JSON-formatted plan (hint: set `output_type` to a `pydantic` model).
>
> The starter script already defines the `LessonPlan` schema and a `draft_outline` function decorated with `@function_tool()`. Your tasks are to:
>
> - Complete the implementation of `draft_outline`.
> - Craft system instructions that tell the agent how to juggle both the tool and the MCP data.
> - Pick an appropriate prompt that causes a single run to produce a coherent lesson plan.

Run the activity the same way:

```bash
python -m stages.stage2.activity.starter_agent
```

**Stretch ideas**

- Add a tool guardrail that blocks lesson requests longer than N minutes.
- Modify the MCP server to return example code snippets per stage.
- Experiment with `ToolOutputText` vs returning plain Python objects.

Once you can orchestrate custom tools and MCP data, move on to Stage 3 to coordinate entire multi-agent workflows.
