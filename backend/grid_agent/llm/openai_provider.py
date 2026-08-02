import openai

from .base import LLMResponse, Provider

DEFAULT_MODEL = "gpt-4o"


class OpenAIProvider(Provider):
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )
        except openai.RateLimitError as e:
            raise RuntimeError(f"OpenAI rate limited: {e}") from e
        except openai.APIStatusError as e:
            raise RuntimeError(f"OpenAI API error ({e.status_code}): {e.message}") from e
        except openai.APIConnectionError as e:
            raise RuntimeError(f"OpenAI connection error: {e}") from e

        choice = response.choices[0]
        return LLMResponse(
            text=choice.message.content or "",
            model=response.model,
            stop_reason=choice.finish_reason,
            usage={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        )
