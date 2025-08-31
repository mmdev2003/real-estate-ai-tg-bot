from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    id: int
    chat_id: str

    role: str
    text: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                chat_id=row.chat_id,
                role=row.role,
                text=row.text,
                created_at=row.created_at,
            ) for row in rows
        ]


@dataclass
class Chat:
    id: int | None

    tg_chat_id: int | None

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                tg_chat_id=row.tg_chat_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
