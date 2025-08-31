from datetime import datetime
from dataclasses import dataclass


@dataclass
class PostShortLink:
    id: int

    name: str
    description: str
    image_name: str
    image_fid: str
    file_name: str
    file_fid: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                name=row.name,
                description=row.description,
                image_name=row.image_name,
                image_fid=row.image_fid,
                file_name=row.file_name,
                file_fid=row.file_fid,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
