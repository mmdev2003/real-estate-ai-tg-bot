from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface

from pkg.client.client import AsyncHTTPClient


class WewallTgBotClient(interface.IWewallTgBotClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int
    ):

        self.logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/tg-bot",
            use_tracing=True,
            logger=self.logger,
        )
        self.tracer = tel.tracer()

    async def send_message_to_user(self, tg_chat_id: int, text: str):
        with self.tracer.start_as_current_span(
                "WewallTgBotClient.send_message_to_user",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }

                response = await self.client.post("/message/send", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def delete_state(self, tg_chat_id: int):
        with self.tracer.start_as_current_span(
                "WewallTgBotClient.delete_state",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id}

                response = await self.client.post("/state/delete", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
