from dataclasses import dataclass
from datetime import datetime


@dataclass
class Analysis:
    id: int

    analysis_summary: str
    analysis_name: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                analysis_name=row.analysis_name,
                analysis_summary=row.analysis_summary,
                created_at=row.created_at,
            )
            for row in rows
        ]
