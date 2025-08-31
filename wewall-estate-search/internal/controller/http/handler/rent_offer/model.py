from pydantic import BaseModel


class EstateSearchRentBody(BaseModel):
    type: int
    budget: int
    location: int
    square: float
    estate_class: int
    distance_to_metro: int
    design: int
    readiness: int
    irr: float

