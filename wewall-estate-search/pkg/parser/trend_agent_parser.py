import json
import re
import html
from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point

from bs4 import BeautifulSoup

from internal import model, interface
import requests


class TrendAgentParser(interface.ITrendAgentParser):
    def __init__(self):
        pass

    def parse(self) -> list[model.ParsedEstate]:
        estates = []
        try:
            all_metro = self.__all_metro_coords()
            auth_token, refresh_token = self.__trend_agent_auth()
            estates_data = self.__commerce_list(auth_token, refresh_token)

            n = 0
            for estate_data in estates_data:
                n += 1
                if n % 25 == 0:
                    auth_token, refresh_token = self.__trend_agent_auth()
                    print("Token refreshed", flush=True)

                print(f"\n\nEstate №{n}", flush=True)

                estate = self.__extract_estate_params(estate_data, all_metro, auth_token, refresh_token)
                estate_image_urls = self.__extract_images(estate_data["block_id"], auth_token)
                estate_description = self.__extract_estate_description(estate_data["block_id"], auth_token)
                sale_offers = self.__extract_sale_offer_params(estate_data["block_id"], auth_token)

                if estate is None or len(sale_offers) == 0:
                    continue

                for sale_offer in sale_offers:
                    sale_offer.location = self.__define_ring_by_coords(estate.coords)
                    sale_offer.description = estate_description
                    sale_offer.image_urls = estate_image_urls

                    print(f"Sale offer: {sale_offer}\n", flush=True)

                print(f"Estate: {estate}\n", flush=True)
                estate.sale_offers = sale_offers
                estates.append(estate)

            return estates

        except Exception as err:
            return estates

    def __extract_estate_description(self, estate_id: str, auth_token: str) -> str:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://msk.trendagent.ru",
            "Priority": "u=1, i",
            "Referer": "https://msk.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }
        url = f"https://api.trendagent.ru/v4_29/blocks/{estate_id}/unified/?ch=false&formating=true&auth_token={auth_token}&city=5a5cb42159042faa9a218d04&lang=ru"
        response = requests.get(url).json()
        raw_estate_description = response['data']['description']
        estate_description = self.__clean_html_text(raw_estate_description)

        return estate_description

    def __extract_estate_category(self, estate_id: str, auth_token: str) -> str:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://msk.trendagent.ru",
            "Priority": "u=1, i",
            "Referer": "https://msk.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }

        url = f"https://api.trendagent.ru/v4_29/blocks/{estate_id}/unified/?ch=false&formating=true&auth_token={auth_token}&city=5a5cb42159042faa9a218d04&lang=ru"
        response = requests.get(url).json()
        estate_category = response.get("data", {}).get("level_type", {}).get("name")

        if estate_category == "Элитный":
            estate_category = "A"
        else:
            estate_category = "B"

        return estate_category

    def __extract_sale_offer_params(self, estate_id: str, auth_token: str) -> list[model.ParsedSaleOffer]:
        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.7",
            "Origin": "https://msk.trendagent.ru",
            "Referer": "https://msk.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Linux",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "If-None-Match": 'W/"a7aa-3fWHsqErsegJbNfJ11aWPm4k/K4"'
        }

        all_offers_url = f"https://commerce.trendagent.ru/search/{estate_id}/premises?auth_token={auth_token}&city=5a5cb42159042faa9a218d04&lang=ru"
        all_offers = requests.get(all_offers_url, headers=header).json()
        sale_offers = []
        for offer in all_offers["result"]:
            offer_readiness, readiness_date = self.__process_deadline(offer["deadline"])

            for offer_purpose in offer["purposes"]:
                offer_type = 0 if offer_purpose["purpose"]["label"] == "Офисные" else 1

                for offer_premise in offer_purpose["premises"]:
                    image_url = f'https://selcdn.trendagent.ru/images/l/u/{offer_premise["individual_plan_image"]["file_name"]}'
                    link = f'https://msk.trendagent.ru/commerce-premise/{offer_premise["_id"]}/?open=objectpage'
                    name = offer_premise["building_name"] + " " + offer_premise["number"]
                    if offer_premise["price_m2"] < 1 or offer_premise["price"] < 1:
                        continue

                    sale_offer = model.ParsedSaleOffer(
                        link=link,
                        name=name,
                        square=offer_premise["area_total"],
                        floor=offer_premise["floors"][0],
                        design=self.__extract_design(offer_premise["finishing_type"]["label"]),
                        type=offer_type,
                        price=offer_premise["price"],
                        price_per_meter=int(offer_premise["price_m2"]),
                        location="",
                        image_urls=[image_url],
                        offer_readiness=offer_readiness,
                        readiness_date=readiness_date,
                        description=""
                    )
                    sale_offers.append(sale_offer)

        return sale_offers
    def __extract_design(self, design: str) -> int:
        if "Без отделки" in design:
            int_design = 0
        else:
            int_design = 1
        return int_design
    def __extract_estate_params(self, estate_data: dict, all_metro: dict[str, model.Coords],
                                auth_token: str, refresh_token: str) -> model.ParsedEstate | None:
        estate_prefix = estate_data["guid"]
        estate_id = estate_data["guid"]

        lat, long = self.__extract_estate_coords(estate_data["block_id"], auth_token)
        estate = model.ParsedEstate("", "", "", "",
                                    model.Coords(lat, long), [], [], [])

        estate.category = self.__extract_estate_category(estate_data["block_id"], auth_token)
        estate.link = f"https://msk.trendagent.ru/object/{estate_prefix}/#commerce"
        print(f"{estate.link=}\n\n", flush=True)

        metro_stations = []
        for metro in estate_data["subways"]:
            metro_name = re.sub(r'\s*\([^)]*\)', "", metro["name"]).strip().lower()
            if metro_name == "зеленоград-крюково":
                metro_name = "крюково"
            elif metro_name == "реутов":
                metro_name = "реутово"
            elif metro_name == "очаково":
                metro_name = "очаково i"
            coords = all_metro[metro_name]

            car_distance, car_time = self.__calc_distance_by_coords(
                coords.lon,
                coords.lat,
                long,
                lat,
                True
            )
            leg_distance, leg_time = self.__calc_distance_by_coords(
                coords.lon,
                coords.lat,
                long,
                lat,
                False
            )

            metro_stations.append(
                model.MetroStation(
                    name=metro_name,
                    time_leg=leg_time,
                    time_car=car_time,
                    leg_distance=leg_distance,
                    car_distance=car_distance
                )
            )
        if not metro_stations:
            return None

        estate.name = estate_data["block_name"]
        estate.address = estate_data["address"]
        estate.metro_stations = metro_stations

        return estate

    @staticmethod
    def __extract_estate_coords(estate_id: str, auth_token: str) -> tuple[float, float]:

        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://msk.trendagent.ru",
            "Priority": "u=1, i",
            "Referer": "https://msk.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }

        url = f"https://api.trendagent.ru/v4_29/blocks/{estate_id}/unified/?ch=false&formating=true&auth_token={auth_token}&city=5a5cb42159042faa9a218d04&lang=ru"
        response = requests.get(url, headers=header)
        response_json = response.json()
        try:
            longitude = response_json["data"]["geometry"]["coordinates"][0]
            latitude = response_json["data"]["geometry"]["coordinates"][1]

            return latitude, longitude
        except Exception as err:
            print(f"{estate_id=}, {response_json=}, {err=}")
            raise err

    @staticmethod
    def __commerce_list(auth_token: str, refresh_token: str) -> list[dict]:
        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.7",
            "Origin": "https://msk.trendagent.ru",
            "Referer": "https://msk.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Linux",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "If-None-Match": 'W/"a7aa-3fWHsqErsegJbNfJ11aWPm4k/K4"'
        }

        url = f"https://commerce.trendagent.ru/search/blocks?count=141&offset=0&sort=price&sort_order=asc&auth_token={auth_token}&city=5a5cb42159042faa9a218d04&lang=ru"
        cookies = {
            "activeCity": "5a5cb42159042faa9a218d04",
            "agency": "5f1e8ebec480e406e996d542",
            "agency_type": "1",
            "auth_token": auth_token,
            "cookies_allowed": "all",
            "defaultCity": "58c665588b6aa52311afa01b",
            "detectedCity": "true",
            "i18n": "ru",
            "refresh_token": refresh_token,
            "route": "1748072613.109.308.606748|9ab6736d071660f3cf0e092923a09e59",
            "userCanChangeTariff": "true"
        }

        response = requests.get(url, headers=header, cookies=cookies)
        response_json = response.json()

        return response_json["result"]

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
                # print(raw_value)
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
    def __trend_agent_auth() -> tuple[str, str]:
        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.7",
            "Origin": "https://sso.trendagent.ru",
            "Referer": "https://sso.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Linux",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }
        body = {
            "password": "WeWALL5804",
            "phone": "+79177206316"
        }
        url = "https://sso-api.trendagent.ru/v1/login?app_id=66d84ffc4c0168b8ccd281c7&lang=ru"

        response = requests.post(url, headers=header, json=body)
        response_json = response.json()
        auth_token = response_json['auth_token']
        refresh_token = response_json['refresh_token']

        return auth_token, refresh_token

    @staticmethod
    def __all_metro_coords() -> dict[str, model.Coords]:
        metro_data = requests.get("https://api.hh.ru/metro/1").json()["lines"]

        metro_coords = {}
        for metro_line in metro_data:
            for metro_station in metro_line["stations"]:
                metro_coords[metro_station["name"].lower().replace("ё", "е").rstrip()] = model.Coords(lat=metro_station["lat"],
                                                                           lon=metro_station["lng"])


        return metro_coords

    @staticmethod
    def __process_deadline(deadline: str) -> tuple[int, str]:
        deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))

        offer_readiness = 1 if deadline < datetime.now(deadline.tzinfo) else 0

        readiness_date = f"{(deadline.month - 1) // 3 + 1}Q{deadline.year}"

        return offer_readiness, readiness_date

    @staticmethod
    def __clean_html_text(raw_text: str) -> str:
        text = re.sub(r'<[^>]+>', '', raw_text)
        text = html.unescape(text)
        text = text.replace('\\n', '\n').strip()

        return text

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

    @staticmethod
    def __extract_images(estate_id: str, auth_token: str) -> list[str]:
        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.7",
            "Origin": "https://msk.trendagent.ru",
            "Referer": "https://msk.trendagent.ru/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Linux",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "If-None-Match": 'W/"a7aa-3fWHsqErsegJbNfJ11aWPm4k/K4"'
        }

        url = f"https://api.trendagent.ru/v4_29/blocks/{estate_id}/unified/?ch=false&formating=true&auth_token={auth_token}&city=5a5cb42159042faa9a218d04&lang=ru"

        html = requests.get(url, headers=header).text
        data = json.loads(html)['data']

        image_urls = []
        for item in data['renderer']:
            path = item['path']
            file_name = item['file_name']

            image_link = f"https://selcdn.trendagent.ru/images/{path}{file_name}"
            image_urls.append(image_link)

        return image_urls
