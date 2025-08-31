from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface, common

from pkg.client.client import AsyncHTTPClient


class WewallEstateCalculatorClient(interface.IWewallEstateCalculatorClient):
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
            prefix="/api/estate-calculator",
            use_tracing=True,
            logger=self.logger,
        )
        self.tracer = tel.tracer()

    async def calc_finance_model_finished_office(
            self,
            square: float,
            price_per_meter: float,
            need_repairs: int,
            estate_category: str,
            metro_station_name: str,
            distance_to_metro: float,
            nds_rate: int,
    ) -> model.FinanceModelResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_finished_office",
                kind=SpanKind.CLIENT,
                attributes={
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "need_repairs": need_repairs,
                    "estate_category": estate_category,
                    "metro_station_name": metro_station_name,
                    "distance_to_metro": distance_to_metro,
                    "nds_rate": nds_rate,
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "need_repairs": need_repairs,
                    "metro_station_name": metro_station_name,
                    "estate_category": estate_category,
                    "distance_to_metro": distance_to_metro,
                    "nds_rate": nds_rate,
                }
                response = await self.client.post("/finished/office", json=body)
                json_response = response.json()

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return model.FinanceModelResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    async def calc_finance_model_finished_retail(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
    ) -> model.FinanceModelResponse:
        with self.tracer.start_as_current_span(
                "WewallEstateCalculatorClient.calc_finance_model_finished_retail",
                kind=SpanKind.CLIENT,
                attributes={
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                }
        ) as span:
            try:
                body = {
                    "square": square,
                    "price_per_meter": price_per_meter,
                    "m_a_p": m_a_p,
                    "nds_rate": nds_rate,
                    "need_repairs": need_repairs,
                }
                response = await self.client.post("/finished/retail", json=body)
                json_response = response.json()

                if response.status_code >= 500:
                    raise Exception("Internal Server Error")
                if response.status_code >= 400:
                    raise Exception(f"Client error: {response.status_code}")

                span.set_status(Status(StatusCode.OK))
                return model.FinanceModelResponse(**json_response)
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
