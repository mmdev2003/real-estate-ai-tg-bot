import io
from abc import abstractmethod
from typing import Protocol
from internal.controller.http.handler.estate_calculator.model import *


class IEstateCalculatorController(Protocol):
    @abstractmethod
    async def calc_finance_model_finished_office(self, body: FinishedOfficeFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_finished_retail(self, body: FinishedRetailFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_building_office(self, body: BuildingOfficeFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_building_retail(self, body: BuildingRetailFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_finished_office_table(self, body: FinishedOfficeFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_finished_retail_table(self, body: FinishedRetailFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_building_office_table(self, body: BuildingOfficeFinanceModelBody): pass

    @abstractmethod
    async def calc_finance_model_building_retail_table(self, body: BuildingRetailFinanceModelBody): pass


class IEstateCalculator(Protocol):
    @abstractmethod
    async def calc_finance_model_finished_office(
            self,
            square: float,
            price_per_meter: float,
            need_repairs: int,
            metro_station_name: str,
            estate_category: str,
            distance_to_metro: float,
            nds_rate: int,
            create_xlsx: bool = False,
    ) -> dict | io.BytesIO: pass

    @abstractmethod
    async def calc_finance_model_finished_retail(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
            create_xlsx: bool = False,
    ) -> dict | io.BytesIO: pass

    @abstractmethod
    async def calc_finance_model_building_office(
            self,
            square: float,
            price_per_meter: float,
            distance_to_metro: float,
            metro_station_name: str,
            estate_category: str,
            project_readiness: str,
            nds_rate: int,
            transaction_dict: dict,
            create_xlsx: bool = False,
    ) -> dict | io.BytesIO: pass

    @abstractmethod
    async def calc_finance_model_building_retail(
            self,
            square: float,
            price_per_meter: float,
            transaction_dict: dict,
            price_rva: float,
            m_a_p: float,
            nds_rate: int,
            project_readiness: str,
            need_repairs: int,
            create_xlsx: bool = False,
    ) -> dict | io.BytesIO: pass
