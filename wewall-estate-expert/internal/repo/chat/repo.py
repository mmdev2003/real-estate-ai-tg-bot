from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model
from .query import *


class ChatRepository(interface.IChatRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_chat(self, tg_chat_id) -> int:
        with self.tracer.start_as_current_span(
                "ChatRepository.create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                args = {"tg_chat_id": tg_chat_id}
                chat_id = await self.db.insert(create_chat, args)

                span.set_status(Status(StatusCode.OK))
                return chat_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_message(self, chat_id: int, text: str, role: str) -> int:
        with self.tracer.start_as_current_span(
                "ChatRepository.create_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "text": text,
                    "role": role
                }
        ) as span:
            try:
                args = {"chat_id": chat_id, "text": text, "role": role}
                message_id = await self.db.insert(create_message, args)

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def chat_by_tg_chat_id(self, tg_chat_id: int) -> list[model.Chat]:
        with self.tracer.start_as_current_span(
                "ChatRepository.chat_by_tg_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                args = {"tg_chat_id": tg_chat_id}
                rows = await self.db.select(chat_by_tg_chat_id, args)

                if rows:
                    rows = model.Chat.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def message_by_chat_id(self, chat_id: int) -> list[model.Message]:
        with self.tracer.start_as_current_span(
                "ChatRepository.message_by_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                }
        ) as span:
            try:
                args = {"chat_id": chat_id}
                rows = await self.db.select(message_by_chat_id, args)
                if rows:
                    rows = model.Message.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_all_message(self, chat_id: int) -> None:
        with self.tracer.start_as_current_span(
                "ChatRepository.delete_all_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                }
        ) as span:
            try:
                args = {"chat_id": chat_id}
                await self.db.delete(delete_all_message, args)
                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err