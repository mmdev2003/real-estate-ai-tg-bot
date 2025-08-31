from pydantic import BaseModel


class CreateChatWithAmocrmManagerFromTgBody(BaseModel):
    amocrm_pipeline_id: int
    tg_chat_id: int
    tg_username: str
    first_name: str
    last_name: str | None


class EditLeadBody(BaseModel):
    tg_chat_id: int
    amocrm_pipeline_status_id: int
    amocrm_pipeline_id: int

class SubscribeToEventWebhookBody(BaseModel):
    webhook_url: str
    event_name: str


class SendMessageFromTgToAmocrm(BaseModel):
    tg_chat_id: int
    text: str


class SendMessageFromAmoCrmToTgBody(BaseModel):
    account_id: str

    class Message(BaseModel):
        receiver: dict
        sender: dict
        conversation: dict
        message: dict

    message: Message
