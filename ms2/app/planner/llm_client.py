"""OpenAI ChatOpenAI singleton for the AI planner.

Tries gpt-4.1 first; falls back to gpt-4o if the model is unavailable.
All planner nodes must obtain the LLM instance via get_llm().
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.config.logger import get_logger

load_dotenv()
logger = get_logger("ms2.planner.llm_client")

_PRIMARY_MODEL = "gpt-4.1"
_FALLBACK_MODEL = "gpt-4o"

_llm_instance: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    """Return the shared ChatOpenAI instance, creating it once on first call."""
    global _llm_instance
    if _llm_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "Set it in ms2/.env to use the AI planner."
            )
        # Try primary model; the actual availability is checked at call time.
        _llm_instance = ChatOpenAI(
            model=_PRIMARY_MODEL,
            api_key=api_key,
            temperature=0.2,
            max_tokens=4096,
        )
        logger.info("LLM client initialised | model=%s", _PRIMARY_MODEL)
    return _llm_instance


def get_fallback_llm() -> ChatOpenAI:
    """Return a fallback ChatOpenAI instance using gpt-4o."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    return ChatOpenAI(
        model=_FALLBACK_MODEL,
        api_key=api_key,
        temperature=0.2,
        max_tokens=4096,
    )
