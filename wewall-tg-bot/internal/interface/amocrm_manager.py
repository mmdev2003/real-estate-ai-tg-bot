from abc import abstractmethod
from typing import Protocol

from aiogram.types import Message

from internal import model


class IAmoCrmManagerMessageService(Protocol):
    @abstractmethod
    async def handler(self, message: Message, state: model.State): pass