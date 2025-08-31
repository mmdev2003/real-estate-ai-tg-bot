from dataclasses import dataclass
from internal.model.estate import Coords, MetroStation


@dataclass
class ParsedSaleOffer:
    link: str
    name: str
    square: float
    floor: int
    design: int
    type: int
    price: int
    price_per_meter: int
    location: str
    image_urls: list[str]
    offer_readiness: int
    readiness_date: str
    description: str


@dataclass
class ParsedRentOffer:
    link: str
    name: str
    square: float
    floor: int
    design: int
    type: int
    price_per_month: int
    location: str
    image_urls: list[str]
    offer_readiness: int
    readiness_date: str
    description: str

@dataclass
class ParsedEstate:
    link: str
    name: str
    address: str
    category: str

    coords: Coords
    metro_stations: list[MetroStation]

    rent_offers: list[ParsedRentOffer]
    sale_offers: list[ParsedSaleOffer]
