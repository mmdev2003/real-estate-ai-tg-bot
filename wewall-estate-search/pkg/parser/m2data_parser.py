import re
import json
import requests

import geopandas as gpd
from shapely.geometry import Point

from bs4 import BeautifulSoup

from pkg.logger.logger import logger
from internal import model, interface


class M2DataParser(interface.IM2DataParser):
    def __init__(
            self,
            m2data_building_url: str
    ):
        self.m2data_building_url = m2data_building_url

    def parse(self) -> list[model.ParsedEstate]:
        print("Start M2DataParsing", flush=True)
        estates = []
        n = 0

        for page in range(1, self.__page_counter()):
            print(f"Parsing page {page}", flush=True)
            for estate_link in self.__all_estate_link(page):
                n += 1
                print(f"Парсим№ {n}: {estate_link}", flush=True)
                estate = self.__extract_estate_parameters(estate_link)
                if estate is None:
                    continue

                # RENT
                rent_offer_links = self.__extract_rent_offer_link(estate_link)
                rent_offers = []
                if rent_offer_links is None:
                    continue
                for rent_offer_link in rent_offer_links:
                    rent_offer = self.extract_rent_offer_parameters(rent_offer_link)
                    if rent_offer is None:
                        continue

                    rent_offer.location = self.__define_ring_by_coords(estate.coords)
                    rent_offers.append(rent_offer)
                    break
                estate.rent_offers = rent_offers
                print(f"{len(rent_offers)=}", flush=True)

                # SALE
                sale_offer_links = self.__extract_sale_offer_link(estate_link)
                sale_offers = []
                if sale_offer_links is None:
                    continue
                for sale_offer_link in sale_offer_links:
                    sale_offer = self.__extract_sale_offer_parameters(sale_offer_link)
                    if sale_offer is None:
                        continue

                    sale_offer.location = self.__define_ring_by_coords(estate.coords)
                    sale_offers.append(sale_offer)
                    break
                estate.sale_offers = sale_offers
                print(f"{len(sale_offers)=}", flush=True)
                estates.append(estate)

        return estates

    def __all_estate_link(self, page: int) -> list | None:
        try:
            html = requests.get(self.m2data_building_url + "?page=" + str(page)).text
            soup = BeautifulSoup(html, "html.parser")

            element = soup.find("search-objects")
            estate_links = []
            for estate in json.loads(element.attrs[":default-objects-list"]):
                estate_links.append(estate["url"])

            return estate_links
        except Exception as err:
            logger.error(err)

    def __extract_estate_parameters(self, estate_link: str) -> model.ParsedEstate | None:
        try:
            html = requests.get(estate_link).text
            soup = BeautifulSoup(html, "html.parser")

            estate_coords = json.loads(soup.find('object-gallery').attrs[":panorama"])["coords"]
            estate = model.ParsedEstate(estate_link, "", "", "",
                                        model.Coords(estate_coords[0], estate_coords[1]), [], [], [])

            metro_coords = self.__all_metro_coords()
            estate_data = soup.find('object-main')

            metro_stations = []
            for metro in json.loads(estate_data.attrs[":metro"])["stations"]:
                if metro is None:
                    return None

                car_distance, car_time = self.__calc_distance_by_coords(
                    metro_coords[metro["title"]].lon,
                    metro_coords[metro["title"]].lat,
                    estate.coords.lon,
                    estate.coords.lat,
                    True
                )
                leg_distance, leg_time = self.__calc_distance_by_coords(
                    metro_coords[metro["title"]].lon,
                    metro_coords[metro["title"]].lat,
                    estate.coords.lon,
                    estate.coords.lat,
                    False
                )
                metro_stations.append(
                    model.MetroStation(
                        name=metro["title"],
                        time_leg=leg_time,
                        time_car=car_time,
                        leg_distance=leg_distance,
                        car_distance=car_distance
                    )
                )
            if not metro_stations:
                return None

            estate.name = estate_data.attrs["title"]
            estate.category = self.__process_estate_category(estate_data)
            estate.address = estate_data.attrs["address"]
            estate.metro_stations = metro_stations

            return estate

        except Exception as err:
            logger.error(err)
            return None

    @staticmethod
    def __process_estate_category(estate_data: BeautifulSoup) -> str:
        category = json.loads(estate_data.attrs[":class-data"])["title"].replace(" класс", "")
        if category in ["A", "A+", "А", "А+"]:
            return "A"
        else:
            return "B"

    @staticmethod
    def __extract_rent_offer_link(estate_link: str) -> list | None:
        try:
            html = requests.get(estate_link).text
            soup = BeautifulSoup(html, "html.parser")

            rent_offers = soup.find('object-offer', class_='object-page__rent-spaces')
            rent_offer_links = []
            for offer in json.loads(rent_offers.attrs[":data"]):
                rent_offer_links.append(offer["area"]["link"])

            return rent_offer_links

        except Exception as err:
            logger.error(err)

    @staticmethod
    def __extract_sale_offer_link(estate_link: str) -> list | None:
        try:
            html = requests.get(estate_link).text
            soup = BeautifulSoup(html, "html.parser")

            sale_offers = soup.find('object-offer', class_='object-page__sale-spaces')
            sale_offer_links = []
            for offer in json.loads(sale_offers.attrs[":data"]):
                sale_offer_links.append(offer["area"]["link"])

            return sale_offer_links

        except Exception as err:
            logger.error(err)

    @staticmethod
    def extract_rent_offer_parameters(rent_offer_link: str) -> model.ParsedRentOffer | None:
        try:
            print(f"Парсим аренду: {rent_offer_link}", flush=True)
            rent_offer = model.ParsedRentOffer(rent_offer_link, "", 0, 0, 0, 0, 0, "", [], 0, "", "")

            html = requests.get(rent_offer_link).text
            soup = BeautifulSoup(html, "html.parser")

            rent_main_tag = soup.find('rent-main')

            parameters = rent_main_tag.attrs[":parameters"]

            for parameter in json.loads(parameters):
                # print(f"{parameters=}", flush=True)
                if parameter["title"] == "Арендуемая площадь":
                    rent_offer_square = parameter["values"][0]["value"]
                    if "-" in rent_offer_square:
                        return

                    rent_offer.square = float(rent_offer_square.replace(' м²', '').replace(" ", ""))

                if parameter["title"] == "Этаж":
                    if "-" in parameter["values"][0]["value"]:
                        return
                    try:
                        rent_offer.floor = int(parameter["values"][0]["value"])
                    except:
                        rent_offer.floor = 1

                if parameter["title"] == "Отделка":
                    rent_offer.design = 0 if parameter["values"][0]["value"] == "С отделкой" else 1

                if parameter["title"] == "Тип помещения":
                    rent_offer.type = 0 if parameter["values"][0]["value"] == "Офис" else 1

            for condition in json.loads(soup.find('rent-conditions').attrs[":select-data"]):
                if condition["title"] == "за м²/месяц":
                    rent_offer.price_per_month = int(condition["totalPeriodValue"][0].replace("₽", "").replace(" ", ""))

            rent_offer.image_urls = [
                meta['content']
                for meta in soup.select('div[itemprop="product"] meta[itemprop="image"]')
                if meta.get('content')
            ]
            rent_offer.name = soup.find('object-gallery').attrs["title"]

            rent_offer.description = BeautifulSoup(rent_main_tag.get("description", ""), "html.parser").get_text(separator=" ", strip=True)
            rent_offer.offer_readiness = 1
            rent_offer.readiness_date = "1Q2025"

            return rent_offer
        except Exception as err:
            logger.error(err)

    @staticmethod
    def __extract_sale_offer_parameters(sale_offer_link: str) -> model.ParsedSaleOffer | None:
        try:
            sale_offer = model.ParsedSaleOffer(sale_offer_link, "", 0, 0, 0, 0, 0, 0, "", [], 0, "", "")

            html = requests.get(sale_offer_link).text
            soup = BeautifulSoup(html, "html.parser")
            rent_main_tag = soup.find('rent-main')

            for parameter in json.loads(rent_main_tag.attrs[":parameters"]):
                if parameter["title"] == "Площадь":
                    sale_offer_square = parameter["values"][0]["value"]
                    if "-" in sale_offer_square:
                        return
                    sale_offer.square = float(sale_offer_square.replace(' м²', '').replace(" ", ""))

                if parameter["title"] == "Этаж":
                    if "-" in parameter["values"][0]["value"]:
                        return
                    if parameter["title"] == "Этаж":
                        try:
                            sale_offer.floor = int(parameter["values"][0]["value"])
                        except:
                            sale_offer.floor = 1
                if parameter["title"] == "Отделка":
                    sale_offer.design = 0 if parameter["values"][0]["value"] == "С отделкой" else 1

                if parameter["title"] == "Тип помещения":
                    sale_offer.type = 0 if parameter["values"][0]["value"] == "Офис" else 1

            for condition in json.loads(soup.find('sale-conditions').attrs[":sale-conditions"]):
                if condition["title"] == "Общая стоимость":
                    sale_offer.price = int(condition["value"].replace(" ₽", "").replace(" ", ""))
                if condition["title"] == "Стоимость за 1 м²":
                    sale_offer.price_per_meter = int(condition["value"].replace(" ₽", "").replace(" ", ""))

            sale_offer.name = soup.find('object-gallery').attrs["title"]
            sale_offer.image_urls = [
                meta['content']
                for meta in soup.select('div[itemprop="product"] meta[itemprop="image"]')
                if meta.get('content')
            ]

            sale_offer.description = BeautifulSoup(rent_main_tag.get("description", ""), "html.parser").get_text(separator=" ", strip=True)
            sale_offer.offer_readiness = 1
            sale_offer.readiness_date = "1Q2025"

            return sale_offer

        except Exception as err:
            logger.error(err)

    def __page_counter(self) -> int:
        html = requests.get(self.m2data_building_url).text
        soup = BeautifulSoup(html, "html.parser")

        pages = int(json.loads(soup.find("search-objects").attrs[":found-objects"])["total"] / 20)

        return pages

    @staticmethod
    def __calc_distance_by_coords(lon1: float, lat1: float, lon2: float, lat2: float, is_car: bool) -> tuple[int, int]:

        link = f"https://www.google.ru/maps/dir/{lat1},{lon1}/{lat2},{lon2}/@55.7629171,37.6096677,17z/data=!4m2!4m1!3e{0 if is_car else 2}?entry=ttu&g_ep=EgoyMDI1MDUwNy4wIKXMDSoASAFQAw%3D%3D"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.google.com/ ',
        }
        html = requests.get(link, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")

        script = soup.find('script').string
        pattern = r'window\.APP_INITIALIZATION_STATE=(.*?)window\.APP_FLAGS'

        distance = 0
        time = 0
        match = re.search(pattern, script)
        if match:
            try:
                raw_value = json.loads(match.group(1)[:-1])
                route_data = json.loads(raw_value[3][4].replace(")]}'", ""))[0][1][0][0]
                distance = route_data[2][0]
                time = route_data[3][0]
            except Exception as err:
                raw_value = match.group(1)[:-1]
                print(raw_value)
                logger.error(err)
                return 0, 0
        else:
            print("Пиздак")
            print("Пиздак")
            print("Пиздак")
            print("Пиздак")
            print("Пиздак")
            print("Пиздак")
            print("Пиздак")

        return distance, time

    @staticmethod
    def __all_metro_coords() -> dict[str, model.Coords]:
        metro_data = requests.get("https://api.hh.ru/metro/1").json()["lines"]

        metro_coords = {}
        for metro_line in metro_data:
            for metro_station in metro_line["stations"]:
                metro_coords[metro_station["name"]] = model.Coords(lat=metro_station["lat"],
                                                                   lon=metro_station["lng"])

        return metro_coords

    @staticmethod
    def __define_ring_by_coords(coords: model.Coords) -> str:
        ttk = gpd.read_file("pkg/moscow_ring_polygon/ttk.geojson").to_crs(epsg=4326).unary_union
        mkad = gpd.read_file("pkg/moscow_ring_polygon/mkad.geojson").to_crs(epsg=4326).unary_union
        point = Point(coords.lon, coords.lat)

        if ttk.contains(point):
            location = "ТТК"
        elif mkad.contains(point):
            location = "МКАД"
        else:
            location = "ЗАМКАД"

        return location
