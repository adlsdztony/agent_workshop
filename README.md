## Agent Workshop · Ollama + OpenAI Agents SDK

Four-stage curriculum (Stage 0–3) for teaching the OpenAI Agents SDK with a locally hosted `qwen3-coder:30b` model (Ollama) and a reproducible Docker + Python virtual environment.

### Quickstart

```bash
docker compose up -d
docker compose exec ollama ollama pull qwen3-coder:30b   # first run only; downloads the model
docker compose exec workshop bash   # Get into the workshop container
```

### Repository Layout

- `Dockerfile`, `docker-compose.yml` — reproducible environment with Python + Ollama.
- `stages/stage0` — orientation demo that proves the SDK wiring.
- `stages/stage1` — custom bash function tool for repository exploration.
- `stages/stage2` — custom function tools blended with a FastMCP curriculum server.
- `stages/stage3` — multi-agent workflows with shared context and handoffs.

Each stage directory contains:

- `README.md` — teaching notes, concepts, and run instructions.
- `demo.py` — runnable example referenced in the guide.
- `activity/` — starter code scaffolds for hands-on practice.

> Stage 0 ships only with a README and demo; later stages introduce activities.
### Running Examples

Use `python -m` from inside the workshop container so the repository root stays on `sys.path`:

```bash
python -m stages.stage0.demo
python -m stages.stage1.demo
python -m stages.stage2.demo
python -m stages.stage3.demo
```

Append `--verbose` to any demo/activity command (e.g. `python -m stages.stage1.demo --verbose`) to stream agent lifecycle events, including tool calls and handoffs. Activities are inside each stage's `activity/` folder (`python -m stages.stageX.activity.<script>`). Follow the TODO markers in the starter scripts.

### Updating Dependencies

Add packages with `pip` inside the workshop container:

```bash
pip install "<package>"
pip freeze > requirements.txt
```

Commit the updated `requirements.txt` so collaborators (or rebuilt containers) get the new dependencies.

### References

- OpenAI Agents SDK quickstart: <https://openai.github.io/openai-agents-python/quickstart/>
- MCP Python SDK: <https://github.com/modelcontextprotocol/python-sdk>
- Ollama: <https://ollama.com>

Happy building!
