from datetime import datetime
from dataclasses import dataclass

from internal.model.client.estate_search import SaleOffer, RentOffer


@dataclass
class State:
    id: int
    tg_chat_id: int
    status: str
    is_transferred_to_manager: bool

    count_estate_search: int
    count_estate_calculator: int
    count_message: int

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                tg_chat_id=row.tg_chat_id,
                status=row.status,
                is_transferred_to_manager=row.is_transferred_to_manager,
                count_estate_search=row.count_estate_search,
                count_estate_calculator=row.count_estate_calculator,
                count_message=row.count_message,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class EstateSearchState:
    id: int
    state_id: int

    current_estate_id: int
    current_offer_id: int

    offers: list[SaleOffer | RentOffer]
    estate_search_params: dict

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                state_id=row.state_id,
                current_estate_id=row.current_estate_id,
                current_offer_id=row.current_offer_id,
                offers=[cls.define_offer_strategy(offer) for offer in row.offers],
                estate_search_params=row.estate_search_params,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    @classmethod
    def define_offer_strategy(cls, offer: dict) -> SaleOffer | RentOffer:
        if offer.get("price_per_meter") is not None:
            return SaleOffer(offer)
        else:
            return RentOffer(offer)
