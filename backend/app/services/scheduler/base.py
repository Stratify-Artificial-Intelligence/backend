from abc import ABC, abstractmethod


class SchedulerProvider(ABC):
    """Base class for scheduler providers."""

    @abstractmethod
    async def create_schedule(
        self,
        name: str,
        group_name: str,
        expression: str,
        body: dict,
    ) -> None:
        """Create a schedule."""
        raise NotImplementedError

    @abstractmethod
    async def delete_schedule(
        self,
        name: str,
        group_name: str,
    ) -> None:
        """Delete a schedule."""
        raise NotImplementedError
