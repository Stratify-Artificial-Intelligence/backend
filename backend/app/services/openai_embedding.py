from typing import Any

from openai import OpenAI

from app.settings import OpenAIEmbeddingSettings

settings = OpenAIEmbeddingSettings()

client = OpenAI(api_key=settings.API_KEY)


def get_embedding(text: str) -> list[float]:
    embedded_response = client.embeddings.create(
        model=settings.MODEL_NAME,
        input=text,
    )
    return embedded_response.data[0].embedding
