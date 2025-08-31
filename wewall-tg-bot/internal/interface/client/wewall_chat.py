from abc import abstractmethod
from typing import Protocol

class IWewallChatClient(Protocol):
    @abstractmethod
    async def create_chat_with_amocrm_manager(
            self,
            amocrm_pipeline_id: int,
            tg_chat_id: int,
            tg_username: str,
            first_name: str,
            last_name: str,
    ): pass

    @abstractmethod
    async def send_message_to_amocrm(self, tg_chat_id: int, text: str): pass

    @abstractmethod
    async def import_message_to_amocrm(self, tg_chat_id: int, text: str): pass

    @abstractmethod
    async def edit_lead(self, tg_chat_id: int, amocrm_pipeline_id: int, amocrm_pipeline_status_id: int): pass