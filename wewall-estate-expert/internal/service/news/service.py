from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model

class NewsService(interface.INewsService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            news_repo: interface.INewsRepo
    ):
        self.tracer = tel.tracer()
        self.news_repo = news_repo

    async def create_news(self, news_name: str, news_summary: str) -> int:
        with self.tracer.start_as_current_span(
                "NewsService.create_news",
                kind=SpanKind.INTERNAL,
                attributes={
                    "news_name": news_name,
                    "news_summary": news_summary,
                }
        ) as span:
            try:
                news_id = await self.news_repo.create_news(news_name, news_summary)

                span.set_status(Status(StatusCode.OK))
                return news_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def all_news(self) -> list[model.News]:
        with self.tracer.start_as_current_span(
                "NewsService.all_news",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                news = await self.news_repo.all_news()

                span.set_status(Status(StatusCode.OK))
                return news
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
