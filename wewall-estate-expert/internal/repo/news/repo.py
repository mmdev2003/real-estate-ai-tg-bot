from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model
from .query import *


class NewsRepo(interface.INewsRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_news(self, news_name: str, news_summary: str) -> int:
        with self.tracer.start_as_current_span(
                "NewsRepo.create_news",
                kind=SpanKind.INTERNAL,
                attributes={
                    "news_name": news_name,
                    "news_summary": news_summary,
                }
        ) as span:
            try:
                body = {
                    "news_name": news_name,
                    "news_summary": news_summary
                }
                news_id = await self.db.insert(create_news, body)

                span.set_status(Status(StatusCode.OK))
                return news_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def all_news(self) -> list[model.News]:
        with self.tracer.start_as_current_span(
                "NewsRepo.all_news",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(all_news, {})
                if rows:
                    rows = model.News.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise