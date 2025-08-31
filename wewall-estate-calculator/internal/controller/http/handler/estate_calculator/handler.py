from fastapi.responses import Response, JSONResponse
from fastapi import status
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import common

from .model import *


class EstateCalculatorController(interface.IEstateCalculatorController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            estate_calculator: interface.IEstateCalculator,
    ):
        self.tracer = tel.tracer()
        self.estate_calculator = estate_calculator

    async def calc_finance_model_finished_office(self, body: FinishedOfficeFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_finished_office",
                kind=SpanKind.INTERNAL,
                attributes={
                    "square": body.square,
                    "price_per_meter": body.price_per_meter,
                    "need_repairs": body.need_repairs,
                    "metro_station_name": body.metro_station_name,
                    "estate_category": body.estate_category,
                    "distance_to_metro": body.distance_to_metro,
                    "nds_rate": body.nds_rate
                }
        ) as span:
            try:
                finance_model = await self.estate_calculator.calc_finance_model_finished_office(**body.model_dump())

                response = FinanceModelResponse(**finance_model)
                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )

            except common.MetroStationNotFound as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": str(err), "error_code": 4041},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def calc_finance_model_finished_retail(self, body: FinishedRetailFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_finished_retail",
                kind=SpanKind.INTERNAL,
                attributes={
                    "square": body.square,
                    "price_per_meter": body.price_per_meter,
                    "m_a_p": body.m_a_p,
                    "nds_rate": body.nds_rate,
                    "need_repairs": body.need_repairs
                }
        ) as span:
            try:
                finance_model = await self.estate_calculator.calc_finance_model_finished_retail(**body.model_dump())

                response = FinanceModelResponse(**finance_model)
                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def calc_finance_model_building_office(self, body: BuildingOfficeFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_building_office",
                kind=SpanKind.INTERNAL,
                attributes={
                    "project_readiness": body.project_readiness,
                    "square": body.square,
                    "metro_station_name": body.metro_station_name,
                    "distance_to_metro": body.distance_to_metro,
                    "estate_category": body.estate_category,
                    "price_per_meter": body.price_per_meter,
                    "nds_rate": body.nds_rate,
                    "transaction_dict": body.transaction_dict
                }
        ) as span:
            try:
                finance_model = await self.estate_calculator.calc_finance_model_building_office(**body.model_dump())

                response = FinanceModelResponse(**finance_model)
                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except common.MetroStationNotFound as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": str(err), "error_code": 4041},
                )
            except common.TransactionDictSumNotEqual100 as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": str(err), "error_code": 4001},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def calc_finance_model_building_retail(self, body: BuildingRetailFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_building_retail",
                kind=SpanKind.INTERNAL,
                attributes={
                    "square": body.square,
                    "price_per_meter": body.price_per_meter,
                    "transaction_dict": body.transaction_dict,
                    "price_rva": body.price_rva,
                    "m_a_p": body.m_a_p,
                    "nds_rate": body.nds_rate,
                    "project_readiness": body.project_readiness,
                    "need_repairs": body.need_repairs
                }
        ) as span:
            try:
                finance_model = await self.estate_calculator.calc_finance_model_building_retail(**body.model_dump())

                response = FinanceModelResponse(**finance_model)
                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except common.TransactionDictSumNotEqual100 as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": str(err), "error_code": 4001},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def calc_finance_model_finished_office_table(self, body: FinishedOfficeFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_finished_office_table",
                kind=SpanKind.INTERNAL,
                attributes={
                    "square": body.square,
                    "price_per_meter": body.price_per_meter,
                    "need_repairs": body.need_repairs,
                    "metro_station_name": body.metro_station_name,
                    "estate_category": body.estate_category,
                    "distance_to_metro": body.distance_to_metro,
                    "nds_rate": body.nds_rate
                }
        ) as span:
            try:
                finance_model_xlsx = await self.estate_calculator.calc_finance_model_finished_office(
                    **body.model_dump(),
                    create_xlsx=True
                )

                span.set_status(Status(StatusCode.OK))
                return Response(
                    content=finance_model_xlsx.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=finance_model.xlsx"}
                )
            except common.MetroStationNotFound as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": str(err), "error_code": 4041},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def calc_finance_model_finished_retail_table(self, body: FinishedRetailFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_finished_retail_table",
                kind=SpanKind.INTERNAL,
                attributes={
                    "square": body.square,
                    "price_per_meter": body.price_per_meter,
                    "m_a_p": body.m_a_p,
                    "nds_rate": body.nds_rate,
                    "need_repairs": body.need_repairs
                }
        ) as span:
            try:
                finance_model_xlsx = await self.estate_calculator.calc_finance_model_finished_retail(
                    **body.model_dump(),
                    create_xlsx=True
                )

                span.set_status(Status(StatusCode.OK))
                return Response(
                    content=finance_model_xlsx.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=finance_model.xlsx"}
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err


    async def calc_finance_model_building_office_table(self, body: BuildingOfficeFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_building_office_table",
                kind=SpanKind.INTERNAL,
                attributes={
                    "project_readiness": body.project_readiness,
                    "square": body.square,
                    "metro_station_name": body.metro_station_name,
                    "distance_to_metro": body.distance_to_metro,
                    "estate_category": body.estate_category,
                    "price_per_meter": body.price_per_meter,
                    "nds_rate": body.nds_rate,
                    "transaction_dict": body.transaction_dict
                }
        ) as span:
            try:
                finance_model_xlsx = await self.estate_calculator.calc_finance_model_building_office(
                    **body.model_dump(),
                    create_xlsx=True
                )

                span.set_status(Status(StatusCode.OK))
                return Response(content=finance_model_xlsx.getvalue())
            except common.MetroStationNotFound as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": str(err), "error_code": 4041},
                )
            except common.TransactionDictSumNotEqual100 as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": str(err), "error_code": 4001},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err


    async def calc_finance_model_building_retail_table(self, body: BuildingRetailFinanceModelBody):
        with self.tracer.start_as_current_span(
                "EstateCalculatorController.calc_finance_model_building_retail_table",
                kind=SpanKind.INTERNAL,
                attributes={
                    "square": body.square,
                    "price_per_meter": body.price_per_meter,
                    "transaction_dict": body.transaction_dict,
                    "price_rva": body.price_rva,
                    "m_a_p": body.m_a_p,
                    "nds_rate": body.nds_rate,
                    "project_readiness": body.project_readiness,
                    "need_repairs": body.need_repairs
                }
        ) as span:
            try:
                finance_model_xlsx = await self.estate_calculator.calc_finance_model_building_retail(
                    **body.model_dump(),
                    create_xlsx=True
                )

                span.set_status(Status(StatusCode.OK))
                return Response(content=finance_model_xlsx.getvalue())
            except common.TransactionDictSumNotEqual100 as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": str(err), "error_code": 4001},
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
