from typing import Protocol, Sequence, Any
from abc import abstractmethod

from internal.controller.http.handler.sale_offer.model import *
from internal import model


class ISaleOfferController(Protocol):
    @abstractmethod
    async def estate_search_sale(self, body: EstateSearchSaleBody): pass

class ISaleOfferService(Protocol):
    @abstractmethod
    async def create_sale_offer(
            self,
            estate_id: int,
            link: str,
            name: str,
            square: float,
            price: int,
            price_per_meter: int,
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
    async def calc_sale_offer_irr(self, sale_offer: model.SaleOffer) -> None: pass

    @abstractmethod
    async def find_sale_offers(
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
    ) -> list[model.SaleOfferDTO]: pass


class ISaleOfferRepo(Protocol):
    @abstractmethod
    async def create_sale_offer(
            self,
            estate_id: int,
            link: str,
            name: str,
            square: float,
            price: int,
            price_per_meter: int,
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
    async def update_sale_offer_irr(self, sale_offer_id: int, irr: float) -> None: pass

    @abstractmethod
    async def sale_offer_by_id(self, sale_offer_id: int) -> list[model.SaleOffer]: pass

    @abstractmethod
    async def all_sale_offer(self) -> list[model.SaleOffer]: pass
