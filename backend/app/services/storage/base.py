from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Base class for storage providers."""

    @abstractmethod
    async def upload_file(
        self,
        file_binary: BinaryIO,
        file_name: str,
        file_content_type: str,
    ) -> str:
        """Upload a file to storage and return its URL."""
        raise NotImplementedError

    @abstractmethod
    async def remove_file(self, file_name: str) -> None:
        """Remove a file from storage."""
        raise NotImplementedError
