from aiogram.types import Message, BotCommand
from aiogram import Dispatcher, Bot
from openai import images
from opentelemetry.trace import SpanKind, StatusCode

from internal import model, interface, common


class CommandController(interface.ICommandController):

    def __init__(
            self,
            tel: interface.ITelemetry,
            dp: Dispatcher,
            bot: Bot,
            state_service: interface.IStateService,
            user_service: interface.IUserService,
            post_short_link_service: interface.IPostShortLinkService,
            estate_expert_client: interface.IWewallEstateExpertClient,
            wewall_expert_message_service: interface.IWewallExpertMessageService,
            estate_search_message_service: interface.IEstateSearchMessageService,
            estate_finance_model_message_service: interface.IEstateFinanceModelMessageService,
            estate_expert_message_service: interface.IEstateExpertMessageService,
            chat_client: interface.IWewallChatClient,
            amocrm_manager_message_service: interface.IAmoCrmManagerMessageService,
            amocrm_appeal_pipeline_id: int,
            amocrm_pipeline_status_chat_with_manager: int
    ):
        self.logger = tel.logger()
        self.tracer = tel.tracer()
        self.dp = dp
        self.bot = bot
        self.state_service = state_service
        self.user_service = user_service
        self.post_short_link_service = post_short_link_service
        self.estate_expert_client = estate_expert_client
        self.wewall_expert_message_service = wewall_expert_message_service
        self.estate_search_message_service = estate_search_message_service
        self.estate_finance_model_message_service = estate_finance_model_message_service
        self.estate_expert_message_service = estate_expert_message_service
        self.chat_client = chat_client
        self.amocrm_manager_message_service = amocrm_manager_message_service
        self.amocrm_appeal_pipeline_id = amocrm_appeal_pipeline_id
        self.amocrm_pipeline_status_chat_with_manager = amocrm_pipeline_status_chat_with_manager

    async def start_handler(self, message: Message):
        with self.tracer.start_as_current_span(
                "CommandController.start_handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                args = message.text.split()
                tg_chat_id = message.chat.id

                if len(args) > 1:
                    self.logger.info(f"Переход по короткой ссылке")
                    span.set_attribute("short_link_args", args)
                    post_short_link_id = int(args[1].split("-")[1])

                    await self.user_service.track_user(tg_chat_id, model.SourceType.POST_LINK)

                    text, photo, file, keyboard = await self.post_short_link_service.trigger(post_short_link_id)
                    if photo is not None and file is not None:
                        await self.bot.send_photo(tg_chat_id, photo, caption=text)
                        await self.bot.send_document(tg_chat_id, file, reply_markup=keyboard)
                    elif photo is not None:
                        await self.bot.send_photo(tg_chat_id, photo, caption=text, reply_markup=keyboard)
                    elif file is not None:
                        await self.bot.send_document(tg_chat_id, file, caption=text, reply_markup=keyboard)
                    else:
                        await message.answer(text, reply_markup=keyboard)

                    await self.chat_client.import_message_to_amocrm(tg_chat_id, text)
                    return

                await self.user_service.track_user(tg_chat_id, model.SourceType.DIRECT_LINK)

                await self.estate_expert_client.delete_all_message(tg_chat_id)
                await self.__set_bot_commands()

                await self.state_service.delete_state_by_tg_chat_id(tg_chat_id)
                state_id = await self.state_service.create_state(tg_chat_id)
                await self.state_service.change_status(state_id, common.StateStatuses.wewall_expert)

                await self.wewall_expert_message_service.handler(message, None)
                span.set_status(StatusCode.OK)
            except (IndexError, ValueError):
                await self.bot.send_message(
                    message.chat.id,
                    "Некорректная ссылка. Пожалуйста, проверьте правильность ввода. Либо нажмите /start"
                )
                return
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def estate_search_handler(self, message: Message, user_state: model.State):
        with self.tracer.start_as_current_span(
                "CommandController.estate_search_handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                await self.state_service.change_status(user_state.id, common.StateStatuses.estate_search)
                await self.estate_search_message_service.handler(message, user_state)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def finance_model_handler(self, message: Message, user_state: model.State):
        with self.tracer.start_as_current_span(
                "CommandController.finance_model_handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                await self.state_service.change_status(user_state.id, common.StateStatuses.estate_finance_model)
                await self.estate_finance_model_message_service.handler(message, user_state)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err


    async def news_handler(self, message: Message, user_state: model.State):
            with self.tracer.start_as_current_span(
                    "CommandController.news_handler",
                    kind=SpanKind.INTERNAL
            ) as span:
                try:
                    await self.estate_expert_client.delete_all_message(message.chat.id)
                    await self.state_service.change_status(user_state.id, common.StateStatuses.estate_expert)
                    await self.estate_expert_message_service.handler(message, user_state)

                    span.set_status(StatusCode.OK)
                except Exception as err:
                    span.record_exception(err)
                    span.set_status(StatusCode.ERROR, str(err))
                    raise err


    async def manager_handler(self, message: Message, user_state: model.State):
            with self.tracer.start_as_current_span(
                    "CommandController.manager_handler",
                    kind=SpanKind.INTERNAL
            ) as span:
                try:
                    await self.chat_client.edit_lead(message.chat.id, self.amocrm_appeal_pipeline_id,
                                                self.amocrm_pipeline_status_chat_with_manager)
                    await self.state_service.set_is_transferred_to_manager(user_state.id, True)

                    await self.estate_expert_client.delete_all_message(message.chat.id)
                    await self.amocrm_manager_message_service.handler(message, user_state)
                    await message.answer(common.manger_is_connecting_text)

                    span.set_status(StatusCode.OK)
                except Exception as err:
                    span.record_exception(err)
                    span.set_status(StatusCode.ERROR, str(err))
                    raise err

    async def __set_bot_commands(self):
        commands = [
            BotCommand(command="/start", description="Перезапустить бота"),
            BotCommand(command="/estate_search", description="Поиск недвижимости"),
            BotCommand(command="/finance_model", description="Оценка доходности"),
            BotCommand(command="/news", description="Тренды и новости"),
            BotCommand(command="/manager", description="Связаться с менеджером"),
        ]
        await self.bot.set_my_commands(commands)

