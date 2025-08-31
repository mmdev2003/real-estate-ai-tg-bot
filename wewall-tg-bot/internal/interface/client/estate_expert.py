from abc import abstractmethod
from typing import Protocol

class IWewallEstateExpertClient(Protocol):

    @abstractmethod
    async def send_message_to_wewall_expert(self, tg_chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_estate_expert(self, tg_chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_estate_search_expert(self, tg_chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_estate_analysis_expert(self, tg_chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_estate_finance_model_expert(self, tg_chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_contact_collector(self, tg_chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def add_message_to_chat(self, tg_chat_id: int, text: str, role: str): pass

    @abstractmethod
    async def summary(self, tg_chat_id: int) -> str: pass

    @abstractmethod
    async def delete_all_message(self, tg_chat_id: int) -> None: pass
