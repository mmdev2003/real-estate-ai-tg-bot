from datetime import datetime
from dataclasses import dataclass


@dataclass
class Coords:
    lat: float
    lon: float

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon
        }


@dataclass
class MetroStation:
    name: str
    time_leg: int
    time_car: int
    leg_distance: int
    car_distance: int

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "time_leg": self.time_leg,
            "time_car": self.time_car,
            "leg_distance": self.leg_distance,
            "car_distance": self.car_distance
        }


@dataclass
class Estate:
    id: int

    link: str
    name: str
    category: str
    address: str
    metro_stations: list[MetroStation]
    coords: Coords

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                link=row.link,
                name=row.name,
                category=row.category,
                address=row.address,
                metro_stations=[MetroStation(**metro_station_dict) for metro_station_dict in
                                row.metro_stations],
                coords=Coords(**row.coords),
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
