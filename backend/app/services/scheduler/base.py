from abc import ABC, abstractmethod


class SchedulerProvider(ABC):
    """Base class for scheduler providers."""

    @abstractmethod
    async def create_schedule(
        self,
        name: str,
        expression: str,
        target_endpoint: str,
        body: str,
    ) -> None:
        """Create a schedule."""
        raise NotImplementedError
