from aiogram.enums import InputMediaType
from aiogram.types import InputMediaDocument, BufferedInputFile, InputMediaPhoto, InlineKeyboardMarkup
from opentelemetry.trace import SpanKind, StatusCode

from internal import interface, model


class PostShortLinkService(interface.IPostShortLinkService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            post_short_link_repo: interface.IPostShortLinkRepo,
            storage: interface.IStorage,
            post_short_link_inline_keyboard_generator: interface.IPostShortLinkInlineKeyboardGenerator,
    ):
        self.tracer = tel.tracer()
        self.post_short_link_repo = post_short_link_repo
        self.storage = storage
        self.post_short_link_inline_keyboard_generator = post_short_link_inline_keyboard_generator

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
                "PostShortLinkService.create_post_short_link",
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
                await self.post_short_link_repo.create_post_short_link(
                    post_short_link_id,
                    name,
                    description,
                    image_name,
                    image_fid,
                    file_name,
                    file_fid
                )

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def trigger(self, post_short_link_id: int) -> tuple[str, BufferedInputFile | None, BufferedInputFile | None, InlineKeyboardMarkup]:
        with self.tracer.start_as_current_span(
                "PostShortLinkService.trigger",
                kind=SpanKind.INTERNAL,
                attributes={
                    "post_short_link_id": post_short_link_id,
                }
        ) as span:
            try:
                post_short_link = (await self.post_short_link_repo.post_short_link_by_id(post_short_link_id))[0]
                # image
                if post_short_link.image_name != "":
                    image_file, _ = self.storage.download(post_short_link.image_fid, post_short_link.image_name)
                    image_file.seek(0)
                    file_bytes = image_file.read()
                    photo = BufferedInputFile(file_bytes, filename=post_short_link.image_name)
                else:
                    photo = None
                # file
                if post_short_link.file_name != "":
                    file_stream, _ = self.storage.download(post_short_link.file_fid, post_short_link.file_name)
                    file_stream.seek(0)
                    file_bytes = file_stream.read()
                    file = BufferedInputFile(file_bytes, filename=post_short_link.file_name)
                else:
                    file = None

                keyboard = await self.post_short_link_inline_keyboard_generator.start()
                text = post_short_link.description + "\n"

                return text, photo, file, keyboard
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err