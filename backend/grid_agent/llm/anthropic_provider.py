import anthropic

from .base import LLMResponse, Provider

DEFAULT_MODEL = "claude-opus-5"


class AnthropicProvider(Provider):
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        max_tokens = kwargs.pop("max_tokens", 4096)
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
        except anthropic.RateLimitError as e:
            raise RuntimeError(f"Anthropic rate limited: {e}") from e
        except anthropic.APIStatusError as e:
            raise RuntimeError(f"Anthropic API error ({e.status_code}): {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise RuntimeError(f"Anthropic connection error: {e}") from e

        if response.stop_reason == "refusal":
            raise RuntimeError("Anthropic refused the request for safety reasons")

        text = next((b.text for b in response.content if b.type == "text"), "")
        return LLMResponse(
            text=text,
            model=response.model,
            stop_reason=response.stop_reason,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )
