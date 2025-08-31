from typing import Protocol
from abc import abstractmethod

from internal import model

class IEstateService(Protocol):
    @abstractmethod
    async def create_estate(
            self,
            link: str,
            name: str,
            category: str,
            address: str,
            coords: model.Coords,
            metro_stations: list[model.MetroStation],
    ) -> int: pass

    @abstractmethod
    async def all_estate(self) -> list[model.Estate]: pass

class IEstateRepo(Protocol):
    @abstractmethod
    async def create_estate(
            self,
            link: str,
            name: str,
            category: str,
            address: str,
            coords: model.Coords,
            metro_stations: list[model.MetroStation],
    ) -> int: pass

    @abstractmethod
    async def estate_by_id(self, estate_id: int) -> list[model.Estate]: pass

    @abstractmethod
    async def all_estate(self) -> list[model.Estate]: pass
