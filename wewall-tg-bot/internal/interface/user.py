from abc import abstractmethod
from typing import Protocol

from internal import model

class IUserService(Protocol):
    @abstractmethod
    async def track_user(self, tg_chat_id: int, source_type: str) -> None: pass

    @abstractmethod
    async def all_user(self) -> list[model.User]: pass

    @abstractmethod
    async def update_is_bot_blocked(self, user_id: int, is_bot_blocked: bool = True) -> None: pass

class IUserRepo(Protocol):
    @abstractmethod
    async def create_user(self, tg_chat_id: int, source_type: str) -> int: pass

    @abstractmethod
    async def user_by_tg_chat_id(self, tg_chat_id: int) -> list[model.User]: pass

    @abstractmethod
    async def update_is_bot_blocked(self, user_id: int, is_bot_blocked: bool) -> None: pass

    @abstractmethod
    async def all_user(self) -> list[model.User]: pass
