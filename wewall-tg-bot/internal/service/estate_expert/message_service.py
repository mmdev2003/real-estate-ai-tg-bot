from aiogram.types import Message
from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import model, interface, common


class EstateExpertMessageService(interface.IEstateExpertMessageService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            state_repo: interface.IStateRepo,
            estate_expert_client: interface.IWewallEstateExpertClient,
            chat_client: interface.IWewallChatClient,
            wewall_expert_inline_keyboard_generator: interface.IWewallExpertInlineKeyboardGenerator,
            amocrm_appeal_pipeline_id: int,
            amocrm_pipeline_status_chat_with_manager: int,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.state_repo = state_repo
        self.estate_expert_client = estate_expert_client
        self.chat_client = chat_client
        self.wewall_expert_inline_keyboard_generator = wewall_expert_inline_keyboard_generator
        self.amocrm_appeal_pipeline_id = amocrm_appeal_pipeline_id
        self.amocrm_pipeline_status_chat_with_manager = amocrm_pipeline_status_chat_with_manager

    async def handler(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateExpertMessageService.handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                llm_response = await self.estate_expert_client.send_message_to_estate_expert(
                    message.chat.id,
                    message.text
                )

                if common.StateSwitchCommand.to_manager in llm_response:
                    self.logger.info("Получена команда перехода на менеджера")
                    await self.__to_manager(message, state)
                elif common.StateSwitchCommand.to_estate_finance_model_expert in llm_response:
                    self.logger.info("Получена команда переключения на расчет доходности недвижимости")
                    await self.__to_estate_finance_model_expert(message, state)

                elif common.StateSwitchCommand.to_wewall_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по wewall")
                    await self.__to_wewall_expert(message, state)

                elif common.StateSwitchCommand.to_estate_search_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по поиску недвижимости")
                    await self.__to_estate_search_expert(message, state)
                else:
                    await message.answer(llm_response)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def __to_manager(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateExpertMessageService.__to_manager",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await message.answer(common.manger_is_connecting_text)

                chat_summary = await self.estate_expert_client.summary(message.chat.id)
                await self.estate_expert_client.delete_all_message(message.chat.id)

                llm_response = await self.estate_expert_client.send_message_to_wewall_expert(
                    message.chat.id,
                    "Расскажи мне про WEWALL"
                )

                keyboard = await self.wewall_expert_inline_keyboard_generator.start()
                await message.answer(llm_response, reply_markup=keyboard)

                await self.state_repo.change_status(state.id, common.StateStatuses.wewall_expert)

                await self.chat_client.import_message_to_amocrm(message.chat.id, chat_summary)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)
                await self.chat_client.edit_lead(message.chat.id, self.amocrm_appeal_pipeline_id, self.amocrm_pipeline_status_chat_with_manager)
                await self.state_repo.set_is_transferred_to_manager(state.id, True)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def __to_estate_finance_model_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateExpertMessageService.__to_estate_finance_model_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                llm_response = await self.estate_expert_client.send_message_to_estate_finance_model_expert(
                    message.chat.id,
                    "Помоги, мне рассчитать доходность недвижимости"
                )
                await message.answer(llm_response)

                await self.state_repo.change_status(state.id, common.StateStatuses.estate_finance_model)

                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_wewall_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateExpertMessageService.__to_wewall_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                llm_response = await self.estate_expert_client.send_message_to_wewall_expert(
                    message.chat.id,
                    "Расскажи мне про WEWALL"
                )

                await self.state_repo.change_status(state.id, common.StateStatuses.wewall_expert)
                keyboard = await self.wewall_expert_inline_keyboard_generator.start()
                await message.answer(llm_response, reply_markup=keyboard)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_estate_search_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateExpertMessageService.__to_estate_search_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                llm_response = await self.estate_expert_client.send_message_to_estate_search_expert(
                    message.chat.id,
                    "Помоги мне подобрать недвижимость из вашего ассортимента"
                )

                await self.state_repo.change_status(state.id, common.StateStatuses.estate_search)
                await message.answer(llm_response)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
