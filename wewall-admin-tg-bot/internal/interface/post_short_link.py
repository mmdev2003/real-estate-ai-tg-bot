import io
from typing import Protocol
from abc import abstractmethod

from internal import model


class IPostShortLinkService(Protocol):
    @abstractmethod
    async def create_post_short_link(self, state_id: int, tg_chat_id: int): pass

    @abstractmethod
    async def update_name(self, tg_chat_id: int, name: str): pass

    @abstractmethod
    async def update_description(self, tg_chat_id: int, description: str): pass

    @abstractmethod
    async def update_image(self, tg_chat_id: int, image: io.BytesIO): pass

    @abstractmethod
    async def update_file(self, tg_chat_id: int, file_name: str, file: io.BytesIO): pass

    @abstractmethod
    async def generate_post_short_deep_link(self, tg_chat_id: int): pass

    @abstractmethod
    async def delete_post_short_link(self, state_id: int, tg_chat_id: int): pass


class IPostShortLinkRepo(Protocol):

    @abstractmethod
    async def create_post_short_link(self, tg_chat_id: int): pass

    @abstractmethod
    async def update_name(self, tg_chat_id: int, name: str): pass

    @abstractmethod
    async def update_description(self, tg_chat_id: int, description: str): pass

    @abstractmethod
    async def update_image(self, tg_chat_id: int, image_name: str, image_fid: str):  pass

    @abstractmethod
    async def update_file(self, tg_chat_id: int, file_name: str, file_fid: str):  pass

    @abstractmethod
    async def delete_post_short_link(self, tg_chat_id: int): pass

    @abstractmethod
    async def post_short_link_by_tg_chat_id(self, tg_chat_id: int) -> list[model.PostShortLink]: pass
