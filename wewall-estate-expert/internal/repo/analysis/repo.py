from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface
from internal import model
from .query import *


class AnalysisRepo(interface.IAnalysisRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_analysis(self, analysis_name: str, analysis_summary: str) -> int:
        with self.tracer.start_as_current_span(
                "AnalysisRepo.create_analysis",
                kind=SpanKind.INTERNAL,
                attributes={
                    "analysis_name": analysis_name,
                    "analysis_summary": analysis_summary,
                }
        ) as span:
            try:
                args = {
                    "analysis_name": analysis_name,
                    "analysis_summary": analysis_summary,
                }
                analysis_id = await self.db.insert(create_analysis, args)

                span.set_status(Status(StatusCode.OK))
                return analysis_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def all_analysis(self) -> list[model.Analysis]:
        with self.tracer.start_as_current_span(
                "AnalysisRepo.all_analysis",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(all_analysis, {})

                if rows:
                    rows = model.Analysis.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err