from abc import ABC, abstractmethod

from app.schemas import BusinessResearch


class DeepResearchProvider(ABC):
    """Base class for deep research providers."""

    @staticmethod
    @abstractmethod
    def do_deep_research(prompt: str, max_tokens: int) -> BusinessResearch:
        """Do deep research."""
        raise NotImplementedError
