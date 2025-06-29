from abc import ABC, abstractmethod


class ChatAIModelProvider(ABC):
    """Base class for chat AI model providers."""

    @staticmethod
    @abstractmethod
    async def create_chat() -> str:
        """Create a chat and return its internal ID."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def add_message_to_chat(
        chat_internal_id: str,
        content: str,
        instructions_prompt: str | None = None,
    ) -> str:
        """Add a message to a thread and return run id."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def add_message_to_chat_and_get_response(
        chat_internal_id: str,
        content: str,
        context: str,
        instructions_prompt: str | None = None,
    ) -> str:
        """Add a message to a chat and return the response of the AI model."""
        raise NotImplementedError
