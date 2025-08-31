from aiogram.types import Message
from abc import abstractmethod
from typing import Protocol

from internal import model

class IEstateExpertMessageService(Protocol):
    @abstractmethod
    async def handler(self, message: Message, state: model.State): pass