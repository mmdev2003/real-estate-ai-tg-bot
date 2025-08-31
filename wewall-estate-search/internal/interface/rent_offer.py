from typing import Protocol
from abc import abstractmethod

from internal.controller.http.handler.rent_offer.model import *
from internal import model

class IRentOfferController(Protocol):
    @abstractmethod
    async def estate_search_rent(self, body: EstateSearchRentBody): pass

class IRentOfferService(Protocol):
    @abstractmethod
    async def create_rent_offer(
            self,
            estate_id: int,
            link: str,
            name: str,
            square: float,
            price_per_month: int,
            design: int,
            floor: int,
            type: int,
            location: str,
            image_urls: list[str],
            offer_readiness: int,
            readiness_date: str,
            description: str
    ) -> int: pass

    @abstractmethod
    async def find_rent_offers(
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
    ) -> list[model.RentOfferDTO]: pass

class IRentOfferRepo(Protocol):
    @abstractmethod
    async def create_rent_offer(
            self,
            estate_id: int,
            link: str,
            name: str,
            square: float,
            price_per_month: int,
            design: int,
            floor: int,
            type: int,
            location: str,
            image_urls: list[str],
            offer_readiness: int,
            readiness_date: str,
            description: str
    ) -> int: pass

    @abstractmethod
    async def rent_offer_by_id(self, rent_offer_id: int) -> list[model.RentOffer]: pass

    @abstractmethod
    async def all_rent_offer(self) -> list[model.RentOffer]: pass

