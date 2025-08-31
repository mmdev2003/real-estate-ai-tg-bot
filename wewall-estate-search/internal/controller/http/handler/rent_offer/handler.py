from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi.responses import JSONResponse

from .model import *
from internal import model, interface


class RentOfferController(interface.IRentOfferController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            rent_offer_service: interface.IRentOfferService,
    ):
        self.tracer = tel.tracer()
        self.rent_offer_service = rent_offer_service

    async def estate_search_rent(self, body: EstateSearchRentBody):
        with self.tracer.start_as_current_span(
                "RentOfferController.estate_search_rent",
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
                rent_offers = await self.rent_offer_service.find_rent_offers(
                    body.type,
                    body.budget,
                    body.location,
                    body.square,
                    body.estate_class,
                    body.distance_to_metro,
                    body.design,
                    body.readiness,
                    body.irr,
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"rent_offers": [rent_offer.to_dict() for rent_offer in rent_offers]},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
