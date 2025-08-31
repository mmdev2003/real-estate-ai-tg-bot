from pydantic import BaseModel


class FinishedOfficeFinanceModelBody(BaseModel):
    square: float
    price_per_meter: float
    need_repairs: int
    metro_station_name: str
    estate_category: str
    distance_to_metro: float
    nds_rate: int


class FinishedRetailFinanceModelBody(BaseModel):
    square: float
    price_per_meter: float
    m_a_p: float
    nds_rate: int
    need_repairs: int


class BuildingOfficeFinanceModelBody(BaseModel):
    project_readiness: str
    square: float
    metro_station_name: str
    distance_to_metro: float
    estate_category: str
    price_per_meter: float
    nds_rate: int
    transaction_dict: dict


class BuildingRetailFinanceModelBody(BaseModel):
    square: float
    price_per_meter: float
    transaction_dict: dict
    price_rva: float
    m_a_p: float
    nds_rate: int
    project_readiness: str
    need_repairs: int


class FinanceModelResponse(BaseModel):
    buying_property: float
    sale_property: float
    sale_tax: float
    rent_tax: float
    price_of_finishing: float
    rent_flow: float
    terminal_value: float
    sale_income: float
    rent_income: float
    added_value: float
    rent_irr: float
    sale_irr: float
