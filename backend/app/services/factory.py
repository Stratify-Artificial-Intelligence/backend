from __future__ import annotations

from typing import final

from app.enums import ChatAIModelProviderEnum
from app.services.chat_ai_model import ChatAIModelOpenAI, ChatAIModelProvider
from app.settings import ChatAIModelSettings


class ServicesFactory:
    """Factory class to create service instances."""

    _instance: ServicesFactory | None = None
    _chat_ai_model: ChatAIModelProvider | None = None

    @final
    def __new__(cls) -> ServicesFactory:
        """Overwrite __new__ to make the class a singleton

        Examples
        --------
        >>> services_factory = ServicesFactory()
        >>> services_factory_2 = ServicesFactory()
        >>> services_factory is services_factory_2
        True
        """
        # Note: Overwriting __new__ to make the class a singleton is not the best
        # implementation in Python. The __new__ method can be overwritten in an
        # inheritance context. If such thing happens, this function has to be addressed.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def get_chat_ai_model_provider() -> ChatAIModelProvider:
        settings = ChatAIModelSettings()
        if settings.PROVIDER == ChatAIModelProviderEnum.OPENAI:
            return ChatAIModelOpenAI()
        else:
            raise ValueError(f'Unexpected chat AI model provider: {settings.PROVIDER}')

