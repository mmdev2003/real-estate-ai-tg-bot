from abc import abstractmethod
from typing import Protocol

from internal import model

class INewsService(Protocol):
    @abstractmethod
    async def create_news(self, news_name: str, news_summary: str) -> int: pass

    @abstractmethod
    async def all_news(self) -> list[model.News]: pass

class INewsRepo(Protocol):
    @abstractmethod
    async def all_news(self) -> list[model.News]: pass

    @abstractmethod
    async def create_news(self, news_name: str, news_summary: str) -> int: pass

