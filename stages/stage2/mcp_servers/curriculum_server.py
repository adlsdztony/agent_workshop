"""
FastMCP server that exposes structured curriculum knowledge for the workshop.

Run manually (optional) with:
    python stages/stage2/mcp_servers/curriculum_server.py
"""

from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP


STAGE_SUMMARIES = {
    "stage1": {
        "focus": "Minimum viable agent",
        "capabilities": [
            "Configure the Agents SDK",
            "Call built-in tools like the LocalShellTool",
            "Run agents against the local qwen:30b model via Ollama",
        ],
        "activity": "Project scout report that inspects the repository.",
    },
    "stage2": {
        "focus": "Custom tooling and MCP integration",
        "capabilities": [
            "Design custom function tools with structured outputs",
            "Expose domain knowledge through FastMCP",
            "Blend multiple capabilities inside a single agent",
        ],
        "activity": "Curriculum coach that composes lesson plans.",
    },
    "stage3": {
        "focus": "Multi-agent workflows",
        "capabilities": [
            "Coordinate specialised agents via handoffs",
            "Persist context across steps",
            "Chain tool + MCP calls through a workflow controller",
        ],
        "activity": "Delivery of an end-to-end automation workflow.",
    },
}

RESOURCE_TEMPLATE = """# {stage}

**Focus**: {focus}

## Capabilities
{capabilities}

## Activity
- {activity}
"""


mcp = FastMCP(
    "Curriculum Server",
    instructions=(
        "Provides per-stage summaries, capabilities, and activity descriptions for the Agent Workshop."
    ),
)


@mcp.tool()
def fetch_stage_summary(
    stage: Literal["stage1", "stage2", "stage3"],
) -> dict[str, object]:
    """Return the structured summary (focus, capabilities, activity) for the requested stage."""
    summary = STAGE_SUMMARIES.get(stage)
    if summary is None:
        raise ValueError(
            f"Unknown stage '{stage}'. Valid options: stage1, stage2, stage3."
        )
    return {"stage": stage, **summary}


@mcp.resource("curriculum://stage/{stage_name}")
def stage_resource(stage_name: str) -> str:
    """Markdown view of the stage summary."""
    summary = STAGE_SUMMARIES.get(stage_name)
    if summary is None:
        raise ValueError(f"Unknown stage '{stage_name}'.")
    capabilities = "\n".join(f"- {cap}" for cap in summary["capabilities"])
    return RESOURCE_TEMPLATE.format(
        stage=stage_name,
        focus=summary["focus"],
        capabilities=capabilities,
        activity=summary["activity"],
    )


if __name__ == "__main__":
    mcp.run()
