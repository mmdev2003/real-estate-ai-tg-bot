from datetime import datetime
from dataclasses import dataclass


@dataclass
class MetroDistanceCoeff:
    id: int
    min_distance: int
    max_distance: int
    coeff: float

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                min_distance=row.min_distance,
                max_distance=row.max_distance,
                coeff=row.coeff,
                created_at=row.created_at,
            )
            for row in rows
        ]


@dataclass
class SquareCoeff:
    id: int
    min_square: int
    max_square: int
    coeff: float

    created_at: datetime
    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                min_square=row.min_square,
                max_square=row.max_square,
                coeff=row.coeff,
                created_at=row.created_at,
            )
            for row in rows
        ]

@dataclass
class MetroStation:
    id: int
    name: str
    price_a: int
    price_b: int
    rent_a: int
    rent_b: int
    average_cadastral_value: int

    created_at: datetime
    updated_at: datetime
    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                name=row.name,
                price_a=row.price_a,
                price_b=row.price_b,
                rent_a=row.rent_a,
                rent_b=row.rent_b,
                average_cadastral_value=row.average_cadastral_value,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price_a": self.price_a,
            "price_b": self.price_b,
            "rent_a": self.rent_a,
            "rent_b": self.rent_b,
            "average_cadastral_value": self.average_cadastral_value
        }