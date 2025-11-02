## Agent Workshop · Ollama + OpenAI Agents SDK

Three-stage curriculum for teaching the OpenAI Agents SDK with a locally hosted `qwen:30b` model (Ollama) and a reproducible Docker + Python virtual environment.

### Quickstart

```bash
docker compose up -d
docker compose exec ollama ollama pull qwen:30b   # first run only; downloads the model
docker compose exec workshop bash   # Get into the workshop container

# inside the container
python --version
pip install -r requirements.txt  # optional if you changed dependencies locally
```

Environment defaults:

- `OPENAI_BASE_URL=http://ollama:11434/v1`
- `OPENAI_API_KEY=ollama`

> GPU requirement: the `ollama` container requests an NVIDIA GPU via Docker Compose. Make sure the NVIDIA container toolkit is installed and your GPU is accessible to Docker before starting the stack.

### Repository Layout

- `Dockerfile`, `docker-compose.yml` — reproducible environment with Python + Ollama.
- `stages/stage1` — minimum viable agent using built-in tools.
- `stages/stage2` — custom function tools and a FastMCP curriculum server.
- `stages/stage3` — multi-agent workflows with shared context and handoffs.

Each stage directory contains:

- `README.md` — teaching notes, concepts, and run instructions.
- `demo.py` — runnable example referenced in the guide.
- `activity/` — starter code scaffolds for hands-on practice.

### Running Examples

Use `python` from inside the workshop container:

```bash
python stages/stage1/demo.py
python stages/stage2/demo.py
python stages/stage3/demo.py
```

Activities are inside each stage's `activity/` folder. Follow the TODO markers in the starter scripts.

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
