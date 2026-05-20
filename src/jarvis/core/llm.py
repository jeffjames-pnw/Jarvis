from functools import lru_cache

from langchain_anthropic import ChatAnthropic

from jarvis.core.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatAnthropic:
    # ANTHROPIC_API_KEY is read from environment automatically by langchain-anthropic
    return ChatAnthropic(model=settings.model_name)
