from typing import Protocol
from abc import abstractmethod

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
    async def calc_finance_model_finished_retail(
            self,
            square: float,
            price_per_meter: float,
            m_a_p: float,
            nds_rate: int,
            need_repairs: int,
    ) -> model.FinanceModelResponse: pass
