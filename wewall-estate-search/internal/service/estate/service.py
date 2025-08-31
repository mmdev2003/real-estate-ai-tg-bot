from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface


class EstateService(interface.IEstateService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            estate_repo: interface.IEstateRepo,
    ):
        self.tracer = tel.tracer()
        self.estate_repo = estate_repo

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
                "EstateService.create_estate",
                kind=SpanKind.INTERNAL,
                attributes={
                    "link": link,
                    "name": name,
                    "category": category,
                    "address": address,
                    "coords": coords,
                    "metro_stations": metro_stations,
                }
        ) as span:
            try:
                estate_id = await self.estate_repo.create_estate(
                    link,
                    name,
                    category,
                    address,
                    coords,
                    metro_stations,
                )

                span.set_status(Status(StatusCode.OK))
                return estate_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise


    async def all_estate(self) -> list[model.Estate]:
        with self.tracer.start_as_current_span(
                "EstateService.all_estate",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                estates = await self.estate_repo.all_estate()

                span.set_status(Status(StatusCode.OK))
                return estates
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

