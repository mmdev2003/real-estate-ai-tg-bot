from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model
from .query import *


class WewallRepo(interface.IWewallRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def get_wewall(self) -> model.Wewall:
        with self.tracer.start_as_current_span(
                "WewallRepo.get_wewall",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                rows = await self.db.select(get_wewall, {})

                if rows:
                    rows = model.Analysis.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows[0]
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise