from dataclasses import dataclass
from datetime import datetime


@dataclass
class Wewall:
    id: int
    about: str
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                about=row.about,
                created_at=row.created_at,
            )
            for row in rows
        ]
