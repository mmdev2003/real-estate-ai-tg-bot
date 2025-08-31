from pydantic import BaseModel


class SendMessageToLLMtByTgBody(BaseModel):
    tg_chat_id: int
    text: str


class SendMessageToLLMByTgResponse(BaseModel):
    llm_response: str


class GetChatSummaryBody(BaseModel):
    tg_chat_id: int


class GetChatSummaryResponse(BaseModel):
    chat_summary: str


class AddMessageToChat(BaseModel):
    tg_chat_id: int
    text: str
    role: str


class DeleteAllMessageBody(BaseModel):
    tg_chat_id: int