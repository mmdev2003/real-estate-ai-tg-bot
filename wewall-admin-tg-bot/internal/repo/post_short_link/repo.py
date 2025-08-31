from opentelemetry.trace import SpanKind, StatusCode

from internal import interface, model
from .sql_query import *


class PostShortLinkRepo(interface.IPostShortLinkRepo):
    def __init__(self,
                 tel: interface.ITelemetry,
                 db: interface.IDB
                 ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_post_short_link(self, tg_chat_id: int):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.create_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                }

                post_short_link_id = await self.db.insert(create_post_short_link, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_name(self, tg_chat_id: int, name: str):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.update_name",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "name": name
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                    "name": name
                }

                await self.db.update(update_post_short_link_name, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_description(self, tg_chat_id: int, description: str):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.update_desc",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "description": description
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                    "description": description
                }
                await self.db.update(update_post_short_link_description, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_image(self, tg_chat_id: int, image_name: str, image_fid: str):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.update_image",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "image_name": image_name,
                    "image_fid": image_fid
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                    "image_name": image_name,
                    "image_fid": image_fid,
                }

                await self.db.update(update_post_short_link_image, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_file(self, tg_chat_id: int, file_name: str, file_fid: str):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.update_image",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                    "file_name": file_name,
                    "file_fid": file_fid,
                }
                await self.db.update(update_post_short_link_file, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_post_short_link(self, tg_chat_id: int):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.delete_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                }

                await self.db.delete(delete_post_short_link, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def post_short_link_by_tg_chat_id(self, tg_chat_id: int) -> list[model.PostShortLink]:
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.post_short_link_by_tg_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                args = {
                    "tg_chat_id": tg_chat_id,
                }

                rows = await self.db.select(post_short_link_by_tg_chat_id, args)
                if rows:
                    rows = model.PostShortLink.serialize(rows)


                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
