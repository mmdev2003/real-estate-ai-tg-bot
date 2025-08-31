from dataclasses import dataclass
from internal.model.estate import Coords, MetroStation



@dataclass
class RentOfferDTO:
    estate_id: int
    estate_name: str
    estate_category: str
    estate_address: str
    estate_coords: Coords
    metro_stations: list[MetroStation]

    link: str
    name: str
    square: float
    price_per_month: int
    design: int
    floor: int
    type: int
    image_urls: list[str]
    offer_readiness: int
    readiness_date: str
    description: str

    def to_dict(self) -> dict:
        return {
            "estate_id": self.estate_id,
            "estate_name": self.estate_name,
            "estate_category": self.estate_category,
            "estate_address": self.estate_address,
            "estate_coords": self.estate_coords.to_dict(),
            "metro_stations": [metro_station.to_dict() for metro_station in self.metro_stations],
            "link": self.link,
            "name": self.name,
            "square": self.square,
            "price_per_month": self.price_per_month,
            "design": self.design,
            "floor": self.floor,
            "type": self.type,
            "image_urls": self.image_urls,
            "offer_readiness": self.offer_readiness,
            "readiness_date": self.readiness_date,
            "description": self.description,
        }


@dataclass
class SaleOfferDTO:
    estate_id: int
    estate_name: str
    estate_category: str
    estate_address: str
    estate_coords: Coords
    metro_stations: list[MetroStation]

    link: str
    name: str
    square: float
    price: int
    price_per_meter: int
    design: int
    floor: int
    type: int
    image_urls: list[str]
    offer_readiness: int
    readiness_date: str
    description: str

    def to_dict(self) -> dict:
        return {
            "estate_id": self.estate_id,
            "estate_name": self.estate_name,
            "estate_category": self.estate_category,
            "estate_address": self.estate_address,
            "estate_coords": self.estate_coords.to_dict(),
            "metro_stations": [metro_station.to_dict() for metro_station in self.metro_stations],
            "link": self.link,
            "name": self.name,
            "square": self.square,
            "price": self.price,
            "price_per_meter": self.price_per_meter,
            "design": self.design,
            "floor": self.floor,
            "type": self.type,
            "image_urls": self.image_urls,
            "offer_readiness": self.offer_readiness,
            "readiness_date": self.readiness_date,
            "description": self.description,
        }
