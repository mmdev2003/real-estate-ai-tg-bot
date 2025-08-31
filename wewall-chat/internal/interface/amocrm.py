from typing import Protocol
from abc import abstractmethod
from fastapi import Request
from internal.controller.http.handler.amocrm.model import *

from internal import model


class IAmocrmChatController(Protocol):
    @abstractmethod
    async def create_chat_with_amocrm_manager_from_tg(self, body: CreateChatWithAmocrmManagerFromTgBody): pass

    @abstractmethod
    async def subscribe_to_event_webhook(self, body: SubscribeToEventWebhookBody): pass

    @abstractmethod
    async def delete_contact(self, request: Request): pass

    @abstractmethod
    async def delete_lead(self, request: Request): pass

    @abstractmethod
    async def edit_lead(self, body: EditLeadBody): pass

    @abstractmethod
    async def connect_channel_to_account(self): pass

    @abstractmethod
    async def send_message_from_tg_to_amocrm(self, body: SendMessageFromTgToAmocrm): pass

    @abstractmethod
    async def send_message_from_bot_to_amocrm(self, body: SendMessageFromTgToAmocrm): pass

    @abstractmethod
    async def send_message_from_amocrm_to_tg(self, body: SendMessageFromAmoCrmToTgBody): pass


class IAmocrmChatService(Protocol):
    # CHAT
    @abstractmethod
    async def create_chat_with_amocrm_manager_from_tg(
            self,
            amocrm_pipeline_id: int,
            tg_chat_id: int,
            tg_username: str,
            first_name: str,
            last_name: str
    ) -> int: pass

    # MESSAGE
    @abstractmethod
    async def send_message_from_tg_to_amocrm(
            self,
            tg_chat_id: int,
            text: str,
    ): pass

    @abstractmethod
    async def import_message_from_bot_to_amocrm(
            self,
            tg_chat_id: int,
            text: str,
    ): pass

    @abstractmethod
    async def send_message_from_amocrm_to_tg(
            self,
            amocrm_chat_id: str,
            amocrm_message_id: str,
            text: str,
    ): pass

    @abstractmethod
    async def edit_lead(
            self,
            tg_chat_id: int,
            amocrm_pipeline_id: int,
            amocrm_pipeline_status_id: int
    ) -> None: pass

    @abstractmethod
    async def connect_channel_to_account(self) -> str: pass

    @abstractmethod
    async def subscribe_to_event_webhook(self, webhook_url: str, event_name: str) -> None: pass

    @abstractmethod
    async def delete_contact(self, amocrm_contact_id: int) -> None: pass

    @abstractmethod
    async def delete_lead(self, amocrm_lead_id: int) -> None: pass


class IAmocrmChatRepo(Protocol):
    # CREATE
    @abstractmethod
    async def create_amocrm_contact(
            self,
            amocrm_contact_id: int,
            contact_name: str,
            tg_chat_id: int
    ): pass

    @abstractmethod
    async def create_amocrm_lead(
            self,
            amocrm_lead_id: int,
            amocrm_contact_id: int,
            amocrm_pipeline_id: int
    ): pass

    @abstractmethod
    async def create_amocrm_chat(
            self,
            amocrm_chat_id: str,
            amocrm_conversation_id: str,
            amocrm_lead_id: int
    ): pass

    @abstractmethod
    async def create_amocrm_message(
            self,
            amocrm_message_id: str,
            amocrm_chat_id: str,
            role: str,
            text: str
    ) -> int: pass

    # GET
    @abstractmethod
    async def contact_by_id(self, amocrm_contact_id: int) -> list[model.AmocrmContact]: pass

    @abstractmethod
    async def contact_by_tg_chat_id(self, tg_chat_id: int) -> list[model.AmocrmContact]: pass

    @abstractmethod
    async def lead_by_id(self, amocrm_lead_id: int) -> list[model.AmocrmLead]: pass

    @abstractmethod
    async def lead_by_amocrm_contact_id(self, amocrm_contact_id: int) -> list[model.AmocrmLead]: pass

    @abstractmethod
    async def chat_by_id(self, amocrm_chat_id: str) -> list[model.AmocrmChat]: pass

    @abstractmethod
    async def chat_by_amocrm_lead_id(self, amocrm_lead_id: int) -> list[model.AmocrmChat]: pass

    # DELETE
    @abstractmethod
    async def delete_amocrm_contact_by_id(self, amocrm_contact_id: int) -> None: pass

    @abstractmethod
    async def delete_amocrm_lead_by_id(self, amocrm_lead_id: int) -> None: pass

    @abstractmethod
    async def delete_amocrm_chat_by_id(self, amocrm_chat_id: str) -> None: pass
