import io
from uuid import uuid4

from opentelemetry.trace import SpanKind, StatusCode

from internal import interface, common


class PostShortLinkService(interface.IPostShortLinkService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            storage: interface.IStorage,
            state_service: interface.IStateService,
            post_short_link_repo: interface.IPostShortLinkRepo,
            wewall_tg_bot_client: interface.IWewallTgBotClient,
            bot_link: str
    ):
        self.tracer = tel.tracer()
        self.storage = storage
        self.state_service = state_service
        self.post_short_link_repo = post_short_link_repo
        self.wewall_tg_bot_client = wewall_tg_bot_client
        self.bot_link = bot_link

    async def create_post_short_link(self, state_id: int, tg_chat_id: int):
        with self.tracer.start_as_current_span(
                "PostShortLinkService.create_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                await self.post_short_link_repo.create_post_short_link(tg_chat_id)
                await self.state_service.change_status(state_id, common.StateStatuses.post_name)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_name(self, tg_chat_id: int, name: str):
        with self.tracer.start_as_current_span(
                "PostShortLinkService.update_name",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "name": name
                }
        ) as span:
            try:
                await self.post_short_link_repo.update_name(tg_chat_id, name)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_description(self, tg_chat_id: int, description: str):
        with self.tracer.start_as_current_span(
                "PostShortLinkService.update_description",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "description": description
                }
        ) as span:
            try:
                await self.post_short_link_repo.update_description(tg_chat_id, description)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_image(self, tg_chat_id: int, image: io.BytesIO):
        with self.tracer.start_as_current_span(
                "PostShortLinkService.update_images",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "image": str(image)

                }
        ) as span:
            try:
                image_name = str(uuid4())
                upload_response = self.storage.upload(image, image_name)

                await self.post_short_link_repo.update_image(tg_chat_id, image_name, upload_response.fid)

            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_file(self, tg_chat_id: int, file_name: str, file: io.BytesIO):
        with self.tracer.start_as_current_span(
                "PostShortLinkService.update_file",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                upload_response = self.storage.upload(file, file_name)

                await self.post_short_link_repo.update_file(tg_chat_id, file_name, upload_response.fid)

            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def generate_post_short_deep_link(self, tg_chat_id: int) -> tuple[str, str]:
        with self.tracer.start_as_current_span(
                "PostShortLinkService.generate_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                post_short_link = (await self.post_short_link_repo.post_short_link_by_tg_chat_id(tg_chat_id))[0]
                await self.wewall_tg_bot_client.send_post_short_link(
                    post_short_link.id,
                    post_short_link.name,
                    post_short_link.description,
                    post_short_link.image_name,
                    post_short_link.image_fid,
                    post_short_link.file_name,
                    post_short_link.file_fid,
                )
                await self.post_short_link_repo.delete_post_short_link(tg_chat_id)

                post_short_deep_link = self.bot_link + "?start=" + "post_short_link_id-" + str(post_short_link.id)

                span.set_status(StatusCode.OK)
                return post_short_link.name, post_short_deep_link
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_post_short_link(self, state_id: int, tg_chat_id: int):
        with self.tracer.start_as_current_span(
                "PostShortLinkService.delete_post_short_link",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                await self.post_short_link_repo.delete_post_short_link(tg_chat_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
