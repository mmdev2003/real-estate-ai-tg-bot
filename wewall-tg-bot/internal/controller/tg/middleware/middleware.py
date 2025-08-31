import time

from aiogram import Bot
from typing import Callable, Any, Awaitable
from aiogram.types import TelegramObject, Update
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import interface, common, model

class TgMiddleware(interface.ITelegramMiddleware):
    def __init__(
            self,
            tel: interface.ITelemetry,
            bot: Bot,
            state_service: interface.IStateService,
            estate_expert_client: interface.IWewallEstateExpertClient,
            chat_client: interface.IWewallChatClient,
            wewall_expert_inline_keyboard_generator: interface.IWewallExpertInlineKeyboardGenerator,
            wewall_tg_channel_login: str,
            amocrm_main_pipeline_id: int,
            amocrm_pipeline_status_high_engagement: int,
            amocrm_pipeline_status_active_user: int,
    ):
        self.tracer = tel.tracer()
        self.meter = tel.meter()
        self.logger = tel.logger()

        self.bot = bot
        self.state_service = state_service
        self.estate_expert_client = estate_expert_client
        self.chat_client = chat_client
        self.wewall_expert_inline_keyboard_generator = wewall_expert_inline_keyboard_generator
        self.wewall_tg_channel_login = wewall_tg_channel_login
        self.amocrm_main_pipeline_id = amocrm_main_pipeline_id
        self.amocrm_pipeline_status_high_engagement = amocrm_pipeline_status_high_engagement
        self.amocrm_pipeline_status_active_user = amocrm_pipeline_status_active_user

        self.ok_message_counter = self.meter.create_counter(
            name=common.OK_MESSAGE_TOTAL_METRIC,
            description="Total count of 200 messages",
            unit="1"
        )

        self.error_message_counter = self.meter.create_counter(
            name=common.ERROR_MESSAGE_TOTAL_METRIC,
            description="Total count of 500 messages",
            unit="1"
        )

        self.message_duration = self.meter.create_histogram(
            name=common.REQUEST_DURATION_METRIC,
            description="Message duration in seconds",
            unit="s"
        )

        self.active_messages = self.meter.create_up_down_counter(
            name=common.ACTIVE_REQUESTS_METRIC,
            description="Number of active messages",
            unit="1"
        )

    async def trace_middleware01(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ):
        message = event.message if event.message is not None else event.callback_query.message
        event_type = "message" if event.message is not None else "callback_query"
        message_id = message.message_id
        if event_type == "message":
            user_username = message.from_user.username
        else:
            user_username = event.callback_query.from_user.username
        tg_chat_id = message.chat.id
        if message.text is not None:
            message_text = message.text
        else:
            message_text = "Изображение"
        callback_query_data = event.callback_query.data if event.callback_query is not None else ""

        with self.tracer.start_as_current_span(
                "TgMiddleware.trace_middleware01",
                kind=SpanKind.INTERNAL,
                attributes={
                    common.TELEGRAM_EVENT_TYPE_KEY: event_type,
                    common.TELEGRAM_CHAT_ID_KEY: tg_chat_id,
                    common.TELEGRAM_USER_USERNAME_KEY: user_username,
                    common.TELEGRAM_USER_MESSAGE_KEY: message_text,
                    common.TELEGRAM_MESSAGE_ID_KEY: message_id,
                    common.TELEGRAM_CALLBACK_QUERY_DATA_KEY: callback_query_data,
                }
        ) as root_span:
            span_ctx = root_span.get_span_context()
            trace_id = format(span_ctx.trace_id, '032x')
            span_id = format(span_ctx.span_id, '016x')

            data["trace_id"] = trace_id
            data["span_id"] = span_id
            try:
                await handler(event, data)

                root_span.set_status(Status(StatusCode.OK))
            except TelegramBadRequest:
                pass
            except Exception as error:
                await message.answer("Непредвиденная ошибка на сервере")
                root_span.record_exception(error)
                root_span.set_status(Status(StatusCode.ERROR, str(error)))

    async def metric_middleware02(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ):
        with self.tracer.start_as_current_span(
                "TgMiddleware.metric_middleware02",
                kind=SpanKind.INTERNAL
        ) as span:
            start_time = time.time()
            self.active_messages.add(1)

            message = event.message if event.message is not None else event.callback_query.message
            event_type = "message" if event.message is not None else "callback_query"
            message_id = message.message_id
            if event_type == "message":
                user_username = message.from_user.username
            else:
                user_username = event.callback_query.from_user.username
            tg_chat_id = message.chat.id
            if message.text is not None:
                message_text = message.text
            else:
                message_text = "Изображение"
            callback_query_data = event.callback_query.data if event.callback_query is not None else ""
            trace_id = data["trace_id"]
            span_id = data["span_id"]

            request_attrs: dict = {
                common.TELEGRAM_EVENT_TYPE_KEY: event_type,
                common.TELEGRAM_CHAT_ID_KEY: tg_chat_id,
                common.TELEGRAM_USER_USERNAME_KEY: user_username,
                common.TELEGRAM_USER_MESSAGE_KEY: message_text,
                common.TELEGRAM_MESSAGE_ID_KEY: message_id,
                common.TELEGRAM_CALLBACK_QUERY_DATA_KEY: callback_query_data,
                common.TRACE_ID_KEY: trace_id,
                common.SPAN_ID_KEY: span_id,
            }

            try:
                await handler(event, data)

                duration_seconds = time.time() - start_time

                request_attrs[common.HTTP_REQUEST_DURATION_KEY] = duration_seconds

                self.ok_message_counter.add(1, attributes=request_attrs)
                self.message_duration.record(duration_seconds, attributes=request_attrs)
                span.set_status(Status(StatusCode.OK))
            except TelegramBadRequest:
                pass
            except Exception as err:
                duration_seconds = time.time() - start_time
                request_attrs[common.TELEGRAM_MESSAGE_DURATION_KEY] = 500
                request_attrs[common.ERROR_KEY] = str(err)

                self.error_message_counter.add(1, attributes=request_attrs)
                self.message_duration.record(duration_seconds, attributes=request_attrs)

                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
            finally:
                self.active_messages.add(-1)

    async def logger_middleware03(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ):
        with self.tracer.start_as_current_span(
                "TgMiddleware.logger_middleware03",
                kind=SpanKind.INTERNAL
        ) as span:
            start_time = time.time()

            message = event.message if event.message is not None else event.callback_query.message
            event_type = "message" if event.message is not None else "callback_query"
            message_id = message.message_id
            if event_type == "message":
                user_username = message.from_user.username
            else:
                user_username = event.callback_query.from_user.username
            tg_chat_id = message.chat.id
            if message.text is not None:
                message_text = message.text
            else:
                message_text = "Изображение"
            callback_query_data = event.callback_query.data if event.callback_query is not None else ""
            trace_id = data["trace_id"]
            span_id = data["span_id"]

            extra_log: dict = {
                common.TELEGRAM_EVENT_TYPE_KEY: event_type,
                common.TELEGRAM_CHAT_ID_KEY: tg_chat_id,
                common.TELEGRAM_USER_USERNAME_KEY: user_username,
                common.TELEGRAM_USER_MESSAGE_KEY: message_text,
                common.TELEGRAM_MESSAGE_ID_KEY: message_id,
                common.TELEGRAM_CALLBACK_QUERY_DATA_KEY: callback_query_data,
                common.TRACE_ID_KEY: trace_id,
                common.SPAN_ID_KEY: span_id,
            }
            try:
                if event_type == "message":
                    self.logger.info("Начали обработку telegram message", extra_log)
                if event_type == "callback_query":
                    self.logger.info("Начали обработку telegram callback", extra_log)

                del data["trace_id"], data["span_id"]
                await handler(event, data)

                extra_log = {
                    **extra_log,
                    common.TELEGRAM_MESSAGE_DURATION_KEY: int((time.time() - start_time) * 1000),
                }
                if event_type == "message":
                    self.logger.info("Завершили обработку telegram message", extra_log)
                elif event_type == "callback_query":
                    self.logger.info("Завершили обработку telegram callback", extra_log)

                span.set_status(Status(StatusCode.OK))
            except TelegramBadRequest:
                pass
            except Exception as err:
                extra_log = {
                    **extra_log,
                    common.TELEGRAM_MESSAGE_DURATION_KEY: int((time.time() - start_time) * 1000),
                }
                if event_type == "message":
                    self.logger.error(f"Ошибка обработки telegram message: {str(err)}", extra_log)
                elif event_type == "callback_query":
                    self.logger.error(f"Ошибка обработки telegram callback: {str(err)}", extra_log)
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def check_subscribe_middleware04(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ):
        with self.tracer.start_as_current_span(
                "TgMiddleware.check_subscribe_middleware04",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                message = event.message if event.message is not None else event.callback_query.message
                tg_chat_id = message.chat.id
                subscribe = await self.__check_wewall_channel_subscribe(tg_chat_id)
                if not subscribe:
                    self.logger.info("Пользователь не подписан на тг канал")

                    if event.callback_query is not None:
                        await event.callback_query.answer()

                    keyboard = await self.wewall_expert_inline_keyboard_generator.check_subscribe()
                    await message.answer(common.not_subscribe_text, reply_markup=keyboard)
                else:
                    if event.callback_query is not None and event.callback_query.data == common.WewallExpertKeyboardCallbackData.check_subscribe:
                        self.logger.info("Пользователь подписался на тг канал")

                        tg_chat_id = message.chat.id
                        await self.state_service.delete_state_by_tg_chat_id(tg_chat_id)
                        state_id = await self.state_service.create_state(tg_chat_id)

                        username = event.callback_query.from_user.username if event.callback_query.from_user.username is not None else ""
                        first_name = event.callback_query.from_user.first_name if event.callback_query.from_user.first_name is not None else ""
                        last_name = event.callback_query.from_user.last_name if event.callback_query.from_user.last_name is not None else ""
                        await self.chat_client.create_chat_with_amocrm_manager(
                            self.amocrm_main_pipeline_id,
                            message.chat.id,
                            username,
                            first_name,
                            last_name,
                        )

                        llm_response = await self.estate_expert_client.send_message_to_wewall_expert(
                            tg_chat_id,
                            "Расскажи мне про WEWALL"
                        )
                        await self.state_service.change_status(state_id, common.StateStatuses.wewall_expert)

                        keyboard = await self.wewall_expert_inline_keyboard_generator.start()
                        await event.callback_query.message.answer(llm_response, reply_markup=keyboard)
                        await event.callback_query.answer()
                    else:
                        await handler(event, data)
                span.set_status(Status(StatusCode.OK))
            except TelegramForbiddenError:
                self.logger.warning("Пользователь заблокировал бота")
                return

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def __check_wewall_channel_subscribe(self, tg_user_id: int) -> bool:
        user_channel_status = await self.bot.get_chat_member(chat_id=self.wewall_tg_channel_login, user_id=tg_user_id)

        if user_channel_status.status != 'left':
            return True
        else:
            return False

    async def get_state_middleware05(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ):
        with self.tracer.start_as_current_span(
                "TgMiddleware.get_state_middleware05",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                message = event.message if event.message is not None else event.callback_query.message
                event_type = "message" if event.message is not None else "callback_query"
                if event_type == "message":
                    username = message.from_user.username if message.from_user.username is not None else ""
                    first_name = message.from_user.first_name if message.from_user.first_name is not None else ""
                    last_name = message.from_user.last_name if message.from_user.last_name is not None else ""
                else:
                    username = event.callback_query.from_user.username if event.callback_query.from_user.username is not None else ""
                    first_name = event.callback_query.from_user.first_name if event.callback_query.from_user.first_name is not None else ""
                    last_name = event.callback_query.from_user.last_name if event.callback_query.from_user.last_name is not None else ""


                tg_chat_id = message.chat.id

                state = await self.state_service.state_by_id(tg_chat_id)
                if not state:
                    await self.state_service.create_state(tg_chat_id)
                    state = await self.state_service.state_by_id(tg_chat_id)
                    await self.state_service.change_status(state[0].id, common.StateStatuses.wewall_expert)
                    state[0].status = common.StateStatuses.wewall_expert

                    await self.chat_client.create_chat_with_amocrm_manager(
                        self.amocrm_main_pipeline_id,
                        message.chat.id,
                        username,
                        first_name,
                        last_name,
                    )

                state = state[0]
                data["user_state"] = state
                await handler(event, data)

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def count_message_middleware06(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ):
        with self.tracer.start_as_current_span(
                "TgMiddleware.count_message_middleware06",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                state: model.State = data["user_state"]

                if event.message is not None:
                    if not state.is_transferred_to_manager:
                        if state.count_message == 20 - 1:
                            self.logger.info("Счетчик сообщений сигнализирует о 'Высокой вовлеченности'")
                            await self.chat_client.edit_lead(event.message.chat.id, self.amocrm_main_pipeline_id,
                                                             self.amocrm_pipeline_status_high_engagement)
                        elif state.count_message == 60 - 1:
                            self.logger.info("Счетчик сообщений сигнализирует о 'Активном пользователе'")
                            await self.chat_client.edit_lead(event.message.chat.id, self.amocrm_main_pipeline_id,
                                                             self.amocrm_pipeline_status_active_user)
                        await self.state_service.increment_message_count(state.id)
                        self.logger.debug("Инкрементировали счетчик сообщений")

                await handler(event, data)
                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_contact_message_to_amocrm_middleware07(
             self,
             handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
             event: Update,
             data: dict[str, Any]
    ):
        with self.tracer.start_as_current_span(
                "TgMiddleware.send_contact_message_to_amocrm_middleware07",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if event.message is not None:
                    await self.chat_client.send_message_to_amocrm(event.message.chat.id, event.message.text)
                await handler(event, data)
                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err