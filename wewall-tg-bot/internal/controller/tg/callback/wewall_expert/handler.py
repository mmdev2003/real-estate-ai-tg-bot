from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import model, interface, common


class WewallExpertCallbackController(interface.IWewallExpertCallbackController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            dp: Dispatcher,
            wewall_expert_callback_service: interface.IWewallExpertCallbackService,
    ):
        self.dp = dp
        self.wewall_expert_callback_service = wewall_expert_callback_service
        self.tracer = tel.tracer()
        self.logger = tel.logger()

    async def wewall_expert_callback(self, callback: CallbackQuery, user_state: model.State):
        with self.tracer.start_as_current_span(
                "WewallExpertCallbackController.wewall_expert_callback",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if callback.data == common.WewallExpertKeyboardCallbackData.to_estate_search:
                    self.logger.info("Нажали кнопку перехода на поиск недвижимости")
                    await self.wewall_expert_callback_service.to_estate_search(callback, user_state)

                elif callback.data == common.WewallExpertKeyboardCallbackData.to_estate_finance_model:
                    self.logger.info("Нажали кнопку перехода на расчет фин.модели")
                    await self.wewall_expert_callback_service.to_estate_finance_model(callback, user_state)

                elif callback.data == common.WewallExpertKeyboardCallbackData.to_estate_expert:
                    self.logger.info("Нажали кнопку перехода на экспертизу недвижимости")
                    await self.wewall_expert_callback_service.to_estate_expert(callback, user_state)

                elif callback.data == common.WewallExpertKeyboardCallbackData.to_manager:
                    self.logger.info("Нажали кнопку перехода на менеджера")
                    await self.wewall_expert_callback_service.to_manager(callback, user_state)

                elif callback.data == common.WewallExpertKeyboardCallbackData.start:
                    self.logger.info("Нажали кнопку перехода на менеджера")
                    await self.wewall_expert_callback_service.start(callback, user_state)
                else:
                    self.logger.warning("Неизвестная кнопка")
                    pass

                await callback.answer()
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
