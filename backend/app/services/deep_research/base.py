from abc import ABC, abstractmethod

from app.schemas import ResearchExtended


class DeepResearchProvider(ABC):
    """Base class for deep research providers."""

    @abstractmethod
    def do_deep_research(self, prompt: str, max_tokens: int) -> ResearchExtended:
        """Do deep research."""
        raise NotImplementedError

    @abstractmethod
    def get_deep_research_async(
        self,
        request_id: str,
    ) -> ResearchExtended | None:
        """Get deep research by request ID, if found."""
        raise NotImplementedError

    @abstractmethod
    def do_deep_research_async(
        self,
        prompt: str,
        max_tokens: int,
    ) -> ResearchExtended:
        """Do deep research async."""
        raise NotImplementedError
