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
class Offer:
    estate_id: int
    estate_name: str
    estate_category: str
    estate_address: str
    estate_coords: Coords
    metro_stations: list[MetroStation]

    link: str
    name: str
    square: float
    design: int
    floor: int
    type: int
    image_urls: list[str]
    offer_readiness: int
    readiness_date: str
    description: str

    def __init__(self, offer_dict: dict):
        self.estate_id = offer_dict["estate_id"]
        self.estate_name = offer_dict["estate_name"]
        self.estate_category = offer_dict["estate_category"]
        self.estate_address = offer_dict["estate_address"]
        self.estate_coords = Coords(**offer_dict['estate_coords'])
        self.metro_stations = [MetroStation(**metro) for metro in offer_dict['metro_stations']]

        self.link = offer_dict['link']
        self.name = offer_dict['name']
        self.square = offer_dict['square']
        self.design = offer_dict['design']
        self.floor = offer_dict['floor']
        self.type = offer_dict['type']
        self.image_urls = offer_dict['image_urls']
        self.offer_readiness = offer_dict['offer_readiness']
        self.readiness_date = offer_dict['readiness_date']
        self.description = offer_dict['description']

@dataclass
class SaleOffer(Offer):
    price: int
    price_per_meter: int

    def __init__(self, offer_dict: dict):
        super().__init__(offer_dict)
        self.price = offer_dict['price']
        self.price_per_meter = offer_dict['price_per_meter']

    def to_dict(self) -> dict:
        return {
            "estate_id": self.estate_id,
            "estate_name": self.estate_name,
            "estate_category": self.estate_category,
            "estate_address": self.estate_address,
            "estate_coords": self.estate_coords.to_dict(),
            "metro_stations": [metro.to_dict() for metro in self.metro_stations],
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
            "description": self.description
        }


@dataclass
class RentOffer(Offer):
    price_per_month: int

    def __init__(self, offer_dict: dict):
        super().__init__(offer_dict)
        self.price_per_month = offer_dict['price_per_month']

    def to_dict(self) -> dict:
        return {
            "estate_id": self.estate_id,
            "estate_name": self.estate_name,
            "estate_category": self.estate_category,
            "estate_address": self.estate_address,
            "estate_coords": self.estate_coords.to_dict(),
            "metro_stations": [metro.to_dict() for metro in self.metro_stations],
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
            "description": self.description
        }


@dataclass
class FindRentOfferResponse:
    rent_offers: list[RentOffer]

    def __init__(self, rent_offers: list[dict]):
        rent_offers = self.normalize_estate_id(rent_offers)
        rent_offers = self.sort_by_estate_id(rent_offers)
        _rent_offers = []
        for rent_offer in rent_offers:
            _rent_offers.append(RentOffer(rent_offer))

        self.rent_offers = _rent_offers

    def normalize_estate_id(self, rent_offers: list[dict]) -> list[dict]:
        unique_estate_ids = {offer["estate_id"] for offer in rent_offers}
        for offer in rent_offers:
            for idx, estate_id in enumerate(unique_estate_ids):
                if offer["estate_id"] == estate_id:
                    offer["estate_id"] = idx

        return rent_offers

    def sort_by_estate_id(self, rent_offers: list[dict]) -> list[dict]:
        return sorted(rent_offers, key=lambda x: x["estate_id"])


@dataclass
class FindSaleOfferResponse:
    sale_offers: list[SaleOffer]

    def __init__(self, sale_offers: list[dict]):
        sale_offers = self.normalize_estate_id(sale_offers)
        sale_offers = self.sort_by_estate_id(sale_offers)
        _sale_offers = []
        for sale_offer in sale_offers:
            _sale_offers.append(SaleOffer(sale_offer))

        self.sale_offers = _sale_offers

    def normalize_estate_id(self, sale_offers: list[dict]) -> list[dict]:
        unique_estate_ids = {offer["estate_id"] for offer in sale_offers}
        for offer in sale_offers:
            for idx, estate_id in enumerate(unique_estate_ids):
                if offer["estate_id"] == estate_id:
                    offer["estate_id"] = idx

        return sale_offers

    def sort_by_estate_id(self, sale_offers: list[dict]) -> list[dict]:
        return sorted(sale_offers, key=lambda x: x["estate_id"])
