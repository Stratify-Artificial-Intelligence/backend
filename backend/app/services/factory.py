from __future__ import annotations

from typing import final

from app.enums import ChatAIModelProviderEnum, IdentityProviderEnum, StorageProviderEnum
from app.services.chat_ai_model import ChatAIModelOpenAI, ChatAIModelProvider
from app.services.identity import IdentityFirebaseAuth, IdentityProvider
from app.services.storage import StorageAWSS3, StorageProvider
from app.settings import ServicesSettings


settings = ServicesSettings()


class ServicesFactory:
    """Factory class to create service instances."""

    _instance: ServicesFactory | None = None
    _chat_ai_model_provider: ChatAIModelProvider | None = None
    _identity_provider: IdentityProvider | None = None
    _storage_provider: StorageProvider | None = None

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

    def get_chat_ai_model_provider(self) -> ChatAIModelProvider:
        if self._chat_ai_model_provider is None:
            if settings.CHAT_AI_MODEL_PROVIDER == ChatAIModelProviderEnum.OPENAI:
                self._chat_ai_model_provider = ChatAIModelOpenAI()
            else:
                raise ValueError(
                    f'Unexpected chat AI model provider: '
                    f'{settings.CHAT_AI_MODEL_PROVIDER}'
                )
        return self._chat_ai_model_provider

    def get_identity_provider(self) -> IdentityProvider:
        if self._identity_provider is None:
            if settings.IDENTITY_PROVIDER == IdentityProviderEnum.FIREBASE_AUTH:
                self._identity_provider = IdentityFirebaseAuth()
            else:
                raise ValueError(
                    f'Unexpected identity provider: {settings.IDENTITY_PROVIDER}'
                )
        return self._identity_provider

    def get_storage_provider(self) -> StorageProvider:
        if self._storage_provider is None:
            if settings.STORAGE_PROVIDER == StorageProviderEnum.AWS_S3:
                self._storage_provider = StorageAWSS3()
            else:
                raise ValueError(
                    f'Unexpected storage provider: {settings.STORAGE_PROVIDER}'
                )
        return self._storage_provider
