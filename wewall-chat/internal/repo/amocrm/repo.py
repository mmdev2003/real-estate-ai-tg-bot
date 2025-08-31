from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface
from .query import *


class AmocrmChatRepo(interface.IAmocrmChatRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    # CREATE
    async def create_amocrm_contact(
            self,
            amocrm_contact_id: int,
            contact_name: str,
            tg_chat_id: int,
    ):
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.create_amocrm_contact",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                    "contact_name": contact_name,
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                args = {
                    "amocrm_contact_id": amocrm_contact_id,
                    "name": contact_name,
                    "tg_chat_id": tg_chat_id
                }
                await self.db.insert(create_contact, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def create_amocrm_lead(self, amocrm_lead_id: int, amocrm_contact_id: int, amocrm_pipeline_id: int):
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.create_amocrm_lead",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_lead_id": amocrm_lead_id,
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                }
        ) as span:
            try:
                args = {
                    "amocrm_lead_id": amocrm_lead_id,
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                }

                await self.db.insert(create_amocrm_lead, args)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def create_amocrm_chat(self, amocrm_chat_id: str, amocrm_conversation_id: str, amocrm_lead_id: int):
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.create_amocrm_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_lead_id": amocrm_lead_id
                }
        ) as span:
            try:
                args = {
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_lead_id": amocrm_lead_id
                }
                await self.db.insert(create_amocrm_chat, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def create_amocrm_message(self, amocrm_message_id: str, amocrm_chat_id: str, role: str, text: str) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.create_amocrm_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_message_id": amocrm_message_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "role": role,
                    "text": text
                }
        ) as span:
            try:
                args = {
                    "amocrm_message_id": amocrm_message_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "role": role,
                    "text": text
                }
                message_id = await self.db.insert(create_amocrm_message, args)

                span.set_status(StatusCode.OK)
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    # GET
    async def contact_by_tg_chat_id(self, tg_chat_id: int) -> list[model.AmocrmContact]:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.contact_by_tg_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                args = {"tg_chat_id": tg_chat_id}
                rows = await self.db.select(contact_by_tg_chat_id, args)
                if rows:
                    rows = model.AmocrmContact.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def contact_by_id(self, amocrm_contact_id: int) -> list[model.AmocrmContact]:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.contact_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                }
        ) as span:
            try:
                args = {"amocrm_contact_id": amocrm_contact_id}
                rows = await self.db.select(contact_by_id, args)
                if rows:
                    rows = model.AmocrmContact.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def lead_by_id(self, amocrm_lead_id: int) -> list[model.AmocrmLead]:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.lead_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_lead_id": amocrm_lead_id,
                }
        ) as span:
            try:
                args = {"amocrm_lead_id": amocrm_lead_id}
                rows = await self.db.select(lead_by_id, args)
                if rows:
                    rows = model.AmocrmLead.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def lead_by_amocrm_contact_id(self, amocrm_contact_id: int) -> list[model.AmocrmLead]:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.lead_by_amocrm_contact_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                }
        ) as span:
            try:
                args = {"amocrm_contact_id": amocrm_contact_id}
                rows = await self.db.select(lead_by_amocrm_contact_id, args)
                if rows:
                    rows = model.AmocrmLead.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def chat_by_id(self, amocrm_chat_id: str) -> list[model.AmocrmChat]:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.chat_by_amocrm_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_chat_id": amocrm_chat_id,
                }
        ) as span:
            try:
                args = {"amocrm_chat_id": amocrm_chat_id}
                rows = await self.db.select(chat_by_id, args)
                if rows:
                    rows = model.AmocrmChat.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def chat_by_amocrm_lead_id(self, amocrm_lead_id: int) -> list[model.AmocrmChat]:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.chat_by_amocrm_lead_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_lead_id": amocrm_lead_id,
                }
        ) as span:
            try:
                args = {"amocrm_lead_id": amocrm_lead_id}
                rows = await self.db.select(chat_by_amocrm_lead_id, args)
                if rows:
                    rows = model.AmocrmChat.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    # DELETE
    async def delete_amocrm_contact_by_id(self, amocrm_contact_id: int) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.delete_contact_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                }
        ) as span:
            try:
                args = {"amocrm_contact_id": amocrm_contact_id}
                await self.db.delete(delete_amocrm_contact_by_id, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def delete_amocrm_lead_by_id(self, amocrm_lead_id: int) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.delete_amocrm_lead_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_lead_id": amocrm_lead_id,
                }
        ) as span:
            try:
                args = {"amocrm_lead_id": amocrm_lead_id}
                await self.db.delete(delete_amocrm_lead_by_id, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def delete_amocrm_chat_by_id(self, amocrm_chat_id: str) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatRepo.delete_amocrm_chat_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_chat_id": amocrm_chat_id,
                }
        ) as span:
            try:
                args = {"amocrm_chat_id": amocrm_chat_id}
                await self.db.delete(delete_amocrm_chat_by_id, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise
