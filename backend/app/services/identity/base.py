from abc import ABC, abstractmethod

from app.schemas import TokenData


class IdentityProvider(ABC):
    """Base class for identity providers."""

    @staticmethod
    @abstractmethod
    def verify_and_decode_auth_token(token: str) -> TokenData:
        """Return the decoded sub from the provided token."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_user(email: str, password: str) -> str:
        """Create a user and return its external ID."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def generate_impersonation_token(original_sub: str, impersonated_sub: str) -> str:
        """Generate an impersonation token."""
        raise NotImplementedError
