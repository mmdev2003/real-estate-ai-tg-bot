import io

from aiogram import Bot
from aiogram.types import Message
from opentelemetry.trace import SpanKind, StatusCode

from internal import model, interface, common


class MessageController(interface.IMessageController):

    def __init__(
            self,
            bot: Bot,
            tel: interface.ITelemetry,
            post_short_link_service: interface.IPostShortLinkService,
            state_service: interface.IStateService,
            storage: interface.IStorage,
    ):
        self.bot = bot
        self.logger = tel.logger()
        self.tracer = tel.tracer()
        self.post_short_link_service = post_short_link_service
        self.state_service = state_service
        self.storage = storage

    async def message_handler(self, message: Message, user_state: model.State):
        with self.tracer.start_as_current_span(
                "MessageController.message_handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if user_state.status == common.StateStatuses.post_name:
                    await self.post_short_link_service.update_name(
                        message.chat.id,
                        message.text
                    )
                    await self.state_service.change_status(user_state.id, common.StateStatuses.post_description)
                    await message.answer(common.PostMessageText.post_description)

                if user_state.status == common.StateStatuses.post_description:
                    if len(message.text) >= common.MAX_TEXT_SIZE:
                        await message.answer(
                            common.PostMessageError.text_size
                        )
                        return

                    await self.post_short_link_service.update_description(
                        message.chat.id,
                        message.text
                    )
                    await self.state_service.change_status(user_state.id, common.StateStatuses.post_images)
                    await message.answer(common.PostMessageText.post_images)

                if user_state.status == common.StateStatuses.post_images:
                    if message.photo:
                        photo = message.photo[-1]

                        image_buffer = io.BytesIO()
                        await self.bot.download(photo.file_id, image_buffer)
                        image_buffer.seek(0)

                        await self.post_short_link_service.update_image(
                            message.chat.id,
                            image_buffer
                        )

                    await self.state_service.change_status(user_state.id, common.StateStatuses.post_file)
                    await message.answer(common.PostMessageText.post_file)

                if user_state.status == common.StateStatuses.post_file:
                    if message.document:
                        if message.document.file_size > common.MAX_FILE_SIZE:
                            await self.bot.send_message(
                                message.chat.id,
                                common.PostMessageError.file_size
                            )
                            return

                        document = message.document
                        file_name = document.file_name
                        file_buffer = io.BytesIO()
                        await self.bot.download(document.file_id, file_buffer)
                        file_buffer.seek(0)
                        await self.post_short_link_service.update_file(message.chat.id, file_name, file_buffer)

                    post_short_link_name, post_short_deep_link = await self.post_short_link_service.generate_post_short_deep_link(
                        user_state.tg_chat_id)
                    await message.answer(
                        f"Ваша ссылка для поста на тему '{post_short_link_name}':\n{post_short_deep_link}")
                    await message.answer("Для создания новой ссылки нажмите /start")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
