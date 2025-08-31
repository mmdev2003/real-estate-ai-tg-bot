from fastapi import status, Request
from fastapi.responses import JSONResponse
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from .model import *


class ChatController(interface.IChatController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            chat_service: interface.IChatService
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.chat_service = chat_service

    async def send_message_to_wewall_expert_by_tg(self, body: SendMessageToLLMtByTgBody):
        with self.tracer.start_as_current_span(
                "ChatController.send_message_to_wewall_expert_by_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                llm_response = await self.chat_service.send_message_wewall_expert(chat.id, body.text)
                response = SendMessageToLLMByTgResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_expert_by_tg(self, body: SendMessageToLLMtByTgBody):
        with self.tracer.start_as_current_span(
                "ChatController.send_message_to_estate_expert_by_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                llm_response = await self.chat_service.send_message_estate_expert(chat.id, body.text)
                response = SendMessageToLLMByTgResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_search_expert_by_tg(self, body: SendMessageToLLMtByTgBody):
        with self.tracer.start_as_current_span(
                "ChatController.send_message_to_estate_search_expert_by_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                llm_response = await self.chat_service.send_message_estate_search_expert(chat.id, body.text)
                response = SendMessageToLLMByTgResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_calculator_by_tg(self, body: SendMessageToLLMtByTgBody):
        with self.tracer.start_as_current_span(
                "ChatController.send_message_to_estate_calculator_by_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                llm_response = await self.chat_service.send_message_estate_claculator_expert(chat.id, body.text)
                response = SendMessageToLLMByTgResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_contact_collector_by_tg(self, body: SendMessageToLLMtByTgBody):
        with self.tracer.start_as_current_span(
                "ChatController.send_message_to_contact_collector_by_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                llm_response = await self.chat_service.send_message_contact_collector(chat.id, body.text)
                response = SendMessageToLLMByTgResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def add_message_from_llm(self, body: AddMessageToChat):
        with self.tracer.start_as_current_span(
                "ChatController.add_message_from_llm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text,
                    "role": body.role
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                await self.chat_service.create_message(chat.id, body.text, body.role)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "successful"},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chat_summary(self, body: GetChatSummaryBody):
        with self.tracer.start_as_current_span(
                "ChatController.get_chat_summary",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id
                }
        ) as span:
            try:
                chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                if not chat:
                    self.logger.info("Создаем новый чат")
                    await self.chat_service.create_chat(body.tg_chat_id)
                    chat = await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id)
                chat = chat[0]

                chat_summary = await self.chat_service.get_chat_summary(chat.id)
                response = GetChatSummaryResponse(chat_summary=chat_summary)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_all_message(self, body: DeleteAllMessageBody):
        with self.tracer.start_as_current_span(
                "ChatController.delete_all_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id
                }
        ) as span:
            try:
                chat = (await self.chat_service.chat_by_tg_chat_id(body.tg_chat_id))
                if not chat:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"message": "All messages deleted"},
                    )
                chat = chat[0]
                await self.chat_service.delete_all_message(chat.id)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "All messages deleted"},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
