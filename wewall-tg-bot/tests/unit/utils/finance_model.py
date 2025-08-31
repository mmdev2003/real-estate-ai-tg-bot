from unittest.mock import MagicMock


def calc_resp():
    mock_resp = MagicMock()
    mock_resp.buying_property = 1000000
    mock_resp.sale_property = 1200000
    mock_resp.sale_tax = 50000
    mock_resp.rent_tax = 30000
    mock_resp.price_of_finishing = 200000
    mock_resp.rent_flow = 80000
    mock_resp.terminal_value = 1300000
    mock_resp.sale_income = 150000
    mock_resp.rent_income = 100000
    mock_resp.added_value = 250000
    mock_resp.rent_irr = 12.5
    mock_resp.sale_irr = 15.0
    return mock_resp


def calc_params_finished_office():
    calc_params = {
        "square": 80,
        "price_per_meter": 60000,
        "need_repairs": 1,
        "estate_category": "А",
        "metro_station_name": "ЦСКА",
        "distance_to_metro": 33,
        "nds_rate": 5
    }
    return calc_params


def calc_params_building_office():
    calc_params = {
        "project_readiness": "1Q2025",
        "square": 60000,
        "metro_station_name": "ЦСКА",
        "distance_to_metro": 34,
        "estate_category": "А",
        "price_per_meter": 33,
        "nds_rate": 5,
        "transaction_dict": {}
    }
    return calc_params


def calc_params_finished_retail():
    calc_params = {
        "square": 80,
        "price_per_meter": 60000,
        "need_repairs": 1,
        "nds_rate": 5,
        "m_a_p": 1500,
    }
    return calc_params


def calc_params_building_retail():
    calc_params = {
        "project_readiness": 50,
        "square": 90,
        "price_rva": 2000,
        "m_a_p": 1800,
        "price_per_meter": 70000,
        "nds_rate": 20,
        "need_repairs": True,
        "transaction_dict": {}
    }
    return calc_params