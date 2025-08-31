from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model,interface

from pkg.client.client import AsyncHTTPClient


class WewallEstateExpertClient(interface.IWewallEstateExpertClient):
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
            prefix="/api/estate-expert",
            use_tracing=True,
            logger=self.logger,
        )
        self.tracer = tel.tracer()

    async def send_message_to_wewall_expert(self, tg_chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.send_message_to_wewall_expert",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text}
                response = await self.client.post("/message/send/tg/wewall-expert", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["llm_response"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_expert(self, tg_chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.send_message_to_estate_expert",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text}
                response = await self.client.post("/message/send/tg/estate-expert", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["llm_response"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_search_expert(self, tg_chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.send_message_to_estate_search_expert",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text}
                response = await self.client.post("/message/send/tg/estate-search-expert", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["llm_response"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_analysis_expert(self, tg_chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.send_message_to_estate_analysis_expert",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text}
                response = await self.client.post("/message/send/tg/estate-analysis-expert", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["llm_response"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_estate_finance_model_expert(self, tg_chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.send_message_to_estate_finance_model_expert",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text}
                response = await self.client.post("/message/send/tg/estate-calculator-expert", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["llm_response"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_contact_collector(self, tg_chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.send_message_to_contact_collector",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text}
                response = await self.client.post("/message/send/tg/contact-collector", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["llm_response"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def add_message_to_chat(self, tg_chat_id: int, text: str, role: str):
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.add_message_to_chat",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id, "text": text, "role": role}
                response = await self.client.post("/message/create", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def summary(self, tg_chat_id: int) -> str:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.summary",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id}
                response = await self.client.post("/tg/summary", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return json_response["chat_summary"]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_all_message(self, tg_chat_id: int) -> None:
        with self.tracer.start_as_current_span(
                "WewallEstateExpertClient.delete_all_message",
                kind=SpanKind.CLIENT,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                body = {"tg_chat_id": tg_chat_id}
                response = await self.client.post("/message/delete/all", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
