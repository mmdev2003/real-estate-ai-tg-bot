from aiogram.types import CallbackQuery
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface, common


class WewallExpertCallbackService(interface.IWewallExpertCallbackService):
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
        self.wewall_expert_inline_keyboard_generator = wewall_expert_inline_keyboard_generator
        self.chat_client = chat_client
        self.amocrm_appeal_pipeline_id = amocrm_appeal_pipeline_id
        self.amocrm_pipeline_status_chat_with_manager = amocrm_pipeline_status_chat_with_manager

    async def to_estate_search(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "WewallExpertCallbackService.to_estate_search",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(callback.message.chat.id)
                await self.state_repo.change_status(state.id, common.StateStatuses.estate_search)
                llm_response = await self.estate_expert_client.send_message_to_estate_search_expert(
                    state.tg_chat_id,
                    "Помоги подобрать недвижимость"
                )

                await callback.message.answer(llm_response, parse_mode="HTML")
                await self.chat_client.import_message_to_amocrm(callback.message.chat.id, llm_response)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def to_estate_finance_model(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "WewallExpertCallbackService.to_estate_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(callback.message.chat.id)
                await self.state_repo.change_status(state.id, common.StateStatuses.estate_finance_model)
                llm_response = await self.estate_expert_client.send_message_to_estate_finance_model_expert(
                    state.tg_chat_id,
                    "Помоги рассчитать доходность объекта"
                )

                await callback.message.answer(llm_response, parse_mode="HTML")
                await self.chat_client.import_message_to_amocrm(callback.message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def to_estate_expert(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "WewallExpertCallbackService.to_estate_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(callback.message.chat.id)
                await self.state_repo.change_status(state.id, common.StateStatuses.estate_expert)
                llm_response = await self.estate_expert_client.send_message_to_estate_expert(
                    state.tg_chat_id,
                    "Какие новости на рынке недвижимости?"
                )

                await callback.message.answer(llm_response)
                await self.chat_client.import_message_to_amocrm(callback.message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def to_manager(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "WewallExpertCallbackService.to_manager",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.chat_client.edit_lead(callback.message.chat.id, self.amocrm_appeal_pipeline_id,
                                                 self.amocrm_pipeline_status_chat_with_manager)
                await self.state_repo.set_is_transferred_to_manager(state.id, True)

                summary = await self.estate_expert_client.summary(state.tg_chat_id)
                await self.chat_client.import_message_to_amocrm(
                    state.tg_chat_id,
                    summary
                )
                await self.estate_expert_client.delete_all_message(callback.message.chat.id)

                await callback.message.answer(common.manger_is_connecting_text)
                await self.chat_client.import_message_to_amocrm(callback.message.chat.id,
                                                                common.manger_is_connecting_text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def start(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "WewallExpertCallbackService.start",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                tg_chat_id = callback.message.chat.id
                llm_response = await self.estate_expert_client.send_message_to_wewall_expert(
                    tg_chat_id,
                    "Привет, расскажи про WEWALL AI"
                )

                await self.estate_expert_client.delete_all_message(tg_chat_id)

                await self.state_repo.delete_state_by_tg_chat_id(tg_chat_id)
                state_id = await self.state_repo.create_state(tg_chat_id)
                await self.state_repo.change_status(state_id, common.StateStatuses.wewall_expert)

                keyboard = await self.wewall_expert_inline_keyboard_generator.start()
                await callback.message.answer(
                    llm_response,
                    reply_markup=keyboard,
                    show_alert=False
                )
                await self.chat_client.import_message_to_amocrm(tg_chat_id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise
