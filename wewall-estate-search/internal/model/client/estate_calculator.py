from dataclasses import dataclass

@dataclass
class FinanceModelResponse:
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