from pyrogram import Client
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface


class TgNewsParser(interface.ITgNewsParsing):
    def __init__(
            self,
            tel: interface.ITelemetry,
            phone_number: str,
            api_id: int,
            api_hash: str
    ):
        self.tracer = tel.tracer()
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash

    async def parse(self, channel_name: str) -> str:
        with self.tracer.start_as_current_span(
                "TgNewsParser.parse",
                kind=SpanKind.INTERNAL,
                attributes={
                    "channel_name": channel_name
                }
        ) as span:
            try:
                self.app = await self.__start_client()
                messages_list = []

                async with self.app:
                    channel = await self.app.get_chat(channel_name)
                    async for message in self.app.get_chat_history(channel.id, limit=50):
                        if message.text:
                            messages_list.append(message.text)
                        elif message.caption:
                            messages_list.append(message.caption)

                news = await self.__list_to_str(messages_list)

                span.set_status(Status(StatusCode.OK))
                return news
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def __list_to_str(self, messages_list: list[str]) -> str:
        with self.tracer.start_as_current_span(
                "TgNewsParser.__list_to_str",
                kind=SpanKind.INTERNAL,
                attributes={
                    "messages_list": messages_list
                }
        ) as span:
            try:
                news = ""
                for message in messages_list:
                    news += message
                    news += "\n\n"

                span.set_status(Status(StatusCode.OK))
                return news
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def __start_client(self):
        with self.tracer.start_as_current_span(
                "TgNewsParser.__start_client",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                app = Client(
                    "pkg/my_account",
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    phone_number=self.phone_number
                )

                span.set_status(Status(StatusCode.OK))
                return app
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise