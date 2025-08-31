from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface

from pkg.client.client import AsyncHTTPClient

class WewallEstateSearchClient(interface.IWewallEstateSearchClient):
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
            prefix="/api/estate-search",
            use_tracing=True,
            logger=self.logger,
        )
        self.tracer = tel.tracer()

    async def find_rent_offer(
            self,
            type: int,
            budget: int,
            location: int,
            square: float,
            estate_class: int,
            distance_to_metro: int,
            design: int,
            readiness: int,
            irr: float,
    ) -> model.FindRentOfferResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateSearchClient.find_rent_offer",
                kind=SpanKind.CLIENT,
                attributes={
                    "type": type,
                    "budget": budget,
                    "location": location,
                    "square": square,
                    "estate_class": estate_class,
                    "distance_to_metro": distance_to_metro,
                    "design": design,
                    "readiness": readiness,
                    "irr": irr,
                }
        ) as span:
            try:
                body = {
                    "type": type,
                    "budget": budget,
                    "location": location,
                    "square": square,
                    "estate_class": estate_class,
                    "distance_to_metro": distance_to_metro,
                    "design": design,
                    "readiness": readiness,
                    "irr": irr,
                }
                response = await self.client.post("/rent", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error {response.status_code}: {json_response['message']}")

                span.set_status(Status(StatusCode.OK))
                return model.FindRentOfferResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err


    async def find_sale_offer(
            self,
            type: int,
            budget: int,
            location: int,
            square: float,
            estate_class: int,
            distance_to_metro: int,
            design: int,
            readiness: int,
            irr: float,
    ) -> model.FindSaleOfferResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateSearchClient.find_sale_offer",
                kind=SpanKind.CLIENT,
                attributes={
                    "type": type,
                    "budget": budget,
                    "location": location,
                    "square": square,
                    "estate_class": estate_class,
                    "distance_to_metro": distance_to_metro,
                    "design": design,
                    "readiness": readiness,
                    "irr": irr,
                }
        ) as span:
            try:
                body = {
                    "type": type,
                    "budget": budget,
                    "location": location,
                    "square": square,
                    "estate_class": estate_class,
                    "distance_to_metro": distance_to_metro,
                    "design": design,
                    "readiness": readiness,
                    "irr": irr,
                }

                response = await self.client.post("/sale", json=body)
                json_response = response.json()
                span.set_attribute("json_response", str(json_response))

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error {response.status_code}: {json_response['message']}")

                span.set_status(Status(StatusCode.OK))
                return model.FindSaleOfferResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err