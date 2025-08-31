from abc import abstractmethod
from typing import Protocol


class IAmocrmClient(Protocol):
    @abstractmethod
    async def create_source(
            self,
            amocrm_source_name: str,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
    ) -> int: pass

    @abstractmethod
    async def connect_channel_to_account(self) -> str: pass

    @abstractmethod
    async def create_contact(
            self,
            contact_name: str,
            first_name: str,
            last_name: str,
            tg_username: str
    ) -> int: pass

    @abstractmethod
    async def create_lead(
            self,
            amocrm_contact_id: int,
            amocrm_pipeline_id: int,
            lead_source: str
    ) -> int: pass

    @abstractmethod
    async def edit_lead(
            self,
            amocrm_lead_id: int,
            amocrm_pipeline_id: int,
            amocrm_pipeline_status_id: int
    ) -> None: pass

    @abstractmethod
    async def update_message_status(
            self,
            message_id: str,
            status: int,
            error_code: int = None,
            error: str = None
    ) -> None: pass

    @abstractmethod
    async def create_chat(
            self,
            amocrm_conversation_id: str,
            amocrm_contact_id: int,
            contact_name: str,
    ) -> str: pass

    @abstractmethod
    async def assign_chat_to_contact(
            self,
            amocrm_chat_id: str,
            amocrm_contact_id: int
    ) -> None: pass

    @abstractmethod
    async def send_message_from_contact(
            self,
            amocrm_contact_id: int,
            amocrm_conversation_id: str,
            amocrm_chat_id: str,
            contact_name: str,
            text: str,
    ) -> str: pass

    @abstractmethod
    async def import_message_from_bot_to_amocrm(
            self,
            amocrm_conversation_id: str,
            amocrm_chat_id: str,
            amocrm_contact_id: int,
            contact_name: str,
            text: str,
    ) -> str: pass

    @abstractmethod
    async def delete_source(self, source_id: int): pass

    @abstractmethod
    async def all_status_by_pipeline_id(self, pipeline_id: int): pass

    @abstractmethod
    async def subscribe_to_event_webhook(self, webhook_url: str, event_name: str): pass