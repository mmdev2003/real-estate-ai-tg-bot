from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock

from internal import model


def create_estate_search_state(strategy: str, type: str, amount: int):
    if strategy == "Аренда" and type == "Офис":
        offers = [create_rent_offer("Офис") for _ in range(amount)]
    elif strategy == "Аренда" and type == "Ритейл":
        offers = [create_rent_offer("Ритейл") for _ in range(amount)]
    elif strategy == "Покупка" and type == "Офис":
        offers = [create_sale_offer("Офис") for _ in range(amount)]
    elif strategy == "Покупка" and type == "Ритейл":
        offers = [create_sale_offer("Ритейл") for _ in range(amount)]
    else:
        raise Exception("Invalid strategy or type")

    return model.EstateSearchState(
        id=1,
        state_id=1,
        current_offer_id=0,
        offers=offers,
        estate_search_params=estate_search_params(strategy, type),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def estate_search_state():
    return {
        "estate_type": "rent",
        "estate_strategy": "0",
        "estate_budget": "15000000",
        "estate_location": "ТТК",
        "estate_square": "80",
    }


def estate_search_params(strategy: str, type: str):
    return {
        "strategy": strategy,
        "type": type,
        "budget": 15000000,
        "location": "ТТК",
        "square": 80,
        "floor": 1,
        "irr": 18.0,
        "nds": 20,
        "m_a_p": 2000
    }


def create_rent_offer(type: str):
    rent_offer = MagicMock(spec=model.RentOffer)
    rent_offer.rent_offer_type = 0 if type == "Офис" else 1
    rent_offer.rent_offer_square = 100
    rent_offer.rent_offer_price_per_month = 150000
    rent_offer.rent_offer_design = 1
    rent_offer.estate_category = "A+"
    rent_offer.rent_offer_link = "https://example.com/sale/123"
    rent_offer.rent_offer_image_urls = ["https://example.com/img1.jpg"]

    # Metro stations
    metro_station1 = MagicMock(spec=model.MetroStation)
    metro_station1.name = "Сокольники"
    metro_station1.leg_distance = 300

    metro_station2 = MagicMock(spec=model.MetroStation)
    metro_station2.name = "Красносельская"
    metro_station2.leg_distance = 600

    rent_offer.metro_stations = [metro_station1, metro_station2]
    return rent_offer


def create_sale_offer(type: str):
    sale_offer = model.SaleOffer(
        offer_dict={
            "estate_name": "Estate name",
            "estate_category": "A+",
            "estate_address": "Космонавтов 213",
            "estate_coords": {"lat": 30.123, "lon": 29.2133},
            "metro_stations": [{
                "name": "name",
                "time_leg": 15,
                "time_car": 5,
                "leg_distance": 800,
                "car_distance": 850
            }],
            "sale_offer_link": "https://example.com/sale/123",
            "sale_offer_name": "sale_offer_name",
            "sale_offer_square": 50,
            "sale_offer_price": 5000000,
            "sale_offer_price_per_meter": 100000,
            "sale_offer_design": 0,
            "sale_offer_floor": 5,
            "sale_offer_type": 0 if type == "Офис" else 1,
            "sale_offer_image_urls": ["https://example.com/img1.jpg"]
        }
    )
    return sale_offer


def create_finance_model_response():
    mock_resp = MagicMock(spec=model.FinanceModelResponse)
    mock_resp.buying_property = 15000000
    mock_resp.sale_property = 18000000
    mock_resp.sale_tax = 500000
    mock_resp.rent_tax = 300000
    mock_resp.price_of_finishing = 2000000
    mock_resp.rent_flow = 1200000
    mock_resp.terminal_value = 20000000
    mock_resp.sale_income = 2500000
    mock_resp.rent_income = 900000
    mock_resp.added_value = 3400000
    mock_resp.rent_irr = 14.5
    mock_resp.sale_irr = 16.8
    return mock_resp
