from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface
from .sql_query import *


class RentOfferRepo(interface.IRentOfferRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_rent_offer(
            self,
            estate_id: int,
            link: str,
            name: str,
            square: float,
            price_per_month: int,
            design: int,
            floor: int,
            type: int,
            location: int,
            image_urls: list[str],
            offer_readiness: int,
            readiness_date: str,
            description: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "RentOfferRepo.create_rent_offer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "estate_id": estate_id,
                    "link": link,
                    "name": name,
                    "square": square,
                    "price_per_month": price_per_month,
                    "design": design,
                    "floor": floor,
                    "type": type,
                    "location": location,
                    "image_urls": image_urls,
                    "offer_readiness": offer_readiness,
                    "readiness_date": readiness_date,
                    "description": description,
                }
        ) as span:
            try:
                args = {
                    "estate_id": estate_id,
                    "link": link,
                    "name": name,
                    "square": square,
                    "price_per_month": price_per_month,
                    "design": design,
                    "floor": floor,
                    "type": type,
                    "location": location,
                    "image_urls": image_urls,
                    "offer_readiness": offer_readiness,
                    "readiness_date": readiness_date,
                    "description": description,
                }
                sale_rent_id = await self.db.insert(create_rent_offer, args)

                span.set_status(Status(StatusCode.OK))
                return sale_rent_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def rent_offer_by_id(self, rent_offer_id: int) -> list[model.RentOffer]:
        with self.tracer.start_as_current_span(
                "RentOfferRepo.rent_offer_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "rent_offer_id": rent_offer_id
                }
        ) as span:
            try:
                args = {"rent_offer_id": rent_offer_id}
                rows = await self.db.select(rent_offer_by_id, args)
                if rows:
                    rows = model.RentOffer.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def all_rent_offer(self) -> list[model.RentOffer]:
        with self.tracer.start_as_current_span(
                "RentOfferRepo.all_rent_offer",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                args = {}
                rows = await self.db.select(all_rent_offer, args)
                if rows:
                    rows = model.RentOffer.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

