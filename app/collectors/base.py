from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseCollector(ABC, Generic[T]):
    """External data collector contract.

    Collectors are responsible only for: (1) external request, (2) parsing,
    (3) schema conversion, (4) DB persistence. They MUST NOT invoke the
    LLM / clustering / final-result modules.
    """

    source: str

    @abstractmethod
    def fetch(self, **kwargs) -> list[T]:
        """Fetch + parse + schema-convert. No DB writes."""

    @abstractmethod
    def save(self, items: list[T]) -> int:
        """Persist to DB. Returns count of newly inserted rows."""
