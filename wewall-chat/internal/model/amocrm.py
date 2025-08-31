from dataclasses import dataclass
from datetime import datetime


@dataclass
class AmocrmContact:
    amocrm_contact_id: int

    name: str
    tg_chat_id: int

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                amocrm_contact_id=row.amocrm_contact_id,
                name=row.name,
                tg_chat_id=row.tg_chat_id,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in rows
        ]


@dataclass
class AmocrmLead:
    amocrm_lead_id: int

    amocrm_contact_id: int
    amocrm_pipeline_id: int

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                amocrm_lead_id=row.amocrm_lead_id,
                amocrm_contact_id=row.amocrm_contact_id,
                amocrm_pipeline_id=row.amocrm_pipeline_id,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in rows
        ]


@dataclass
class AmocrmChat:
    amocrm_chat_id: str

    amocrm_lead_id: int
    amocrm_conversation_id: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                amocrm_chat_id=row.amocrm_chat_id,
                amocrm_lead_id=row.amocrm_lead_id,
                amocrm_conversation_id=row.amocrm_conversation_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class AmocrmMessage:
    amocrm_message_id: str

    amocrm_chat_id: int
    role: str
    text: str

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                amocrm_message_id=row.amocrm_message_id,
                amocrm_chat_id=row.amocrm_chat_id,
                role=row.role,
                text=row.text,
            )
            for row in rows
        ]
