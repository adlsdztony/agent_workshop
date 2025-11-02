# Stage 1 · Minimum Viable Agent

Build your first OpenAI Agents SDK project end-to-end. By the end of this stage you will be able to configure a minimal agent, connect it to a pre-defined tool, and execute it against the locally hosted `qwen:30b` Ollama model.

## Learning Goals

- Understand the shape of an `Agent` and the role of the `Runner`.
- Configure the SDK to talk to a self-hosted Ollama endpoint.
- Use the built-in `LocalShellTool` safely by creating a restricted shell executor.
- Run the agent with `uv run` inside the provided Docker environment.

## 1. Environment Check

```bash
# From the repository root
docker compose up -d               # starts the Ollama daemon and workshop shell container
docker compose exec ollama ollama pull qwen:30b   # (first time only, downloads the model)
docker compose exec workshop bash

# Inside the container
uv sync --frozen              # installs dependencies into /workspace/.venv
uv run --python 3.11 --version
uv run python --version
```

The `ollama pull` command is only required the first time (or when you want to update/swap the model); it downloads `qwen:30b` into the shared volume mounted at `/root/.ollama`.

The compose file wires `OPENAI_BASE_URL=http://ollama:11434/v1`, so the Agents SDK automatically talks to the local Ollama runtime. `OPENAI_API_KEY` is set to the placeholder value `ollama` because the Agents SDK expects a key-shaped secret even when targeting a local endpoint.

## 2. Key Concepts

- **Agent** — declarative definition of behaviour (instructions, model, tools, guardrails).
- **Runner** — orchestrates an agent run, resolving tool calls and streaming events.
- **Tools** — capabilities that the model can call. In this stage we stick to a *built-in* tool: `LocalShellTool`.
- **Model Settings** — optional tuning knobs (temperature, max_prompt_tokens, etc).

### LocalShellTool Primer

`LocalShellTool` lets a model run commands on the same machine. To keep learners safe the SDK requires you to provide a `LocalShellExecutor`. You decide which commands are allowed and how to surface the output. Think of it as a whitelist-protected shell.

## 3. Walkthrough Example

Open `stages/stage1/demo.py` — it contains a fully working minimal agent. The important parts are annotated inline. Run it with:

```bash
uv run python stages/stage1/demo.py
```

Expected output (trimmed):

```
> Asking the agent: "List the root level files in this project."

• Agent reasoning, tool use, and final message streaming in the console …
• Final answer that summarises the directory listing
```

If the agent reports that a command is blocked you can adjust the whitelist inside `safe_shell_executor`.

### What to Notice

- The agent is configured with `model="qwen:30b"`. Because the `docker-compose.yml` sets `OPENAI_BASE_URL`, no extra code is needed to target Ollama.
- `Runner.run(...)` returns a `RunResult`. `result.final_output` holds the assistant’s reply as a string.
- The executor implements the safety guardrails: only `pwd`, `ls`, and `cat` are allowed and every command gets a short timeout.

## 4. Activity

File: `stages/stage1/activity/starter_agent.py`

> You are writing a "project scout" agent. It should use the shell tool to inspect the repository and respond with a short report that includes:
>
> 1. The root level directories.
> 2. Whether a `Dockerfile` is present.
> 3. A suggested next command the learner should run.
>
> Extend the starter script so that the agent:
> - Updates its system instructions to reflect the reporting goal.
> - Adjusts the whitelist if it needs additional commands (e.g. `cat Dockerfile`).
> - Formats the final output as a Markdown checklist.

Run your agent with:

```bash
uv run python stages/stage1/activity/starter_agent.py
```

**Stretch ideas**

- Capture the raw tool output (command results) in the agent context and reuse it in the final message.
- Tune `ModelSettings(temperature=0.3)` and observe how output style changes.

Once you are comfortable with the tooling, move to Stage 2 to build custom tools and MCP integrations.
