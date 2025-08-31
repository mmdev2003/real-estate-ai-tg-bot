from internal import interface, model

from opentelemetry.trace import StatusCode, SpanKind

from .query import *


class UserRepo(interface.IUserRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()

        self.db = db

    async def create_user(self, tg_chat_id: int, source_type: str) -> int:
        with self.tracer.start_as_current_span(
                "UserRepo.create_user",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "source_type": source_type
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                    "source_type": source_type
                }
                user_id = await self.db.insert(create_user, args)

                span.set_status(StatusCode.OK)
                return user_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def user_by_tg_chat_id(self, tg_chat_id: int) -> list[model.User]:
        with self.tracer.start_as_current_span(
                "UserRepo.update_source_type",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id
                }
                rows = await self.db.select(user_by_tg_chat_id, args)
                if rows:
                    rows = model.User.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def update_is_bot_blocked(self, user_id: int, is_bot_blocked: bool) -> None:
        with self.tracer.start_as_current_span(
                "UserRepo.update_is_bot_blocked",
                kind=SpanKind.INTERNAL,
                attributes={
                    "user_id": user_id,
                    "is_bot_blocked": is_bot_blocked
                }
        ) as span:
            try:
                args = {
                    "user_id": user_id,
                    "is_bot_blocked": is_bot_blocked
                }
                await self.db.update(update_is_bot_blocked, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def all_user(self) -> list[model.User]:
        with self.tracer.start_as_current_span(
                "UserRepo.all_user",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(all_user, {})
                if rows:
                    rows = model.User.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise
