import logging
import os

from agents import (
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")


def get_openai_client():
    return AsyncOpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )


client = get_openai_client()
set_default_openai_client(client)
set_tracing_disabled(True)

model = OpenAIChatCompletionsModel(
    model="qwen3-coder:30b",
    openai_client=client,
)
