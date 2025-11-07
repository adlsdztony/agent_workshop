from __future__ import annotations

from textwrap import shorten
from typing import Any, Callable

from agents import Agent
from agents.items import ModelResponse
from agents.lifecycle import RunHooksBase
from agents.run_context import RunContextWrapper
from agents.tool import Tool


def _agent_name(agent: Agent[Any]) -> str:
    return getattr(agent, "name", agent.__class__.__name__)


def _tool_name(tool: Tool) -> str:
    return getattr(tool, "name", tool.__class__.__name__)


def _compact(text: str, width: int = 96) -> str:
    return shorten(text, width=width, placeholder="…")


class VerboseRunHooks(RunHooksBase[Any, Agent[Any]]):
    """
    Lightweight tracing hooks that print key lifecycle events while an agent runs.
    """

    def __init__(self, emit: Callable[[str], None] | None = None) -> None:
        self._emit = emit or print

    def _log(self, channel: str, message: str) -> None:
        self._emit(f"[verbose][{channel}] {message}")

    async def on_agent_start(
        self, context: RunContextWrapper[Any], agent: Agent[Any]
    ) -> None:
        self._log("agent", f"Starting {_agent_name(agent)}")

    async def on_agent_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        output: Any,
    ) -> None:
        preview = _compact(str(output)) if output is not None else ""
        suffix = f": {preview}" if preview else ""
        self._log("agent", f"Finished {_agent_name(agent)}{suffix}")

    async def on_handoff(
        self,
        context: RunContextWrapper[Any],
        from_agent: Agent[Any],
        to_agent: Agent[Any],
    ) -> None:
        self._log("handoff", f"{_agent_name(from_agent)} → {_agent_name(to_agent)}")

    async def on_tool_start(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        tool: Tool,
    ) -> None:
        self._log("tool", f"{_agent_name(agent)} calling {_tool_name(tool)}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        tool: Tool,
        result: str,
    ) -> None:
        preview = _compact(result) if result else ""
        suffix = f": {preview}" if preview else ""
        self._log("tool", f"{_agent_name(agent)} completed {_tool_name(tool)}{suffix}")

    async def on_llm_start(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        system_prompt: str | None,
        input_items: list[Any],
    ) -> None:
        prompt_hint = (
            _compact(system_prompt.strip())
            if system_prompt
            else "default system prompt"
        )
        self._log(
            "llm",
            f"{_agent_name(agent)} prompting model ({len(input_items)} input item(s), prompt: {prompt_hint})",
        )

    async def on_llm_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        response: ModelResponse,
    ) -> None:
        response_id = response.response_id or "n/a"
        usage = getattr(response, "usage", None)
        tokens = getattr(usage, "total_tokens", None) if usage else None
        usage_hint = f", tokens={tokens}" if tokens is not None else ""
        self._log(
            "llm",
            f"{_agent_name(agent)} received response_id={response_id}{usage_hint}",
        )


def build_verbose_hooks(enabled: bool) -> VerboseRunHooks | None:
    """
    Convenience helper that returns VerboseRunHooks when tracing is enabled.
    """

    if not enabled:
        return None
    return VerboseRunHooks()


__all__ = ["VerboseRunHooks", "build_verbose_hooks"]
