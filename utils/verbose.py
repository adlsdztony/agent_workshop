from __future__ import annotations

import json
import sys
from textwrap import shorten
from typing import Any, Callable

from agents import Agent
from agents.items import ModelResponse
from openai.types.responses import ResponseOutputMessage
from agents.lifecycle import RunHooksBase
from agents.run_context import RunContextWrapper
from agents.tool import Tool, ToolOutputText


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

    CHANNEL_COLORS = {
        "agent": "\033[36m",  # cyan
        "tool": "\033[33m",  # yellow
        "handoff": "\033[35m",  # magenta
        "llm": "\033[32m",  # green
        "default": "\033[37m",  # white
    }
    RESET_COLOR = "\033[0m"

    def __init__(
        self,
        emit: Callable[[str], None] | None = None,
        use_color: bool | None = None,
    ) -> None:
        self._emit = emit or print
        self._use_color = use_color if use_color is not None else sys.stdout.isatty()

    def _log(self, channel: str, message: str) -> None:
        prefix = f"[verbose][{channel}]"
        if self._use_color:
            color = self.CHANNEL_COLORS.get(channel, self.CHANNEL_COLORS["default"])
            prefix = f"{color}{prefix}{self.RESET_COLOR}"
        self._emit(f"{prefix} {message}")

    def _format_tool_args(self, context: RunContextWrapper[Any]) -> str | None:
        raw_args = getattr(context, "tool_arguments", None)
        if not raw_args:
            return None
        serialized = raw_args
        if isinstance(raw_args, str):
            try:
                parsed = json.loads(raw_args)
                serialized = json.dumps(parsed, ensure_ascii=False)
            except Exception:
                serialized = raw_args
        return _compact(str(serialized))

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
        args_preview = self._format_tool_args(context)
        suffix = f" args={args_preview}" if args_preview else ""
        self._log("tool", f"{_agent_name(agent)} calling {_tool_name(tool)}{suffix}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        tool: Tool,
        result: str | ToolOutputText,
    ) -> None:
        result = result.text if isinstance(result, ToolOutputText) else result
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
        # self._log(
        #     "llm",
        #     f"{_agent_name(agent)} prompting model ({len(input_items)} input item(s), prompt: {prompt_hint})",
        # )

    async def on_llm_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        response: ModelResponse,
    ) -> None:
        if response.output and isinstance(response.output[0], ResponseOutputMessage):
            self._log(
                "llm",
                f"Response content: {response.output[0].content[0].text}",
            )


def build_verbose_hooks(enabled: bool) -> VerboseRunHooks | None:
    """
    Convenience helper that returns VerboseRunHooks when tracing is enabled.
    """

    if not enabled:
        return None
    return VerboseRunHooks()


__all__ = ["VerboseRunHooks", "build_verbose_hooks"]
