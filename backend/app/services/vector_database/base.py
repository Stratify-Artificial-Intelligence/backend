from abc import ABC, abstractmethod


class VectorDatabaseProvider(ABC):
    """Base class for vector database providers."""

    @abstractmethod
    def search_vectors(
        self,
        index_name: str,
        namespace: str,
        query_vector: list[float],
        top_k: int,
    ) -> list[str]:
        """Search for vectors in a vector database."""
        raise NotImplementedError

    @abstractmethod
    def upload_vectors(
        self,
        index_name: str,
        namespace: str,
        vectors: list[tuple[str, list[float], dict[str, str]]],
    ) -> None:
        """Upload vectors to a vector database."""
        raise NotImplementedError

    @abstractmethod
    def delete_vectors(
        self,
        index_name: str,
        namespace: str,
    ) -> None:
        """Delete all vectors of a namespace in an index of a vector database."""
        raise NotImplementedError
