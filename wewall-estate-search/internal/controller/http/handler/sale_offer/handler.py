from opentelemetry.trace import Status, StatusCode, SpanKind

from fastapi.responses import JSONResponse
from internal import model, interface
from .model import *


class SaleOfferController(interface.ISaleOfferController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            sale_offer_service: interface.ISaleOfferService
    ):
        self.tracer = tel.tracer()
        self.sale_offer_service = sale_offer_service

    async def estate_search_sale(self, body: EstateSearchSaleBody):
        with self.tracer.start_as_current_span(
                "SaleOfferController.estate_search_sale",
                kind=SpanKind.INTERNAL,
                attributes={
                    "type": body.type,
                    "budget": body.budget,
                    "location": body.location,
                    "square": body.square,
                    "estate_class": body.estate_class,
                    "distance_to_metro": body.distance_to_metro,
                    "design": body.design,
                    "readiness": body.readiness,
                    "irr": body.irr,
                }
        ) as span:
            try:
                sale_offers = await self.sale_offer_service.find_sale_offers(
                    body.type,
                    body.budget,
                    body.location,
                    body.square,
                    body.estate_class,
                    body.distance_to_metro,
                    body.design,
                    body.readiness,
                    body.irr
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"sale_offers": [sale_offer.to_dict() for sale_offer in sale_offers]},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
