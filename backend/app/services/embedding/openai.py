from openai import OpenAI

from app.services.embedding import EmbeddingProvider
from app.settings import OpenAIEmbeddingSettings

settings = OpenAIEmbeddingSettings()


class EmbeddingOpenAI(EmbeddingProvider):
    """OpenAI embedding provider implementation."""

    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.API_KEY)

    def create_embedding(self, text: str) -> list[float]:
        embedded_response = self.client.embeddings.create(
            model=settings.MODEL_NAME,
            input=text,
        )
        return embedded_response.data[0].embedding
