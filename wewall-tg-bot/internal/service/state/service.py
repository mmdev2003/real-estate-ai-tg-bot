from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface


class StateService(interface.IStateService):
    def __init__(self, tel: interface.ITelemetry, state_repo: interface.IStateRepo):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.state_repo = state_repo

    async def create_state(self, tg_chat_id: int) -> int:
        with self.tracer.start_as_current_span(
                "StateService.create_state",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                state_id = await self.state_repo.create_state(tg_chat_id)

                span.set_status(StatusCode.OK)
                return state_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise


    async def state_by_id(self, tg_chat_id: int) -> list[model.State]:
        with self.tracer.start_as_current_span(
                "StateService.state_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                state = await self.state_repo.state_by_id(tg_chat_id)

                span.set_status(StatusCode.OK)
                return state
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def increment_message_count(self, state_id: int) -> None:
        with self.tracer.start_as_current_span(
                "StateService.increment_message_count",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                }
        ) as span:
            try:
                await self.state_repo.increment_message_count(state_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise
    async def change_status(self, state_id: int, status: str) -> None:
        with self.tracer.start_as_current_span(
                "StateService.change_status",
                kind=SpanKind.INTERNAL,
                attributes={
                    "status": status,
                    "state_id": state_id
                }
        ) as span:
            try:
                await self.state_repo.change_status(state_id, status)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise


    async def delete_state_by_tg_chat_id(self, tg_chat_id: int) -> None:
        with self.tracer.start_as_current_span(
                "StateService.delete_state_by_tg_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                await self.state_repo.delete_state_by_tg_chat_id(tg_chat_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def set_is_transferred_to_manager(self, state_id: int, is_transferred_to_manager: bool) -> None:
        with self.tracer.start_as_current_span(
                "StateService.set_is_transferred_to_manager",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                    "is_transferred_to_manager": is_transferred_to_manager,
                }
        ) as span:
            try:
                await self.state_repo.set_is_transferred_to_manager(state_id, is_transferred_to_manager)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

