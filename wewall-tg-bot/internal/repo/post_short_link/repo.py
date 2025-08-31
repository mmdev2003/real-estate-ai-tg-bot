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

    async def create_post_short_link(
            self,
            post_short_link_id: int,
            name: str,
            description: str,
            image_name: str,
            image_fid: str,
            file_name: str,
            file_fid: str
    ):
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.create_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "post_short_link_id": post_short_link_id,
                    "name": name,
                    "description": description,
                    "image_name": image_name,
                    "file_name": file_name
                }
        ) as span:
            try:
                args = {
                    "post_short_link_id": post_short_link_id,
                    "name": name,
                    "description": description,
                    "image_name": image_name,
                    "image_fid": image_fid,
                    "file_name": file_name,
                    "file_fid": file_fid
                }

                await self.db.insert(create_post_short_link, args)

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

    async def post_short_link_by_id(self, post_short_link_id: int) -> list[model.PostShortLink]:
        with self.tracer.start_as_current_span(
                "PostShortLinkRepo.post_short_link_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "post_short_link_id": post_short_link_id
                }
        ) as span:
            try:
                args = {
                    "post_short_link_id": post_short_link_id,
                }

                rows = await self.db.select(post_short_link_by_id, args)
                if rows:
                    rows = model.PostShortLink.serialize(rows)


                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

