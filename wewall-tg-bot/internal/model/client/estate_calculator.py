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

    def to_dict(self) -> dict:
        return {
            "buying_property": self.buying_property,
            "sale_property": self.sale_property,
            "sale_tax": self.sale_tax,
            "rent_tax": self.rent_tax,
            "price_of_finishing": self.price_of_finishing,
            "rent_flow": self.rent_flow,
            "terminal_value": self.terminal_value,
            "sale_income": self.sale_income,
            "rent_income": self.rent_income,
            "added_value": self.added_value,
            "rent_irr": self.rent_irr,
            "sale_irr": self.sale_irr,
        }