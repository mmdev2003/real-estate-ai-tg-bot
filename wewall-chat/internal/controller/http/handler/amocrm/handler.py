from fastapi.responses import JSONResponse
from fastapi import status, Request

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from .model import *


class AmocrmChatController(interface.IAmocrmChatController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_chat_service: interface.IAmocrmChatService
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.amocrm_chat_service = amocrm_chat_service

    async def create_chat_with_amocrm_manager_from_tg(self, body: CreateChatWithAmocrmManagerFromTgBody):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.create_chat_with_amocrm_manager_from_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "tg_username": body.tg_username,
                    "first_name": body.first_name,
                    "last_name": body.last_name,
                }
        ) as span:
            try:
                await self.amocrm_chat_service.create_chat_with_amocrm_manager_from_tg(
                    body.amocrm_pipeline_id,
                    body.tg_chat_id,
                    body.tg_username,
                    body.first_name,
                    body.last_name,
                )

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "Tg chat created"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def edit_lead(self, body: EditLeadBody):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.edit_lead",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "amocrm_pipeline_status_id": body.amocrm_pipeline_id,
                    "amocrm_pipeline_id": body.amocrm_pipeline_id
                }
        ) as span:
            try:
                await self.amocrm_chat_service.edit_lead(
                    body.tg_chat_id,
                    body.amocrm_pipeline_id,
                    body.amocrm_pipeline_status_id
                )

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def subscribe_to_event_webhook(self, body: SubscribeToEventWebhookBody):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.subscribe_to_event_webhook",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                await self.amocrm_chat_service.subscribe_to_event_webhook(body.webhook_url, body.event_name)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_contact(self, request: Request):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.delete_contact",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                data = await request.form()

                amocrm_contact_id = int(data.get("contacts[delete][0][id]"))
                await self.amocrm_chat_service.delete_contact(amocrm_contact_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_lead(self, request: Request):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.delete_lead",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                data = await request.form()

                amocrm_lead_id = int(data.get("leads[delete][0][id]"))
                await self.amocrm_chat_service.delete_lead(amocrm_lead_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def connect_channel_to_account(self):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.connect_channel_to_account",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                resp = await self.amocrm_chat_service.connect_channel_to_account()

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"scope_id: ": resp}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_message_from_tg_to_amocrm(self, body: SendMessageFromTgToAmocrm):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.send_message_from_tg_to_amocrm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text,
                }
        ) as span:
            try:
                await self.amocrm_chat_service.send_message_from_tg_to_amocrm(
                    body.tg_chat_id,
                    body.text,
                )

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "Message send"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_message_from_bot_to_amocrm(self, body: SendMessageFromTgToAmocrm):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.send_message_from_bot_to_amocrm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text,
                }
        ) as span:
            try:
                await self.amocrm_chat_service.import_message_from_bot_to_amocrm(
                    body.tg_chat_id,
                    body.text,
                )

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "Message send"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_message_from_amocrm_to_tg(self, body: SendMessageFromAmoCrmToTgBody):
        with self.tracer.start_as_current_span(
                "AmocrmChatController.send_message_from_amocrm_to_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "text": body.message.message["text"],
                    "amocrm_message_id": body.message.message["id"],
                    "amocrm_chat_id": body.message.conversation["id"]
                }
        ) as span:
            try:
                amocrm_message_id = body.message.message["id"]
                amocrm_chat_id = body.message.conversation["id"]
                text = body.message.message["text"]

                await self.amocrm_chat_service.send_message_from_amocrm_to_tg(
                    amocrm_chat_id,
                    amocrm_message_id,
                    text
                )

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "Message added"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
