import requests

from .base import LLMResponse, Provider

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


class OllamaProvider(Provider):
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }
        if system:
            payload["system"] = system

        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

        data = resp.json()
        return LLMResponse(
            text=data.get("response", ""),
            model=data.get("model", self.model),
            stop_reason="stop" if data.get("done") else None,
            usage={
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
        )
