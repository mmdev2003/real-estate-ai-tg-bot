from datetime import datetime
from dataclasses import dataclass


@dataclass
class RentOffer:
    id: int
    estate_id: int

    link: str
    name: str
    square: float
    price_per_month: int
    design: int
    floor: int
    type: int
    location: str
    image_urls: list[str]
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
                price_per_month=row.price_per_month,
                design=row.design,
                floor=row.floor,
                type=row.type,
                location=row.location,
                image_urls=row.image_urls,
                offer_readiness=row.offer_readiness,
                readiness_date=row.readiness_date,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
