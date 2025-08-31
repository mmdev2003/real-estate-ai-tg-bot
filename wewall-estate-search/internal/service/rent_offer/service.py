import geopandas as gpd
from shapely.geometry import Point
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface


class RentOfferService(interface.IRentOfferService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            estate_repo: interface.IEstateRepo,
            rent_offer_repo: interface.IRentOfferRepo,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.estate_repo = estate_repo
        self.rent_offer_repo = rent_offer_repo

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
    ) -> int:
        with self.tracer.start_as_current_span(
                "RentOfferService.create_rent_offer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "estate_id": estate_id,
                    "link": link,
                    "name": name,
                    "square": square,
                    "price_per_month": price_per_month,
                    "design": design,
                    "floor": floor,
                    "type": type,
                    "location": location,
                    "image_urls": image_urls,
                    "offer_readiness": offer_readiness,
                    "readiness_date": readiness_date,
                    "description": description,
                }
        ) as span:
            try:
                rent_offer_id = await self.rent_offer_repo.create_rent_offer(
                    estate_id,
                    link,
                    name,
                    square,
                    price_per_month,
                    design,
                    floor,
                    type,
                    location,
                    image_urls,
                    offer_readiness,
                    readiness_date,
                    description,
                )

                span.set_status(Status(StatusCode.OK))
                return rent_offer_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

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
    ) -> list[model.RentOfferDTO]:
        with self.tracer.start_as_current_span(
                "RentOfferService.find_rent_offers",
                kind=SpanKind.INTERNAL,
                attributes={
                    "type": type,
                    "budget": budget,
                    "location": location,
                    "square": square,
                    "estate_class": estate_class,
                    "distance_to_metro": distance_to_metro,
                    "design": design,
                    "readiness": readiness,
                    "irr": irr,
                }
        ) as span:
            try:
                rent_offers = await self.rent_offer_repo.all_rent_offer()
                estates = await self.estate_repo.all_estate()
                filtered_rent_offers = self.__filter_offers(
                    rent_offers,
                    estates,
                    type,
                    budget,
                    location,
                    square,
                    estate_class,
                    distance_to_metro,
                    design,
                    readiness,
                    irr
                )
                self.logger.debug("Получили отфильтрованные rent_offers")

                if len(filtered_rent_offers) > 8:
                    self.logger.debug("Получили больше 8 filtered_rent_offers")
                    filtered_rent_offers = filtered_rent_offers[:8]

                rent_offers_dto = []
                for filtered_rent_offer in filtered_rent_offers:
                    estate = await self.estate_repo.estate_by_id(filtered_rent_offer.estate_id)
                    rent_offer = await self.rent_offer_repo.rent_offer_by_id(filtered_rent_offer.id)

                    rent_offer = rent_offer[0]
                    estate = estate[0]
                    rent_offers_dto.append(
                        model.RentOfferDTO(
                            estate_id=estate.id,
                            estate_name=estate.name,
                            estate_category=estate.category,
                            estate_address=estate.address,
                            estate_coords=estate.coords,
                            metro_stations=estate.metro_stations,
                            link=rent_offer.link,
                            name=rent_offer.name,
                            square=rent_offer.square,
                            price_per_month=rent_offer.price_per_month,
                            design=rent_offer.design,
                            floor=rent_offer.floor,
                            type=rent_offer.type,
                            image_urls=rent_offer.image_urls,
                            offer_readiness=rent_offer.offer_readiness,
                            readiness_date=rent_offer.readiness_date,
                            description=rent_offer.description
                        )
                    )

                span.set_status(Status(StatusCode.OK))
                return rent_offers_dto
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def __filter_offers(
            self,
            rent_offers: list[model.RentOffer],
            estates: list[model.Estate],
            type: int,
            budget: int,
            location: int,
            square: float,
            estate_class: int,
            distance_to_metro: int,
            design: int,
            readiness: int,
            irr: float
    ) -> list[model.RentOffer]:
        with self.tracer.start_as_current_span(
                "RentOfferService.__filter_offers",
                kind=SpanKind.INTERNAL,
                attributes={
                    "type": type,
                    "budget": budget,
                    "location": location,
                    "square": square,
                    "estate_class": estate_class,
                    "distance_to_metro": distance_to_metro,
                    "design": design,
                    "readiness": readiness,
                    "irr": irr
                }
        ) as span:
            try:
                if location not in [1, 2]:
                    location = 0

                if location == 0:
                    filtered_rent_offers = [
                        rent_offer
                        for rent_offer in rent_offers
                        if self.__filter_square(rent_offer.square, square)
                           and self.__filter_type(rent_offer.type, type)
                           and self.__filter_type(rent_offer.type, type)
                           and self.__filter_price(rent_offer.price_per_month, budget)
                           and self.__filter_square(rent_offer.square, square)
                           and self.__filter_estate_class(estates, rent_offer.estate_id, estate_class)
                           and self.__filter_distance_to_metro(estates, rent_offer.estate_id, distance_to_metro)
                           and self.__filter_design(rent_offer.design, design)
                           and self.__filter_readiness(rent_offer.offer_readiness, readiness)
                    ]
                else:
                    filtered_rent_offers = [
                        rent_offer
                        for rent_offer in rent_offers
                        if self.__filter_location(rent_offer.location, location)
                           and self.__filter_type(rent_offer.type, type)
                           and self.__filter_square(rent_offer.square, square)
                           and self.__filter_price(rent_offer.price_per_month, budget)
                           and self.__filter_square(rent_offer.square, square)
                           and self.__filter_estate_class(estates, rent_offer.estate_id, estate_class)
                           and self.__filter_distance_to_metro(estates, rent_offer.estate_id, distance_to_metro)
                           and self.__filter_design(rent_offer.design, design)
                           and self.__filter_readiness(rent_offer.offer_readiness, readiness)
                    ]

                span.set_status(Status(StatusCode.OK))
                return filtered_rent_offers
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise

    def __filter_location(self, rent_offer_location: str, location: int) -> bool:
        if location == 1 and rent_offer_location == "ТТК":
            return True
        elif location == 2 and rent_offer_location == "МКАД":
            return True
        elif location == 0:
            return True
        else:
            return False

    def __filter_estate_class(self, estates: list[model.Estate], estate_id: int, estate_class: int) -> bool:
        if estate_class == 0:
            return True
        else:
            estate = [estate for estate in estates if estate.id == estate_id][0]
            if estate.category == 'A' and estate_class == 1:
                return True
            elif estate.category == 'B' and estate_class == 2:
                return True
            else:
                return False

    def __filter_type(self, sale_offer_type: int, type: int) -> bool:
        if type == 0:
            return True
        else:
            return sale_offer_type == type - 1


    def __filter_distance_to_metro(self, estates: list[model.Estate], estate_id: int, distance_to_metro: int) -> bool:
        if distance_to_metro == 0:
            return True
        else:
            estate = [estate for estate in estates if estate.id == estate_id][0]
            return estate.metro_stations[0].leg_distance <= distance_to_metro

    def __filter_design(self, sale_offer_design: int, design: int) -> bool:
        if design == 0:
            return True
        else:
            return sale_offer_design == design

    def __filter_readiness(self, sale_offer_readiness: int, readiness: int) -> bool:
        if readiness == 0:
            return True
        else:
            return sale_offer_readiness == readiness

    def __filter_price(self, sale_offer_price: int, price: int) -> bool:
        if sale_offer_price == 0:
            return False
        if price == 0:
            return True
        if sale_offer_price > price:
            return (sale_offer_price / price - 1) <= 0.10
        return True

    def __filter_square(self, sale_offer_square: float, square: float) -> bool:
        if sale_offer_square == 0:
            return False
        if square == 0:
            return True
        if sale_offer_square < square:
            return (square - sale_offer_square) / square <= 0.10
        return True

    def __filter_irr(self, sale_offer_irr: float, irr: float) -> bool:
        if irr == 0:
            return True
        result = irr <= sale_offer_irr

        return result
