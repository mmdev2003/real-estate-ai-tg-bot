from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface

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

    async def send_post_short_link(
            self,
            post_short_link_id: int,
            name: str,
            description: str,
            image_name: str,
            image_fid: str,
            file_name: str,
            file_fid: str,
    ) -> None:
        with self.tracer.start_as_current_span(
                "WewallTgBotClient.send_post_short_link",
                kind=SpanKind.CLIENT,
                attributes={
                    "post_short_link_id": post_short_link_id,
                    "name": name,
                    "description": description,
                    "image_name": image_name,
                    "file_name": file_name,
                }
        ) as span:
            try:
                body = {
                    "post_short_link_id": post_short_link_id,
                    "name": name,
                    "description": description,
                    "image_name": image_name,
                    "image_fid": image_fid,
                    "file_name": file_name,
                    "file_fid": file_fid,
                }
                self.logger.debug("Тело запроса: ", {"body": body})
                response = await self.client.post("/post-short-link/create", json=body)

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
