from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    text: str
    model: str
    stop_reason: str | None = None
    usage: dict = field(default_factory=dict)


class Provider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse: ...
