from dataclasses import dataclass
from datetime import datetime


@dataclass
class News:
    id: int

    news_summary: str
    news_name: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                news_name=row.news_name,
                news_summary=row.news_summary,
                created_at=row.created_at,
            )
            for row in rows
        ]
