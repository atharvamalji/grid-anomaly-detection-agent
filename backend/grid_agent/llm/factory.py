import os

from . import anthropic_provider, ollama_provider, openai_provider
from .base import Provider


def get_provider(name: str | None = None) -> Provider:
    name = name or os.environ.get("LLM_PROVIDER", "anthropic")

    if name == "anthropic":
        return anthropic_provider.AnthropicProvider(
            model=os.environ.get("ANTHROPIC_MODEL", anthropic_provider.DEFAULT_MODEL)
        )
    if name == "openai":
        return openai_provider.OpenAIProvider(
            model=os.environ.get("OPENAI_MODEL", openai_provider.DEFAULT_MODEL)
        )
    if name == "ollama":
        return ollama_provider.OllamaProvider(
            model=os.environ.get("OLLAMA_MODEL", ollama_provider.DEFAULT_MODEL),
            base_url=os.environ.get("OLLAMA_BASE_URL", ollama_provider.DEFAULT_BASE_URL),
        )

    raise ValueError(f"Unknown LLM provider '{name}'. Choose from: anthropic, openai, ollama")
