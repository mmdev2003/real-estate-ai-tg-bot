from abc import abstractmethod
from typing import Protocol

from internal import model

class IWewallEstateSearchClient(Protocol):
    @abstractmethod
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
    ) -> model.FindRentOfferResponse: pass

    @abstractmethod
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
    ) -> model.FindSaleOfferResponse: pass