from internal import model, interface
from .query import *


class MetroRepo(interface.IMetroRepo):
    def __init__(self, db: interface.IDB):
        self.db = db

    async def create_metro_station(
            self,
            name: str,
            price_A: int,
            price_B: int,
            rent_A: int,
            rent_B: int,
            average_cadastral_value: int,
    ) -> int:
        args = {
            'name': name,
            "price_A": price_A,
            "price_B": price_B,
            "rent_A": rent_A,
            "rent_B": rent_B,
            "average_cadastral_value": average_cadastral_value
        }
        metro_id = await self.db.insert(create_metro_station, args)
        return metro_id

    async def create_metro_distance_coeff(
            self,
            min_distance: int,
            max_distance: int,
            coeff: float,
    ) -> int:
        args = {
            "min_distance": min_distance,
            "max_distance": max_distance,
            "coeff": coeff
        }
        metro_distance_coeff_id = await self.db.insert(create_metro_distance_coeff, args)
        return metro_distance_coeff_id

    async def create_square_coeff(
            self,
            min_square: int,
            max_square: int,
            coeff: float
    ) -> int:
        args = {
            "min_square": min_square,
            "max_square": max_square,
            "coeff": coeff
        }
        square_coeff_id = await self.db.insert(create_square_coeff, args)
        return square_coeff_id

    async def metro_station_by_name(self, name: str) -> list[model.MetroStation]:
        args = {"name": name}
        rows = await self.db.select(metro_station_by_name, args)
        if rows:
            rows = model.MetroStation.serialize(rows)

        return rows

    async def all_metro_distance_coeff(self) -> list[model.MetroDistanceCoeff]:
        rows = await self.db.select(all_metro_distance_coeff, {})
        if rows:
            rows = model.MetroDistanceCoeff.serialize(rows)

        return rows

    async def all_square_coeff(self) -> list[model.SquareCoeff]:
        rows = await self.db.select(all_square_coeff, {})
        if rows:
            rows = model.SquareCoeff.serialize(rows)

        return rows
