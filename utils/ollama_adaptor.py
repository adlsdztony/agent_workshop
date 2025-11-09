import logging
import os
from collections.abc import Mapping
from functools import wraps
from typing import Any

from agents import (
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


def _ensure_think_disabled(extra_body: Any) -> dict[str, Any]:
    """
    Merge any existing request body overrides with the `think: false` flag required by Ollama.
    """
    if extra_body is None:
        merged: dict[str, Any] = {}
    elif isinstance(extra_body, Mapping):
        merged = dict(extra_body)
    else:
        try:
            merged = dict(extra_body)  # type: ignore[arg-type]
        except Exception:
            logger.warning(
                "Unable to merge extra_body of type %s; only sending think flag.",
                type(extra_body).__name__,
            )
            merged = {}

    merged["think"] = False
    return merged


def _patch_openai_model_for_think_flag() -> None:
    """
    Monkey-patch OpenAIChatCompletionsModel so every call sets think=false.
    """
    patch_attr = "_ollama_think_patch_applied"
    if getattr(OpenAIChatCompletionsModel, patch_attr, False):
        return

    original_fetch = OpenAIChatCompletionsModel._fetch_response

    @wraps(original_fetch)
    async def _fetch_response_with_disabled_think(*args, **kwargs):
        model_settings = kwargs.get("model_settings")
        if model_settings is None and len(args) >= 4:
            model_settings = args[3]

        if model_settings is not None and hasattr(model_settings, "extra_body"):
            model_settings.extra_body = _ensure_think_disabled(
                model_settings.extra_body
            )

        return await original_fetch(*args, **kwargs)

    OpenAIChatCompletionsModel._fetch_response = _fetch_response_with_disabled_think
    setattr(OpenAIChatCompletionsModel, patch_attr, True)


OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")


_patch_openai_model_for_think_flag()


def get_openai_client():
    return AsyncOpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )


client = get_openai_client()
set_default_openai_client(client)
set_tracing_disabled(True)

model = OpenAIChatCompletionsModel(
    model="qwen3:30b",
    openai_client=client,
)
