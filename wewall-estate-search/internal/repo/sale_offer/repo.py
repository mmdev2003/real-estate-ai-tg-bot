from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface
from .sql_query import *


class SaleOfferRepo(interface.ISaleOfferRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_sale_offer(
            self,
            estate_id: int,
            link: str,
            name: str,
            square: float,
            price: int,
            price_per_meter: int,
            design: int,
            floor: int,
            type: int,
            location: str,
            image_urls: list[str],
            offer_readiness: int,
            readiness_date: str,
            description: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "SaleOfferRepo.create_sale_offer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "estate_id": estate_id,
                    "link": link,
                    "name": name,
                    "square": square,
                    "price": price,
                    "price_per_meter": price_per_meter,
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
                    "price": price,
                    "price_per_meter": price_per_meter,
                    "design": design,
                    "floor": floor,
                    "type": type,
                    "location": location,
                    "image_urls": image_urls,
                    "offer_readiness": offer_readiness,
                    "readiness_date": readiness_date,
                    "description": description,
                }
                sale_offer_id = await self.db.insert(create_sale_offer, args)

                span.set_status(Status(StatusCode.OK))
                return sale_offer_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def update_sale_offer_irr(self, sale_offer_id: int, irr: float) -> None:
        with self.tracer.start_as_current_span(
                "SaleOfferRepo.update_sale_offer_irr",
                kind=SpanKind.INTERNAL,
                attributes={
                    "sale_offer_id": sale_offer_id,
                    "irr": irr
                }
        ) as span:
            try:
                args = {"sale_offer_id": sale_offer_id, "irr": irr}
                await self.db.update(update_sale_offer_irr, args)
                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def sale_offer_by_id(self, sale_offer_id: int) -> list[model.SaleOffer]:
        with self.tracer.start_as_current_span(
                "SaleOfferRepo.sale_offer_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "sale_offer_id": sale_offer_id
                }
        ) as span:
            try:
                args = {"sale_offer_id": sale_offer_id}
                rows = await self.db.select(sale_offer_by_id, args)
                if rows:
                    rows = model.SaleOffer.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def all_sale_offer(self) -> list[model.SaleOffer]:
        with self.tracer.start_as_current_span(
                "SaleOfferRepo.all_sale_offer",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                args = {}
                rows = await self.db.select(all_sale_offer, args)
                if rows:
                    rows = model.SaleOffer.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

