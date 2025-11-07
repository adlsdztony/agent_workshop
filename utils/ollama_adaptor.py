from openai import AsyncOpenAI
from agents import set_default_openai_client, set_tracing_disabled, OpenAIChatCompletionsModel

import os

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")

def get_openai_client():
    return AsyncOpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY
    )

client = get_openai_client()
set_default_openai_client(client)
set_tracing_disabled(True)

model = OpenAIChatCompletionsModel(
    model="qwen3:4b",
    openai_client=client
)
