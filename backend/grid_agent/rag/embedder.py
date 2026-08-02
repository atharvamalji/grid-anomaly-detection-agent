import os

import openai

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


class Embedder:
    def __init__(self, model: str = DEFAULT_EMBEDDING_MODEL, api_key: str | None = None):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. OpenAI's embeddings endpoint accepts up to
        2048 inputs per request; batch here to stay well under that."""
        if not texts:
            return []

        batch_size = 500
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(model=self.model, input=batch)
            except openai.APIStatusError as e:
                raise RuntimeError(f"OpenAI embeddings error ({e.status_code}): {e.message}") from e
            except openai.APIConnectionError as e:
                raise RuntimeError(f"OpenAI embeddings connection error: {e}") from e
            vectors.extend(item.embedding for item in response.data)
        return vectors
