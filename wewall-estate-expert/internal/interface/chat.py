from abc import abstractmethod
from typing import Protocol

from internal.controller.http.handler.chat.model import *
from internal import model


class IChatController(Protocol):
    @abstractmethod
    async def send_message_to_wewall_expert_by_tg(self, body: SendMessageToLLMtByTgBody): pass

    @abstractmethod
    async def send_message_to_estate_expert_by_tg(self, body: SendMessageToLLMtByTgBody): pass

    @abstractmethod
    async def send_message_to_estate_search_expert_by_tg(self, body: SendMessageToLLMtByTgBody): pass

    @abstractmethod
    async def send_message_to_estate_calculator_by_tg(self, body: SendMessageToLLMtByTgBody): pass

    @abstractmethod
    async def send_message_to_contact_collector_by_tg(self, body: SendMessageToLLMtByTgBody): pass

    @abstractmethod
    async def add_message_from_llm(self, body: AddMessageToChat): pass

    @abstractmethod
    async def get_chat_summary(self, body: GetChatSummaryBody): pass

    @abstractmethod
    async def delete_all_message(self, body: DeleteAllMessageBody): pass


class IChatService(Protocol):
    @abstractmethod
    async def create_chat(self, tg_chat_id: int) -> int: pass

    @abstractmethod
    async def create_message(self, tg_chat_id: int, text: str, role: str) -> int: pass

    @abstractmethod
    async def chat_by_tg_chat_id(self, tg_chat_id: int) -> list[model.Chat]: pass

    @abstractmethod
    async def send_message_wewall_expert(self, chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_estate_expert(self, chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_estate_search_expert(self, chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_estate_claculator_expert(self, chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_contact_collector(self, chat_id: int, text: str) -> str: pass

    @abstractmethod
    async def get_chat_summary(self, chat_id: int) -> str: pass

    @abstractmethod
    async def delete_all_message(self, chat_id: int) -> None: pass


class IChatRepo(Protocol):

    @abstractmethod
    async def create_chat(self, tg_chat_id: int) -> int: pass

    @abstractmethod
    async def create_message(self, chat_id: int, text: str, role: str) -> int: pass

    @abstractmethod
    async def chat_by_tg_chat_id(self, tg_chat_id: int) -> list[model.Chat]: pass

    @abstractmethod
    async def message_by_chat_id(self, chat_id: int) -> list[model.Message]: pass

    @abstractmethod
    async def delete_all_message(self, chat_id: int) -> None: pass
