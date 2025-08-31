from datetime import datetime
from dataclasses import dataclass

@dataclass
class User:
    id: int
    tg_chat_id: int

    source_type: str
    is_bot_blocked: bool

    created_at: datetime
    updated_at: datetime
    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                tg_chat_id=row.tg_chat_id,
                source_type=row.source_type,
                is_bot_blocked=row.is_bot_blocked,
                updated_at=row.updated_at,
                created_at=row.created_at
            )
            for row in rows
        ]

class SourceType:
    POST_LINK = "post_link"
    DIRECT_LINK = "direct_link"
