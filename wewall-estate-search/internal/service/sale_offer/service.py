import geopandas as gpd
from shapely.geometry import Point
from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import model, interface


class SaleOfferService(interface.ISaleOfferService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            estate_repo: interface.IEstateRepo,
            sale_offer_repo: interface.ISaleOfferRepo,
            estate_calculator_client: interface.IWewallEstateCalculatorClient
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.estate_repo = estate_repo
        self.sale_offer_repo = sale_offer_repo
        self.estate_calculator_client = estate_calculator_client

        self.nds_rate = 0
        self.map_coeff = 120

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
    ) -> int:
        with self.tracer.start_as_current_span(
                "SaleOfferService.create_sale_offer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "estate_id": estate_id,
                    "link": link,
                    "name": name,
                    "square": square,
                    "price": price,
                    "price_per_meter": price_per_meter,
                    "design": design,
                    "floor": floor,
                    "type": type,
                    "location": location,
                    "image_urls": image_urls,
                    "offer_readiness": offer_readiness,
                    "readiness_date": readiness_date,
                    "description": description
                }
        ) as span:
            try:
                sale_offer_id = await self.sale_offer_repo.create_sale_offer(
                    estate_id,
                    link,
                    name,
                    square,
                    price,
                    price_per_meter,
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
                return sale_offer_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def calc_sale_offer_irr(self, sale_offer: model.SaleOffer) -> None:
        if sale_offer.irr != 0.0:
            return

        estate = (await self.estate_repo.estate_by_id(sale_offer.estate_id))[0]
        if sale_offer.type == 0:
            print("Рассчитываем доходность офис sale_offer", flush=True)
            try:
                nearest_metro = self.__nearest_metro(estate.metro_stations)
            except:
                print("Не смогли вычислить ближайшее метро", flush=True)

                return
            calc_resp = await self.estate_calculator_client.calc_finance_model_finished_office(
                sale_offer.square,
                sale_offer.price_per_meter,
                sale_offer.design,
                estate.category.replace('+', '').replace('C', 'B'),
                nearest_metro.name,
                nearest_metro.leg_distance,
                self.nds_rate,
            )
            await self.sale_offer_repo.update_sale_offer_irr(sale_offer.id, calc_resp.rent_irr)
        else:
            return

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
    ) -> list[model.SaleOfferDTO]:
        with self.tracer.start_as_current_span(
                "SaleOfferService.find_sale_offers",
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
                sale_offers = await self.sale_offer_repo.all_sale_offer()
                estates = await self.estate_repo.all_estate()

                filtered_sale_offers = self.__filter_offers(
                    sale_offers,
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
                self.logger.debug("Получили отфильтрованные sale_offers")

                if len(filtered_sale_offers) > 8:
                    self.logger.debug("Получили больше 8 filtered_sale_offers")
                    filtered_sale_offers = filtered_sale_offers[:8]

                sale_offers_dto = []
                for filtered_sale_offer in filtered_sale_offers:
                    estate = await self.estate_repo.estate_by_id(filtered_sale_offer.estate_id)
                    sale_offer = await self.sale_offer_repo.sale_offer_by_id(filtered_sale_offer.id)

                    sale_offer = sale_offer[0]
                    estate = estate[0]
                    sale_offers_dto.append(
                        model.SaleOfferDTO(
                            estate_id=estate.id,
                            estate_name=estate.name,
                            estate_category=estate.category,
                            estate_address=estate.address,
                            estate_coords=estate.coords,
                            metro_stations=estate.metro_stations,
                            link=sale_offer.link,
                            name=sale_offer.name,
                            square=sale_offer.square,
                            price=sale_offer.price,
                            price_per_meter=sale_offer.price_per_meter,
                            design=sale_offer.design,
                            floor=sale_offer.floor,
                            type=sale_offer.type,
                            image_urls=sale_offer.image_urls,
                            offer_readiness=sale_offer.offer_readiness,
                            readiness_date=sale_offer.readiness_date,
                            description=sale_offer.description
                        )
                    )

                span.set_status(Status(StatusCode.OK))
                return sale_offers_dto
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def __filter_offers(
            self,
            sale_offers: list[model.SaleOffer],
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
    ) -> list[model.SaleOffer]:
        with self.tracer.start_as_current_span(
                "SaleOfferService.__filter_offers",
                kind=SpanKind.INTERNAL,
                attributes={
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
                    filtered_sale_offers = [
                        sale_offer
                        for sale_offer in sale_offers
                        if self.__filter_price(sale_offer.price, budget)
                           and self.__filter_type(sale_offer.type, type)
                           and self.__filter_square(sale_offer.square, square)
                           and self.__filter_estate_class(estates, sale_offer.estate_id, estate_class)
                           and self.__filter_distance_to_metro(estates, sale_offer.estate_id, distance_to_metro)
                           and self.__filter_design(sale_offer.design, design)
                           and self.__filter_readiness(sale_offer.offer_readiness, readiness)
                           and self.__filter_irr(sale_offer.irr, irr)
                    ]
                else:
                    filtered_sale_offers = [
                        sale_offer
                        for sale_offer in sale_offers
                        if self.__filter_location(sale_offer.location, location)
                           and self.__filter_type(sale_offer.type, type)
                           and self.__filter_price(sale_offer.price, budget)
                           and self.__filter_square(sale_offer.square, square)
                           and self.__filter_estate_class(estates, sale_offer.estate_id, estate_class)
                           and self.__filter_distance_to_metro(estates, sale_offer.estate_id, distance_to_metro)
                           and self.__filter_design(sale_offer.design, design)
                           and self.__filter_readiness(sale_offer.offer_readiness, readiness)
                           and self.__filter_irr(sale_offer.irr, irr)
                    ]

                span.set_status(Status(StatusCode.OK))
                return filtered_sale_offers
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def __filter_location(self, sale_offer_location: str, location: int) -> bool:
        if location == 1 and sale_offer_location == "ТТК":
            return True
        elif location == 2 and sale_offer_location == "МКАД":
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
            nearest_metro = self.__nearest_metro(estate.metro_stations)
            return nearest_metro.leg_distance <= distance_to_metro

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

    def __nearest_metro(self, metro_stations: list[model.MetroStation]) -> model.MetroStation:
        metro_distances = [metro.leg_distance for metro in metro_stations]
        nearest_metro_distance = min(metro_distances)
        nearest_metro_idx = metro_distances.index(nearest_metro_distance)
        nearest_metro = metro_stations[nearest_metro_idx]

        return nearest_metro
