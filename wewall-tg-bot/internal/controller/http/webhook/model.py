from pydantic import BaseModel


class CreatePostShortLinkBody(BaseModel):
    post_short_link_id: int
    name: str
    description: str
    image_name: str
    image_fid: str
    file_name: str
    file_fid: str


class SendMessageWebhookBody(BaseModel):
    tg_chat_id: int
    text: str


class DeleteStateBody(BaseModel):
    tg_chat_id: int
