from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def create_embedding(self, text: str) -> list[float]:
        """Create an embedding for the given text."""
        raise NotImplementedError
