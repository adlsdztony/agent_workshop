## Agent Workshop · Ollama + OpenAI Agents SDK

Three-stage curriculum for teaching the OpenAI Agents SDK with a locally hosted `qwen:30b` model (Ollama) and a reproducible Docker + uv environment.

### Quickstart

```bash
docker compose up -d
docker compose exec ollama ollama pull qwen:30b   # first run only; downloads the model
docker compose exec workshop bash   # Get into the workshop container

# inside the container
uv sync --frozen
uv run python --version
```

Environment defaults:

- `OPENAI_BASE_URL=http://ollama:11434/v1`
- `OPENAI_API_KEY=ollama`
- `UV_PROJECT_ENVIRONMENT=/workspace/.venv`

### Repository Layout

- `Dockerfile`, `docker-compose.yml` — reproducible environment with uv + Ollama.
- `stages/stage1` — minimum viable agent using built-in tools.
- `stages/stage2` — custom function tools and a FastMCP curriculum server.
- `stages/stage3` — multi-agent workflows with shared context and handoffs.

Each stage directory contains:

- `README.md` — teaching notes, concepts, and run instructions.
- `demo.py` — runnable example referenced in the guide.
- `activity/` — starter code scaffolds for hands-on practice.

### Running Examples

Use `uv run` from inside the workshop container:

```bash
uv run python stages/stage1/demo.py
uv run python stages/stage2/demo.py
uv run python stages/stage3/demo.py
```

Activities are inside each stage's `activity/` folder. Follow the TODO markers in the starter scripts.

### Updating Dependencies

Add packages with:

```bash
uv add <package>
uv lock
```

Then `uv sync --frozen` inside the container or rebuild the Docker image.

### References

- OpenAI Agents SDK quickstart: <https://openai.github.io/openai-agents-python/quickstart/>
- MCP Python SDK: <https://github.com/modelcontextprotocol/python-sdk>
- Ollama: <https://ollama.com>

Happy building!
