from abc import abstractmethod
from typing import Protocol

from internal import model

class IWewallRepo(Protocol):
    @abstractmethod
    async def get_wewall(self) -> model.Wewall: pass
