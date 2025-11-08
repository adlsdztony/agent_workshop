# Stage 0 · Orientation

Stage 0 is a quick orientation so learners can confirm the workshop environment, run their first agent, and see the OpenAI Agents SDK in action before touching any tools.

## Learning Goals

- Understand the minimum `Agent` + `Runner` wiring.
- Verify the local Ollama-backed model is reachable from the container.
- Practice running modules with `python -m` (plus the shared `--verbose` flag).

## Run the Demo

The demo lives in `stages/stage0/demo.py` and simply answers a weather question using a mocked tool.

```bash
python -m stages.stage0.demo --verbose
# add --verbose to stream lifecycle events
```

Expected output (trimmed):

```
> Asking the agent: What's the weather like in San Francisco today?
=== Final Answer ===
Sunny, 25°C
```

If this works you are ready to dive into Stage 1, where you will build a safe bash tool that actually inspects the repository.
