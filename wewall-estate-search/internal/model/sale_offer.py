from datetime import datetime
from dataclasses import dataclass


@dataclass
class SaleOffer:
    id: int
    estate_id: int

    link: str
    name: str
    square: float
    price: int
    price_per_meter: int
    design: int
    floor: int
    type: int
    location: str
    image_urls: list[str]
    irr: float
    offer_readiness: int
    readiness_date: str
    description: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                estate_id=row.estate_id,
                link=row.link,
                name=row.name,
                square=row.square,
                price=row.price,
                price_per_meter=row.price_per_meter,
                design=row.design,
                floor=row.floor,
                type=row.type,
                location=row.location,
                image_urls=row.image_urls,
                irr=row.irr,
                offer_readiness=row.offer_readiness,
                readiness_date=row.readiness_date,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
