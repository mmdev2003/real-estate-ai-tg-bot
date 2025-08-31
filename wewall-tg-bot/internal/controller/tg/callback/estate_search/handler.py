from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import model, interface, common


class EstateSearchCallbackController(interface.IEstateSearchCallbackController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            dp: Dispatcher,
            estate_search_callback_service: interface.IEstateSearchCallbackService,
    ):
        self.dp = dp
        self.estate_search_callback_service = estate_search_callback_service
        self.tracer = tel.tracer()
        self.logger = tel.logger()

    async def estate_search_callback(self, callback: CallbackQuery, user_state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackController.estate_search_callback",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                offer_id = int(callback.data.split(":")[2])
                command = ":".join(callback.data.split(":")[:2])
                span.set_attributes({"offer_id": offer_id, "command": command})

                if command == common.EstateSearchKeyboardCallbackData.like_offer:
                    self.logger.info("Нажали кнопку нравится оффер")
                    await self.estate_search_callback_service.like_offer(callback, user_state, offer_id)

                elif command == common.EstateSearchKeyboardCallbackData.next_offer:
                    self.logger.info("Нажали кнопку следующий оффер")
                    await self.estate_search_callback_service.next_offer(callback, user_state)
                elif command == common.EstateSearchKeyboardCallbackData.next_estate:
                    self.logger.info("Нажали кнопку следующий объект")
                    await self.estate_search_callback_service.next_estate(callback, user_state)
                else:
                    self.logger.warning("Неизвестная команда")
                    pass
                await callback.answer()

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
