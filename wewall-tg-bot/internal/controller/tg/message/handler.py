from aiogram.types import Message
from opentelemetry.trace import SpanKind, StatusCode

from internal import model, interface, common


class MessageController(interface.IMessageController):

    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_manager_message_service: interface.IAmoCrmManagerMessageService,
            wewall_expert_message_service: interface.IWewallExpertMessageService,
            estate_expert_message_service: interface.IEstateExpertMessageService,
            estate_search_message_service: interface.IEstateSearchMessageService,
            estate_finance_model_message_service: interface.IEstateFinanceModelMessageService,
            contact_collector_message_service: interface.IContactCollectorMessageService,
    ):
        self.logger = tel.logger()
        self.tracer = tel.tracer()
        self.amocrm_manager_message_service = amocrm_manager_message_service
        self.wewall_expert_message_service = wewall_expert_message_service
        self.estate_expert_message_service = estate_expert_message_service
        self.estate_search_message_service = estate_search_message_service
        self.estate_finance_model_message_service = estate_finance_model_message_service
        self.contact_collector_message_service = contact_collector_message_service


    async def message_handler(self, message: Message, user_state: model.State):
        with self.tracer.start_as_current_span(
                "MessageController.message_handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if user_state.status == common.StateStatuses.wewall_expert:
                    self.logger.info("Обработка сообщения в состоянии wewall_expert")
                    await self.wewall_expert_message_service.handler(message, user_state)

                elif user_state.status == common.StateStatuses.estate_expert:
                    self.logger.info("Обработка сообщения в состоянии estate_expert")
                    await self.estate_expert_message_service.handler(message, user_state)

                elif user_state.status == common.StateStatuses.estate_search:
                    self.logger.info("Обработка сообщения в состоянии estate_search")
                    await self.estate_search_message_service.handler(message, user_state)

                elif user_state.status == common.StateStatuses.estate_finance_model:
                    self.logger.info("Обработка сообщения в состоянии estate_finance_model")
                    await self.estate_finance_model_message_service.handler(message, user_state)

                elif user_state.status == common.StateStatuses.chat_with_amocrm_manager:
                    self.logger.info("Обработка сообщения в состоянии chat_with_amocrm_manager")
                    await self.amocrm_manager_message_service.handler(message, user_state)

                elif user_state.status == common.StateStatuses.contact_collector:
                    self.logger.info("Обработка сообщения в состоянии contact_collector")
                    await self.contact_collector_message_service.handler(message, user_state)

                span.set_status(StatusCode.OK)

            except common.MetroStationNotFound as err:
                self.logger.warning("Станция метро не найдена")
                await message.answer(f"Станция метро не найдена. Попробуйте другую станцию метро")

            except common.TransactionDictSumNotEqual100 as err:
                self.logger.warning("Сумма транзакций не равна 100%")
                await message.answer(f"{err}. Исправьте")

            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
