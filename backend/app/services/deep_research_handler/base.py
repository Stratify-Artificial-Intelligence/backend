from abc import ABC, abstractmethod


class DeepResearchHandlerProvider(ABC):
    """Base class for deep research handler providers."""

    @abstractmethod
    def track_and_store_research(self, research_id: str, business_id: int) -> None:
        """Track and store research."""
        raise NotImplementedError
