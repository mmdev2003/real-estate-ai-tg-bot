from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface

from pkg.client.client import AsyncHTTPClient


class WewallChatClient(interface.IWewallChatClient):
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
            prefix="/api/chat",
            use_tracing=True,
            logger=self.logger,
        )
        self.tracer = tel.tracer()

    async def create_chat_with_amocrm_manager(
            self,
            amocrm_pipeline_id: int,
            tg_chat_id: int,
            tg_username: str,
            first_name: str,
            last_name: str,
    ):
        with self.tracer.start_as_current_span(
                "WewallChatClient.create_chat_with_amocrm_manager",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "tg_chat_id": tg_chat_id,
                    "tg_username": tg_username,
                    "first_name": first_name,
                    "last_name": last_name,
                }
        ) as span:
            try:
                body = {
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "tg_chat_id": tg_chat_id,
                    "tg_username": tg_username,
                    "first_name": first_name,
                    "last_name": last_name,
                }
                response = await self.client.post("/create/tg/amocrm", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def send_message_to_amocrm(self, tg_chat_id: int, text: str):
        with self.tracer.start_as_current_span(
                "WewallChatClient.send_message_to_amocrm",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text,
                }
        ) as span:
            try:
                body = {
                    "tg_chat_id": tg_chat_id,
                    "text": text,
                }
                response = await self.client.post("/message/send/tg/amocrm", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def import_message_to_amocrm(self, tg_chat_id: int, text: str):
        with self.tracer.start_as_current_span(
                "WewallChatClient.import_message_to_amocrm",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text,
                }
        ) as span:
            try:
                body = {
                    "tg_chat_id": tg_chat_id,
                    "text": text,
                }
                response = await self.client.post("/message/import/tg/amocrm", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def edit_lead(self, tg_chat_id: int, amocrm_pipeline_id: int, amocrm_pipeline_status_id: int):
        with self.tracer.start_as_current_span(
                "WewallChatClient.edit_lead",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "amocrm_pipeline_status_id": amocrm_pipeline_status_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                }
        ) as span:
            try:
                body = {
                    "tg_chat_id": tg_chat_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "amocrm_pipeline_status_id": amocrm_pipeline_status_id,
                }
                response = await self.client.post("/lead/edit", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
