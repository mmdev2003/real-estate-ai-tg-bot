from abc import abstractmethod
from typing import Protocol

from internal import model


class IMetroRepo(Protocol):
    @abstractmethod
    async def create_metro_station(
            self,
            name: str,
            price_A: int,
            price_B: int,
            rent_A: int,
            rent_B: int,
            average_cadastral_value: int,
    ) -> int: pass

    @abstractmethod
    async def create_metro_distance_coeff(
            self,
            min_distance: int,
            max_distance: int,
            coeff: float,
    ) -> int: pass

    @abstractmethod
    async def create_square_coeff(
            self,
            min_square: int,
            max_square: int,
            coeff: float
    ) -> int: pass

    @abstractmethod
    async def metro_station_by_name(self, name: str) -> list[model.MetroStation]: pass

    @abstractmethod
    async def all_metro_distance_coeff(self) -> list[model.MetroDistanceCoeff]: pass

    @abstractmethod
    async def all_square_coeff(self) -> list[model.SquareCoeff]: pass
