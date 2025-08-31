import json
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface
from .sql_query import *


class EstateRepo(interface.IEstateRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_estate(
            self,
            link: str,
            name: str,
            category: str,
            address: str,
            coords: model.Coords,
            metro_stations: list[model.MetroStation],
    ) -> int:
        with self.tracer.start_as_current_span(
                "EstateRepo.create_estate",
                kind=SpanKind.INTERNAL,
                attributes={
                    "link": link,
                    "name": name,
                    "category": category,
                    "address": address,
                    "coords": coords,
                    "metro_stations": metro_stations
                },
        ) as span:
            try:
                args = {
                    "link": link,
                    "name": name,
                    "category": category,
                    "address": address,
                    "metro_stations": [json.dumps(metro_station.to_dict(), ensure_ascii=False) for metro_station in
                                       metro_stations],
                    "coords": json.dumps(coords.to_dict(), ensure_ascii=False)
                }

                estate_id = await self.db.insert(create_estate, args)

                span.set_status(Status(StatusCode.OK))
                return estate_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def estate_by_id(self, estate_id: int) -> list[model.Estate]:
        with self.tracer.start_as_current_span(
                "EstateRepo.estate_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "estate_id": estate_id
                },
        ) as span:
            try:
                args = {"estate_id": estate_id}
                rows = await self.db.select(estate_by_id, args)
                if rows:
                    rows = model.Estate.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def all_estate(self) -> list[model.Estate]:
        with self.tracer.start_as_current_span(
                "EstateRepo.all_estate",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                args = {}
                rows = await self.db.select(all_estate, args)
                if rows:
                    rows = model.Estate.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

