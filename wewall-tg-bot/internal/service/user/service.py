from opentelemetry.trace import StatusCode, SpanKind

from internal import interface, model


class UserService(interface.IUserService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            user_repo: interface.IUserRepo
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.user_repo = user_repo

    async def track_user(self, tg_chat_id: int, source_type: str) -> None:
        with self.tracer.start_as_current_span(
                "UserService.create_user",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "source_type": source_type
                }
        ) as span:
            try:
                user = await self.user_repo.user_by_tg_chat_id(tg_chat_id)
                if not user:
                    self.logger.info("Новый пользователь")
                    await self.user_repo.create_user(tg_chat_id, source_type)
                    span.set_status(StatusCode.OK)

            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def all_user(self) -> list[model.User]:
        with self.tracer.start_as_current_span(
                "UserService.all_user",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                users = await self.user_repo.all_user()

                span.set_status(StatusCode.OK)
                return users
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def update_is_bot_blocked(self, user_id: int, is_bot_blocked: bool = True) -> None:
        with self.tracer.start_as_current_span(
                "UserService.update_is_bot_blocked",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.user_repo.update_is_bot_blocked(user_id, is_bot_blocked)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise