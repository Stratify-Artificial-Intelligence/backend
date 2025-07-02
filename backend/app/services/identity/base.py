from abc import ABC, abstractmethod


class IdentityProvider(ABC):
    """Base class for identity providers."""

    @staticmethod
    @abstractmethod
    def verify_and_decode_auth_token(token: str) -> str:
        """Return the decoded sub from the provided token."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_user(email: str, password: str) -> str:
        """Create a user and return its external ID."""
        raise NotImplementedError
