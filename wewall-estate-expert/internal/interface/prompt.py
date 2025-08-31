from abc import abstractmethod
from typing import Protocol


class IPromptService(Protocol):
    @abstractmethod
    async def wewall_expert_system_prompt(self) -> str: pass

    @abstractmethod
    async def estate_expert_system_prompt(self) -> str: pass

    @abstractmethod
    async def estate_search_expert_prompt(self) -> str: pass

    @abstractmethod
    async def estate_calculator_expert_prompt(self) -> str: pass

    @abstractmethod
    async def contact_collector_prompt(self) -> str: pass

