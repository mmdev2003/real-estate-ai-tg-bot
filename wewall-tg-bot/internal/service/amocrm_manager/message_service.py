from aiogram.types import Message, ReplyKeyboardRemove
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model
from internal import interface
from internal import common


class AmocrmManagerMessageService(interface.IAmoCrmManagerMessageService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            state_repo: interface.IStateRepo,
            chat_client: interface.IWewallChatClient,
            estate_expert_client: interface.IWewallEstateExpertClient,
            wewall_expert_inline_keyboard_generator: interface.IWewallExpertInlineKeyboardGenerator,
    ):
        self.logger = tel.logger()
        self.tracer = tel.tracer()

        self.state_repo = state_repo
        self.chat_client = chat_client
        self.estate_expert_client = estate_expert_client
        self.wewall_expert_inline_keyboard_generator = wewall_expert_inline_keyboard_generator

    async def handler(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "AmocrmManagerMessageService.handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if message.text == "Закрыть чат с менеджером":
                    self.logger.info("Нажали на кнопку закрытия чата с менеджером")
                    await self.chat_client.import_message_to_amocrm(
                        message.chat.id,
                        "Клиент закрыл чат с менеджером"
                    )

                    await self.state_repo.change_status(state.id, common.StateStatuses.wewall_expert)

                    llm_response = await self.estate_expert_client.send_message_to_wewall_expert(
                        message.chat.id,
                        "Чат с менеджером закрыт. Расскажи о своих возможностях и сообщи мне, что чат закрыт"
                    )

                    keyboard = await self.wewall_expert_inline_keyboard_generator.start()
                    await message.answer("Чат с менеджером закрыт", reply_markup=ReplyKeyboardRemove())
                    await message.answer(llm_response, reply_markup=keyboard)
                    await self.chat_client.import_message_to_amocrm(state.tg_chat_id, llm_response)

                else:
                    self.logger.info("Отправляем сообщение менеджеру")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err


