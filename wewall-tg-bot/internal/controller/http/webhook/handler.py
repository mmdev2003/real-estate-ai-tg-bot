from typing import Annotated

from aiogram import Bot, Dispatcher
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from fastapi import Header
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, common
from .model import *


class TelegramWebhookController(interface.ITelegramWebhookController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            dp: Dispatcher,
            bot: Bot,
            state_service: interface.IStateService,
            post_short_link_service: interface.IPostShortLinkService,
            domain: str,
            prefix: str,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.dp = dp
        self.bot = bot

        self.state_service = state_service
        self.post_short_link_service = post_short_link_service

        self.domain = domain
        self.prefix = prefix

    async def bot_webhook(
            self,
            update: dict,
            x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None
    ):
        with self.tracer.start_as_current_span(
                "TelegramWebhookController.bot_webhook",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if x_telegram_bot_api_secret_token != "secret":
                    return {"status": "error", "message": "Wrong secret token !"}

                telegram_update = Update(**update)
                await self.dp.feed_webhook_update(
                    bot=self.bot,
                    update=telegram_update)

                span.set_status(Status(StatusCode.OK))
                return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def create_post_short_link(self, body: CreatePostShortLinkBody):
        with self.tracer.start_as_current_span(
                "TelegramWebhookController.create_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "post_short_link_id": body.post_short_link_id,
                    "name": body.name,
                    "description": body.description,
                    "image_name": body.image_name,
                    "file_name": body.file_name
                }
        ) as span:
            try:
                await self.post_short_link_service.create_post_short_link(
                    body.post_short_link_id,
                    body.name,
                    body.description,
                    body.image_name,
                    body.image_fid,
                    body.file_name,
                    body.file_fid
                )

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def send_message_to_user(self, body: SendMessageWebhookBody):
        with self.tracer.start_as_current_span(
                "TelegramWebhookController.send_message_to_user",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": body.tg_chat_id,
                    "text": body.text,
                }
        ) as span:
            try:
                state = await self.state_service.state_by_id(body.tg_chat_id)
                state = state[0]

                if state.status != common.StateStatuses.chat_with_amocrm_manager:
                    self.logger.info("Меняем статус на chat_with_amocrm_manager")
                    await self.state_service.change_status(state.id, common.StateStatuses.chat_with_amocrm_manager)

                keyboard = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="Закрыть чат с менеджером")]],
                    resize_keyboard=True
                )
                await self.bot.send_message(body.tg_chat_id, body.text, reply_markup=keyboard)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def delete_state(self, body: DeleteStateBody):
        with self.tracer.start_as_current_span(
                "TelegramWebhookController.delete_state",
                kind=SpanKind.INTERNAL,
                attributes={
                "tg_chat_id": body.tg_chat_id
                }
        ) as span:
            try:
                await self.state_service.delete_state_by_tg_chat_id(body.tg_chat_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise


    async def bot_set_webhook(self):
        with self.tracer.start_as_current_span(
                "TelegramWebhookController.bot_set_webhook",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.bot.set_webhook(
                    f'https://{self.domain}{self.prefix}/update',
                    secret_token='secret',
                    allowed_updates=["message", "callback_query"],
                )
                webhook_info = await self.bot.get_webhook_info()

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

