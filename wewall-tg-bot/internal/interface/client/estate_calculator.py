from abc import abstractmethod
from typing import Protocol

from aiogram.types import BufferedInputFile

from internal import model


class IWewallEstateCalculatorClient(Protocol):
    @abstractmethod
    async def calc_finance_model_finished_office(
            self,
            square: float,
            price_per_meter: float,
            need_repairs: int,
            estate_category: str,
            metro_station_name: str,
            distance_to_metro: float,
            nds_rate: int,
    ) -> model.FinanceModelResponse: pass

    @abstractmethod
    async def calc_finance_model_finished_office_table(
            self,
            square: float,
            price_per_meter: float,
            need_repairs: int,
            estate_category: str,
            metro_station_name: str,
            distance_to_metro: float,
            nds_rate: int,
    ) -> BufferedInputFile: pass

    @abstractmethod
    async def calc_finance_model_finished_retail(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
    ) -> model.FinanceModelResponse: pass

    @abstractmethod
    async def calc_finance_model_finished_retail_table(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
    ) -> BufferedInputFile: pass

    @abstractmethod
    async def calc_finance_model_building_office(
            self,
            project_readiness: str,
            square: float,
            metro_station_name: str,
            distance_to_metro: float,
            estate_category: str,
            price_per_meter: float,
            nds_rate: int,
            transaction_dict: dict,
    ) -> model.FinanceModelResponse: pass

    @abstractmethod
    async def calc_finance_model_building_office_table(
            self,
            project_readiness: str,
            square: float,
            metro_station_name: str,
            distance_to_metro: float,
            estate_category: str,
            price_per_meter: float,
            nds_rate: int,
            transaction_dict: dict,
    ) -> BufferedInputFile: pass

    @abstractmethod
    async def calc_finance_model_building_retail(
            self,
            project_readiness: str,
            square: float,
            price_rva: float,
            m_a_p: float,
            price_per_meter: float,
            nds_rate: int,
            need_repairs: int,
            transaction_dict: dict,
    ) -> model.FinanceModelResponse: pass

    @abstractmethod
    async def calc_finance_model_building_retail_table(
            self,
            project_readiness: str,
            square: float,
            price_rva: float,
            m_a_p: float,
            price_per_meter: float,
            nds_rate: int,
            need_repairs: int,
            transaction_dict: dict,
    ) -> BufferedInputFile: pass

    @abstractmethod
    async def generate_pdf(
            self,
            estate_type: str,
            buying_property: float,
            sale_property: float,
            income_tax: float,
            property_tax: float,
            price_of_finishing: float,
            rent_flow: float,
            terminal_value: float,
            sale_income: float,
            rent_income: float,
            added_value: float,
            rent_irr: float,
            sale_irr: float,
    ) -> BufferedInputFile: pass
